"""
treino/fine_tuning.py
─────────────────────
Script completo para treinar a Beauti via fine-tuning na OpenAI.

COMO USAR:
  1. pip install openai python-dotenv
  2. Adicione sua OPENAI_API_KEY no .env
  3. python treino/fine_tuning.py --acao preparar    # converte dataset
  4. python treino/fine_tuning.py --acao enviar       # sobe para OpenAI
  5. python treino/fine_tuning.py --acao treinar      # inicia fine-tuning
  6. python treino/fine_tuning.py --acao status       # verifica progresso
  7. python treino/fine_tuning.py --acao testar       # testa o modelo treinado
"""

import os
import json
import argparse
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_BEAUTI = "Você é a Beauti, coach de vida pessoal calorosa, empática e prática. Especialista em rotinas, hábitos e combate à procrastinação. Responda sempre em português, seja direta e dê ações concretas e pequenas."

# ── PASSO 1: Preparar dataset ─────────────────────────────────
def preparar_dataset(
    entrada: str = "dados/dataset/conversas_treino.json",
    saida: str   = "dados/dataset/beauti_treino.jsonl"
):
    """Converte JSON para JSONL (formato exigido pela OpenAI)."""
    with open(entrada, "r", encoding="utf-8") as f:
        dados = json.load(f)

    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    total = 0

    with open(saida, "w", encoding="utf-8") as f:
        for item in dados:
            msgs = item["messages"]
            # Garante que o system prompt da Beauti está em todas as entradas
            if msgs[0]["role"] != "system":
                msgs.insert(0, {"role": "system", "content": SYSTEM_BEAUTI})
            elif len(msgs[0]["content"]) < 50:
                msgs[0]["content"] = SYSTEM_BEAUTI

            linha = json.dumps({"messages": msgs}, ensure_ascii=False)
            f.write(linha + "\n")
            total += 1

    print(f"✅ Dataset preparado: {total} exemplos → {saida}")
    return saida


# ── PASSO 2: Enviar arquivo ───────────────────────────────────
def enviar_arquivo(caminho: str = "dados/dataset/beauti_treino.jsonl") -> str:
    """Faz upload do JSONL para a OpenAI."""
    print(f"📤 Enviando {caminho}...")
    with open(caminho, "rb") as f:
        resposta = client.files.create(file=f, purpose="fine-tune")
    print(f"✅ Arquivo enviado! ID: {resposta.id}")
    # Salva o ID para uso posterior
    _salvar_config("file_id", resposta.id)
    return resposta.id


# ── PASSO 3: Criar fine-tuning ────────────────────────────────
def iniciar_treino(file_id: str = None, modelo_base: str = "gpt-3.5-turbo") -> str:
    """Cria o job de fine-tuning."""
    if not file_id:
        file_id = _ler_config("file_id")
        if not file_id:
            raise ValueError("Nenhum file_id encontrado. Execute --acao enviar primeiro.")

    print(f"🚀 Iniciando fine-tuning com {modelo_base}...")
    job = client.fine_tuning.jobs.create(
        training_file=file_id,
        model=modelo_base,
        hyperparameters={
            "n_epochs": 4,               # 3-5 épocas é o ideal
            "batch_size": "auto",
            "learning_rate_multiplier": "auto"
        },
        suffix="beauti-coach"            # modelo ficará: gpt-3.5-turbo-...beauti-coach
    )
    print(f"✅ Job criado! ID: {job.id}")
    print(f"⏳ Status: {job.status}")
    _salvar_config("job_id", job.id)
    return job.id


# ── PASSO 4: Verificar status ─────────────────────────────────
def verificar_status(job_id: str = None):
    """Verifica o progresso do fine-tuning."""
    if not job_id:
        job_id = _ler_config("job_id")
        if not job_id:
            raise ValueError("Nenhum job_id encontrado. Execute --acao treinar primeiro.")

    job = client.fine_tuning.jobs.retrieve(job_id)
    print(f"\n📊 STATUS DO TREINO")
    print(f"   Job ID:  {job.id}")
    print(f"   Status:  {job.status}")
    print(f"   Modelo:  {job.fine_tuned_model or 'aguardando...'}")
    print(f"   Criado:  {job.created_at}")

    if job.fine_tuned_model:
        print(f"\n✅ TREINO CONCLUÍDO!")
        print(f"   Use o modelo: {job.fine_tuned_model}")
        _salvar_config("modelo_treinado", job.fine_tuned_model)
    elif job.status == "failed":
        print(f"\n❌ FALHA: {job.error}")
    else:
        print(f"\n⏳ Ainda treinando... Execute novamente em alguns minutos.")

    # Mostra eventos recentes
    eventos = client.fine_tuning.jobs.list_events(fine_tuning_job_id=job_id, limit=5)
    print("\n📝 Eventos recentes:")
    for e in reversed(eventos.data):
        print(f"   [{e.created_at}] {e.message}")

    return job


# ── PASSO 5: Testar modelo ────────────────────────────────────
def testar_modelo(modelo: str = None, mensagem: str = "Não consigo criar uma rotina matinal"):
    """Testa o modelo fine-tunado."""
    if not modelo:
        modelo = _ler_config("modelo_treinado")
        if not modelo:
            raise ValueError("Nenhum modelo treinado encontrado.")

    print(f"\n🧪 Testando modelo: {modelo}")
    print(f"   Pergunta: {mensagem}\n")

    resp = client.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": SYSTEM_BEAUTI},
            {"role": "user", "content": mensagem}
        ],
        temperature=0.75,
        max_tokens=300
    )
    print(f"   Beauti: {resp.choices[0].message.content}")


# ── MONITORAMENTO AUTOMÁTICO ──────────────────────────────────
def monitorar_ate_concluir(job_id: str = None, intervalo: int = 60):
    """Fica verificando o status até o treino terminar."""
    if not job_id:
        job_id = _ler_config("job_id")

    print(f"👀 Monitorando job {job_id}... (Ctrl+C para parar)")
    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)
        print(f"[{time.strftime('%H:%M:%S')}] Status: {job.status}")
        if job.status in ["succeeded", "failed", "cancelled"]:
            verificar_status(job_id)
            break
        time.sleep(intervalo)


# ── EXPANDIR DATASET ──────────────────────────────────────────
def gerar_mais_exemplos(quantidade: int = 50):
    """
    Usa GPT-4 para gerar mais exemplos de treino automaticamente.
    Quanto mais exemplos, melhor o fine-tuning!
    """
    tipos_rotina = [
        "matinal", "noturna", "trabalho", "exercício", "estudo",
        "alimentação", "fim de semana", "ansiedade", "criatividade", "social"
    ]
    situacoes = [
        "procrastinação", "falta de motivação", "cansaço crônico",
        "distração com celular", "insônia", "dificuldade de foco",
        "sedentarismo", "alimentação irregular", "estresse no trabalho",
        "dificuldade de acordar cedo"
    ]

    print(f"🤖 Gerando {quantidade} exemplos com GPT-4...")
    novos_exemplos = []

    for i in range(quantidade):
        tipo = tipos_rotina[i % len(tipos_rotina)]
        situacao = situacoes[i % len(situacoes)]

        prompt = f"""
Crie 1 exemplo de conversa treinamento para uma coach de vida chamada Beauti.
Tema: {tipo} | Situação do usuário: {situacao}

Retorne APENAS este JSON:
{{
  "messages": [
    {{"role": "system", "content": "Você é a Beauti, coach de vida pessoal..."}},
    {{"role": "user", "content": "mensagem do usuário sobre {situacao}"}},
    {{"role": "assistant", "content": "resposta da Beauti: calorosa, prática, 2-3 parágrafos, 1 emoji, termina com pergunta ou ação concreta"}}
  ]
}}
"""
        try:
            resp = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            exemplo = json.loads(resp.choices[0].message.content)
            novos_exemplos.append(exemplo)
            print(f"  [{i+1}/{quantidade}] ✅ {tipo} / {situacao}")
        except Exception as e:
            print(f"  [{i+1}/{quantidade}] ❌ Erro: {e}")

    # Salva os novos exemplos
    saida = "dados/dataset/exemplos_gerados.json"
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(novos_exemplos, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(novos_exemplos)} exemplos salvos em {saida}")
    print("Agora execute: python treino/fine_tuning.py --acao preparar")


# ── Helpers ───────────────────────────────────────────────────
def _salvar_config(chave: str, valor: str):
    config_path = Path("treino/config.json")
    config = {}
    if config_path.exists():
        config = json.loads(config_path.read_text())
    config[chave] = valor
    config_path.write_text(json.dumps(config, indent=2))

def _ler_config(chave: str) -> str | None:
    config_path = Path("treino/config.json")
    if not config_path.exists():
        return None
    config = json.loads(config_path.read_text())
    return config.get(chave)


# ── CLI ───────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Treinar a Beauti")
    parser.add_argument("--acao", choices=[
        "preparar", "enviar", "treinar", "status",
        "testar", "monitorar", "gerar_exemplos"
    ], required=True)
    parser.add_argument("--mensagem", default="Como criar uma rotina matinal?")
    parser.add_argument("--quantidade", type=int, default=50)
    parser.add_argument("--modelo", default="gpt-3.5-turbo")
    args = parser.parse_args()

    if args.acao == "preparar":
        preparar_dataset()
    elif args.acao == "enviar":
        enviar_arquivo()
    elif args.acao == "treinar":
        iniciar_treino(modelo_base=args.modelo)
    elif args.acao == "status":
        verificar_status()
    elif args.acao == "testar":
        testar_modelo(mensagem=args.mensagem)
    elif args.acao == "monitorar":
        monitorar_ate_concluir()
    elif args.acao == "gerar_exemplos":
        gerar_mais_exemplos(args.quantidade)
