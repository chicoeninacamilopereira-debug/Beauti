import json
from datetime import datetime
from pathlib import Path

PASTA = Path("dados/habitos")
PASTA.mkdir(parents=True, exist_ok=True)

HABITOS_PADRAO = [
    {"id": "meditacao",  "nome": "Meditação",   "emoji": "🧘", "duracao": "10 min", "periodo": "manhã",  "categoria": "mente"},
    {"id": "exercicio",  "nome": "Exercício",   "emoji": "🏃", "duracao": "30 min", "periodo": "tarde",  "categoria": "corpo"},
    {"id": "leitura",    "nome": "Leitura",     "emoji": "📚", "duracao": "20 pág", "periodo": "noite",  "categoria": "mente"},
    {"id": "agua",       "nome": "Água",        "emoji": "💧", "duracao": "2L",     "periodo": "dia",    "categoria": "saude"},
    {"id": "gratidao",   "nome": "Gratidão",    "emoji": "🙏", "duracao": "5 min",  "periodo": "manhã",  "categoria": "mente"},
    {"id": "sem_celular","nome": "Sem celular",  "emoji": "📵", "duracao": "1h antes","periodo": "noite", "categoria": "sono"},
]


class GerenciadorHabitos:
    def __init__(self, usuario_id: str):
        self.id = usuario_id
        self.arquivo = PASTA / f"{usuario_id}.json"
        self.dados = self._carregar()

    def _carregar(self) -> dict:
        if self.arquivo.exists():
            with open(self.arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"habitos": HABITOS_PADRAO, "registros": {}}

    def _salvar(self):
        with open(self.arquivo, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, ensure_ascii=False, indent=2)

    def marcar(self, habito_id: str, concluido: bool) -> dict:
        hoje = datetime.now().strftime("%Y-%m-%d")
        if hoje not in self.dados["registros"]:
            self.dados["registros"][hoje] = {}
        self.dados["registros"][hoje][habito_id] = concluido
        self._salvar()
        return {"status": "ok", "habito": habito_id, "concluido": concluido, "data": hoje}

    def get_hoje(self) -> dict:
        hoje = datetime.now().strftime("%Y-%m-%d")
        registros_hoje = self.dados["registros"].get(hoje, {})
        habitos = []
        for h in self.dados["habitos"]:
            habitos.append({
                **h,
                "concluido": registros_hoje.get(h["id"], False)
            })
        return {"habitos": habitos, "data": hoje}

    def get_progresso_hoje(self) -> dict:
        hoje = datetime.now().strftime("%Y-%m-%d")
        registros = self.dados["registros"].get(hoje, {})
        total = len(self.dados["habitos"])
        feitos = sum(1 for v in registros.values() if v)
        pct = round((feitos / total) * 100) if total else 0
        return {"feitos": feitos, "total": total, "percentual": pct}

    def adicionar_habito(self, habito: dict) -> dict:
        self.dados["habitos"].append(habito)
        self._salvar()
        return {"status": "ok", "habito": habito}
