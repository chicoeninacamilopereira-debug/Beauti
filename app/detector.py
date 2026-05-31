"""
Detectores de padrões de linguagem para a Beauti.
"""

# ── Padrões de procrastinação ─────────────────────────────────
PADROES_PROCRASTINACAO = {
    "adiamento":    ["vou fazer depois", "amanhã eu começo", "semana que vem", "mês que vem", "quando der"],
    "desculpas":    ["não tive tempo", "estava cansado", "muito ocupado", "não consegui", "esqueci"],
    "desmotivacao": ["sem motivação", "não tenho vontade", "não consigo", "desisti", "larguei", "parei"],
    "autopiedade":  ["sou preguiçoso", "não sou disciplinado", "nunca consigo", "não fui feito para"],
    "paralisia":    ["não sei por onde começar", "muito difícil", "impossível", "complicado demais"],
}

# ── Palavras-chave para tipos de rotina ──────────────────────
PALAVRAS_ROTINA = {
    "matinal":      ["acordar", "manhã", "matinal", "levantar", "começar o dia", "rotina da manhã"],
    "noturna":      ["dormir", "noturna", "noite", "antes de dormir", "sono", "descansar"],
    "trabalho":     ["trabalho", "produtividade", "foco", "home office", "escritório", "tarefas"],
    "exercicio":    ["exercício", "treino", "academia", "correr", "atividade física", "musculação"],
    "estudo":       ["estudar", "estudo", "aprender", "concurso", "faculdade", "curso", "provas"],
    "alimentacao":  ["dieta", "alimentação", "comer", "nutrição", "emagrecer", "saudável"],
    "fim_semana":   ["fim de semana", "sábado", "domingo", "folga", "descanso"],
    "ansiedade":    ["ansiedade", "ansioso", "estresse", "acalmar", "nervoso", "preocupado"],
    "social":       ["amigos", "social", "relacionamentos", "família", "conexões", "solidão"],
    "criatividade": ["criativo", "criatividade", "arte", "escrever", "criar", "inspiração"],
}


def detectar_procrastinacao(mensagem: str) -> dict:
    msg = mensagem.lower()
    for categoria, padroes in PADROES_PROCRASTINACAO.items():
        for padrao in padroes:
            if padrao in msg:
                return {
                    "detectado": True,
                    "categoria": categoria,
                    "padrao": padrao
                }
    return {"detectado": False}


def detectar_tipo_rotina(mensagem: str) -> str | None:
    msg = mensagem.lower()
    # Verifica se a mensagem pede uma rotina
    pede_rotina = any(p in msg for p in ["rotina", "routine", "crie", "cria", "fazer", "hábito", "plano"])
    if not pede_rotina:
        return None
    for tipo, palavras in PALAVRAS_ROTINA.items():
        for palavra in palavras:
            if palavra in msg:
                return tipo
    return "matinal"  # default
