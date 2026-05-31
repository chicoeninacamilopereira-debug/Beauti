from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn

from .coach import CoachBeauti
from .memoria import MemoriaUsuario
from .habitos import GerenciadorHabitos

app = FastAPI(title="Beauti API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ────────────────────────────────────────────────────
class MensagemRequest(BaseModel):
    usuario_id: str
    mensagem: str
    historico: list = []

class HabitoRequest(BaseModel):
    usuario_id: str
    habito_id: str
    concluido: bool

class PerfilRequest(BaseModel):
    usuario_id: str
    nome: str
    objetivos: list[str]
    horario_acordar: str
    horario_dormir: str
    nivel_energia: str  # manhã / tarde / noite

class RotinaRequest(BaseModel):
    usuario_id: str
    tipo: str  # matinal / noturna / trabalho / exercicio / estudo / alimentacao / fim_semana
    duracao_minutos: int = 60

# ── Instâncias ────────────────────────────────────────────────
coach = CoachBeauti()

# ── Rotas ─────────────────────────────────────────────────────
@app.post("/chat")
async def chat(req: MensagemRequest):
    """Conversa principal com a Beauti."""
    memoria = MemoriaUsuario(req.usuario_id)
    resposta = await coach.responder(
        mensagem=req.mensagem,
        historico=req.historico,
        contexto_usuario=memoria.get_contexto()
    )
    memoria.registrar_mensagem(req.mensagem, resposta)
    return {"resposta": resposta, "usuario": memoria.dados}


@app.post("/gerar-rotina")
async def gerar_rotina(req: RotinaRequest):
    """Gera uma rotina personalizada para o usuário."""
    memoria = MemoriaUsuario(req.usuario_id)
    rotina = await coach.gerar_rotina(
        tipo=req.tipo,
        duracao=req.duracao_minutos,
        perfil=memoria.dados
    )
    memoria.salvar_rotina(req.tipo, rotina)
    return {"rotina": rotina, "tipo": req.tipo}


@app.post("/perfil")
async def salvar_perfil(req: PerfilRequest):
    """Salva ou atualiza o perfil do usuário."""
    memoria = MemoriaUsuario(req.usuario_id)
    memoria.atualizar_perfil(req.dict())
    return {"status": "ok", "perfil": memoria.dados}


@app.get("/perfil/{usuario_id}")
async def get_perfil(usuario_id: str):
    memoria = MemoriaUsuario(usuario_id)
    return memoria.dados


@app.post("/habitos/check")
async def check_habito(req: HabitoRequest):
    """Marca um hábito como concluído ou não."""
    hab = GerenciadorHabitos(req.usuario_id)
    resultado = hab.marcar(req.habito_id, req.concluido)
    return resultado


@app.get("/habitos/{usuario_id}")
async def get_habitos(usuario_id: str):
    hab = GerenciadorHabitos(usuario_id)
    return hab.get_hoje()


@app.get("/progresso/{usuario_id}")
async def get_progresso(usuario_id: str):
    """Retorna streak, % do dia e histórico da semana."""
    memoria = MemoriaUsuario(usuario_id)
    hab = GerenciadorHabitos(usuario_id)
    return {
        "streak": memoria.dados.get("sequencia_dias", 0),
        "hoje": hab.get_progresso_hoje(),
        "semana": memoria.get_semana()
    }


@app.get("/tipos-rotina")
async def tipos_rotina():
    """Lista todos os tipos de rotina disponíveis."""
    return {
        "tipos": [
            {"id": "matinal",      "nome": "Rotina Matinal",        "emoji": "🌅", "desc": "Começar o dia com energia"},
            {"id": "noturna",      "nome": "Rotina Noturna",        "emoji": "🌙", "desc": "Preparar para um sono de qualidade"},
            {"id": "trabalho",     "nome": "Rotina de Trabalho",    "emoji": "💼", "desc": "Foco e produtividade máximos"},
            {"id": "exercicio",    "nome": "Rotina de Exercícios",  "emoji": "🏋️", "desc": "Treino personalizado para seu objetivo"},
            {"id": "estudo",       "nome": "Rotina de Estudos",     "emoji": "📚", "desc": "Aprendizado eficiente e retentivo"},
            {"id": "alimentacao",  "nome": "Rotina Alimentar",      "emoji": "🥗", "desc": "Hábitos saudáveis sem sofrimento"},
            {"id": "fim_semana",   "nome": "Rotina de Fim de Semana","emoji": "🌴","desc": "Recarregar sem perder ritmo"},
            {"id": "ansiedade",    "nome": "Rotina Anti-Ansiedade", "emoji": "🧘", "desc": "Acalmar a mente e o corpo"},
            {"id": "social",       "nome": "Rotina Social",         "emoji": "👥", "desc": "Conexões e relacionamentos"},
            {"id": "criatividade", "nome": "Rotina Criativa",       "emoji": "🎨", "desc": "Despertar o fluxo criativo"},
        ]
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
