import os
import json
from openai import AsyncOpenAI
from .detector import detectar_procrastinacao, detectar_tipo_rotina

# ─────────────────────────────────────────────────────────────
# SYSTEM PROMPT BASE — identidade da Beauti
# ─────────────────────────────────────────────────────────────
SYSTEM_BASE = """
Você é a Beauti, uma coach de vida pessoal calorosa, empática e altamente eficaz.

PERSONALIDADE:
- Tom caloroso, encorajador, nunca julgador
- Objetiva: respostas práticas, não filosóficas
- Usa 1-2 emojis por mensagem (nunca exagera)
- Faz UMA pergunta por vez quando precisar de informações
- Responde SEMPRE em português brasileiro

ESPECIALIDADES:
1. Rotinas matinais, noturnas, de trabalho, exercício, estudo, alimentação
2. Neurociência dos hábitos (loop hábito: gatilho → rotina → recompensa)
3. Técnicas: Atomic Habits, Pomodoro, Time Blocking, Habit Stacking
4. Psicologia comportamental: reforço positivo, identidade-baseada
5. Combate à procrastinação: regra dos 2 minutos, "comer o sapo", implementação de intenções
6. Bem-estar: sono, alimentação, exercício, mindfulness

REGRAS IMPORTANTES:
- Nunca dê mais de 3 ações por vez — o cérebro precisa de simplicidade
- Comece sempre pelo MENOR passo possível
- Quando detectar procrastinação, dê uma ação de 2 minutos imediata
- Celebre vitórias, por menores que sejam
- Use a ciência, mas explique de forma simples e acessível
- Quando o usuário pedir uma rotina, gere uma completa e estruturada em blocos
"""

# ─────────────────────────────────────────────────────────────
# PROMPTS ESPECÍFICOS POR TIPO DE ROTINA
# ─────────────────────────────────────────────────────────────
ROTINA_PROMPTS = {
    "matinal": """
Gere uma rotina matinal personalizada para {duracao} minutos.
Perfil do usuário: {perfil}

FORMATO OBRIGATÓRIO (JSON):
{{
  "titulo": "Rotina Matinal da [Nome]",
  "descricao": "...",
  "blocos": [
    {{
      "horario": "06:00",
      "nome": "Hidratação",
      "duracao": 5,
      "descricao": "Beba 500ml de água antes de qualquer coisa",
      "dica": "Deixe o copo na cabeceira na noite anterior",
      "categoria": "saude"
    }}
  ],
  "principio_chave": "...",
  "dica_consistencia": "..."
}}

Baseie a rotina nos princípios de Atomic Habits e neurociência do sono.
Inclua: acordar, hidratação, movimento, nutrição, intenção do dia.
""",

    "noturna": """
Gere uma rotina noturna para {duracao} minutos para preparar o corpo e mente para dormir.
Perfil: {perfil}

JSON com blocos incluindo: desconexão digital, relaxamento corporal, reflexão do dia,
preparação do amanhã, ritual de sono. Use ciência do sono (melatonina, temperatura corporal).
""",

    "trabalho": """
Gere uma rotina de trabalho produtivo para {duracao} minutos.
Perfil: {perfil}

Use técnica Pomodoro adaptada, time blocking e deep work.
JSON com blocos de: startup ritual, sessões de foco, pausas estratégicas, wrap-up.
""",

    "exercicio": """
Gere uma rotina de exercícios para {duracao} minutos baseada no perfil.
Perfil: {perfil}

Adapte ao nível de condicionamento, objetivo (perda de peso/ganho muscular/saúde geral).
JSON com: aquecimento, exercícios principais com séries/reps, cooldown, registro.
""",

    "estudo": """
Gere uma rotina de estudos eficiente para {duracao} minutos.
Perfil: {perfil}

Use técnicas: espaçamento, recordação ativa, intercalação, método Feynman.
JSON com: ambiente, revisão, sessões de estudo, pausas, revisão final.
""",

    "alimentacao": """
Gere uma rotina alimentar saudável para o dia inteiro.
Perfil: {perfil}

Foco em hábitos sustentáveis, não dietas restritivas.
JSON com: café da manhã, lanches, almoço, jantar com dicas práticas e anti-procrastinação alimentar.
""",

    "fim_semana": """
Gere uma rotina de fim de semana que equilibre descanso e produtividade.
Perfil: {perfil}

Inclua: recuperação do sono, lazer ativo, conexões sociais, preparação da semana.
JSON estruturado por manhã/tarde/noite de sábado e domingo.
""",

    "ansiedade": """
Gere uma rotina anti-ansiedade baseada em evidências para {duracao} minutos.
Perfil: {perfil}

Inclua: técnicas de respiração, movimento, journaling, mindfulness, gratidão.
JSON com blocos gentis e progressivos.
""",

    "social": """
Gere uma rotina para melhorar vida social e relacionamentos.
Perfil: {perfil}

Inclua: check-in com pessoas próximas, networking intencional, atividades sociais.
JSON com frequências semanais/mensais.
""",

    "criatividade": """
Gere uma rotina para despertar e nutrir a criatividade por {duracao} minutos.
Perfil: {perfil}

Inclua: morning pages, entrada em flow state, inputs criativos, experimentação livre.
JSON com blocos que removem bloqueios criativos.
"""
}


class CoachBeauti:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("MODELO", "gpt-4-turbo")

    async def responder(self, mensagem: str, historico: list, contexto_usuario: str) -> str:
        """Responde ao usuário com contexto personalizado."""
        deteccao = detectar_procrastinacao(mensagem)
        tipo_rotina = detectar_tipo_rotina(mensagem)

        system = SYSTEM_BASE
        system += f"\n\nCONTEXTO DO USUÁRIO:\n{contexto_usuario}"

        if deteccao["detectado"]:
            system += f"\n\n⚠️ PADRÃO DE PROCRASTINAÇÃO detectado: '{deteccao['padrao']}'. Responda com empatia e UMA ação de no máximo 2 minutos para fazer AGORA."

        if tipo_rotina:
            system += f"\n\nO usuário está pedindo uma rotina do tipo: {tipo_rotina}. Pergunte detalhes necessários antes de gerar (horário disponível, objetivo principal) se não tiver no contexto."

        messages = [{"role": "system", "content": system}]
        # Adiciona histórico (máx 12 mensagens)
        messages += historico[-12:]
        messages.append({"role": "user", "content": mensagem})

        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.75,
            max_tokens=600
        )
        return resp.choices[0].message.content

    async def gerar_rotina(self, tipo: str, duracao: int, perfil: dict) -> dict:
        """Gera uma rotina completa e estruturada."""
        prompt_template = ROTINA_PROMPTS.get(tipo, ROTINA_PROMPTS["matinal"])

        perfil_str = f"""
        Nome: {perfil.get('nome', 'Usuário')}
        Objetivos: {', '.join(perfil.get('objetivos', ['melhorar hábitos']))}
        Acorda às: {perfil.get('horario_acordar', '07:00')}
        Dorme às: {perfil.get('horario_dormir', '23:00')}
        Nível de energia: {perfil.get('nivel_energia', 'manhã')}
        Pontos fracos: {', '.join(perfil.get('pontos_fracos', ['procrastinação']))}
        Hábitos atuais: {', '.join(perfil.get('habitos', []))}
        """

        prompt = prompt_template.format(duracao=duracao, perfil=perfil_str)
        prompt += "\n\nRETORNE APENAS JSON VÁLIDO, sem markdown ou texto adicional."

        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Você é a Beauti, especialista em rotinas. Retorne APENAS JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        try:
            return json.loads(resp.choices[0].message.content)
        except json.JSONDecodeError:
            return {"erro": "Não foi possível gerar a rotina. Tente novamente."}
