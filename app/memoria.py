import json
import os
from datetime import datetime, timedelta
from pathlib import Path

PASTA = Path("dados/usuarios")
PASTA.mkdir(parents=True, exist_ok=True)


class MemoriaUsuario:
    def __init__(self, usuario_id: str):
        self.id = usuario_id.lower().strip()
        self.arquivo = PASTA / f"{self.id}.json"
        self.dados = self._carregar()

    def _carregar(self) -> dict:
        if self.arquivo.exists():
            with open(self.arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._template()

    def _template(self) -> dict:
        return {
            "id": self.id,
            "nome": "",
            "objetivos": [],
            "horario_acordar": "07:00",
            "horario_dormir": "23:00",
            "nivel_energia": "manhã",
            "habitos": [],
            "pontos_fracos": [],
            "rotinas_salvas": {},
            "sequencia_dias": 0,
            "ultimo_check_in": None,
            "historico_humor": [],
            "mensagens_total": 0,
            "criado_em": datetime.now().isoformat()
        }

    def salvar(self):
        with open(self.arquivo, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, ensure_ascii=False, indent=2)

    def atualizar_perfil(self, dados: dict):
        campos = ["nome","objetivos","horario_acordar","horario_dormir","nivel_energia"]
        for campo in campos:
            if campo in dados and dados[campo]:
                self.dados[campo] = dados[campo]
        self.salvar()

    def registrar_mensagem(self, user_msg: str, ai_msg: str):
        self.dados["mensagens_total"] = self.dados.get("mensagens_total", 0) + 1
        hoje = datetime.now().strftime("%Y-%m-%d")
        ultimo = self.dados.get("ultimo_check_in")
        if ultimo != hoje:
            ontem = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if ultimo == ontem:
                self.dados["sequencia_dias"] = self.dados.get("sequencia_dias", 0) + 1
            elif ultimo is None:
                self.dados["sequencia_dias"] = 1
            else:
                self.dados["sequencia_dias"] = 1
            self.dados["ultimo_check_in"] = hoje
        self.salvar()

    def salvar_rotina(self, tipo: str, rotina: dict):
        self.dados["rotinas_salvas"][tipo] = {
            "rotina": rotina,
            "salva_em": datetime.now().isoformat()
        }
        self.salvar()

    def get_contexto(self) -> str:
        d = self.dados
        rotinas_ativas = list(d.get("rotinas_salvas", {}).keys())
        return f"""
Nome: {d.get('nome') or 'não informado'}
Objetivos: {', '.join(d.get('objetivos', [])) or 'não definidos'}
Acorda: {d.get('horario_acordar','07:00')} | Dorme: {d.get('horario_dormir','23:00')}
Maior energia: {d.get('nivel_energia','manhã')}
Hábitos ativos: {', '.join(d.get('habitos', [])) or 'nenhum ainda'}
Pontos fracos: {', '.join(d.get('pontos_fracos', [])) or 'não mapeados'}
Rotinas criadas: {', '.join(rotinas_ativas) or 'nenhuma ainda'}
Sequência: {d.get('sequencia_dias', 0)} dias consecutivos
Total de conversas: {d.get('mensagens_total', 0)}
"""

    def get_semana(self) -> list:
        """Retorna % de conclusão dos últimos 7 dias."""
        # Placeholder — em produção viria do banco de hábitos
        return [
            {"dia": (datetime.now() - timedelta(days=i)).strftime("%a"), "pct": 0}
            for i in range(6, -1, -1)
        ]
