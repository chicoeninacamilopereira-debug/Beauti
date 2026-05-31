# 🌸 Beauti — Coach de Vida com IA

Backend completo em Python + FastAPI com sistema de fine-tuning para criar rotinas personalizadas.

---

## 📁 Estrutura do Projeto

```
beauti/
├── app/
│   ├── main.py          # API FastAPI (rotas)
│   ├── coach.py         # Cérebro da Beauti (GPT + lógica)
│   ├── memoria.py       # Memória persistente do usuário
│   ├── habitos.py       # Gerenciador de hábitos diários
│   └── detector.py      # Detecta procrastinação e tipos de rotina
├── dados/
│   ├── dataset/
│   │   └── conversas_treino.json   # Dataset base (20 exemplos)
│   └── usuarios/        # Perfis salvos automaticamente
├── treino/
│   └── fine_tuning.py   # Script completo de treino
├── requirements.txt
└── .env.example
```

---

## 🚀 Instalação e Uso

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite o .env e coloque sua OPENAI_API_KEY
```

### 3. Iniciar o servidor
```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Testar a API
```bash
# Chat com a Beauti
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": "usuario1", "mensagem": "Quero criar uma rotina matinal"}'

# Gerar rotina completa
curl -X POST http://localhost:8000/gerar-rotina \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": "usuario1", "tipo": "matinal", "duracao_minutos": 60}'

# Ver hábitos do dia
curl http://localhost:8000/habitos/usuario1
```

---

## 🧠 Como Treinar a Beauti

O fine-tuning ensina a Beauti a responder exatamente como uma coach especializada.
Quanto mais exemplos, melhor ela fica!

### Passo a passo completo:

```bash
# PASSO 1: Gerar mais exemplos automaticamente (opcional mas recomendado)
python treino/fine_tuning.py --acao gerar_exemplos --quantidade 100

# PASSO 2: Preparar dataset (converte para formato JSONL)
python treino/fine_tuning.py --acao preparar

# PASSO 3: Enviar dataset para OpenAI
python treino/fine_tuning.py --acao enviar

# PASSO 4: Iniciar o treino
python treino/fine_tuning.py --acao treinar --modelo gpt-3.5-turbo

# PASSO 5: Monitorar progresso (leva 10-60 minutos)
python treino/fine_tuning.py --acao monitorar

# PASSO 6: Testar o modelo treinado
python treino/fine_tuning.py --acao testar --mensagem "Não consigo acordar cedo"
```

### Após o treino, atualize o .env:
```env
MODELO=ft:gpt-3.5-turbo-XXXX:beauti-coach  # ID retornado pelo treino
```

---

## 🎯 Tipos de Rotina Disponíveis

| Tipo          | Descrição                        |
|---------------|----------------------------------|
| `matinal`     | Rotina da manhã com energia      |
| `noturna`     | Preparar para dormir bem         |
| `trabalho`    | Foco e produtividade             |
| `exercicio`   | Treino personalizado             |
| `estudo`      | Aprendizado eficiente            |
| `alimentacao` | Hábitos saudáveis sem sofrimento |
| `fim_semana`  | Equilíbrio descanso/produção     |
| `ansiedade`   | Técnicas de calma                |
| `social`      | Relacionamentos e conexões       |
| `criatividade`| Despertar o fluxo criativo       |

---

## 📡 Rotas da API

| Método | Rota                    | Descrição                        |
|--------|-------------------------|----------------------------------|
| POST   | `/chat`                 | Conversa com a Beauti            |
| POST   | `/gerar-rotina`         | Gera rotina personalizada        |
| POST   | `/perfil`               | Salva perfil do usuário          |
| GET    | `/perfil/{id}`          | Retorna perfil                   |
| POST   | `/habitos/check`        | Marca hábito como feito          |
| GET    | `/habitos/{id}`         | Lista hábitos do dia             |
| GET    | `/progresso/{id}`       | Streak, % dia, semana            |
| GET    | `/tipos-rotina`         | Lista todos os tipos             |

Documentação interativa: http://localhost:8000/docs

---

## 💡 Estratégia de Treino Recomendada

```
FASE 1 — Sem treino (Hoje)
  Use GPT-4 com o System Prompt da Beauti
  Coleta feedback real dos usuários

FASE 2 — Fine-tuning básico (50-100 exemplos)
  Use GPT-3.5-turbo fine-tunado
  Beauti responde no estilo certo automaticamente
  Custo: ~$0.50 por treino, $0.003/1K tokens de uso

FASE 3 — Fine-tuning avançado (500+ exemplos)
  Beauti conhece todos os tipos de rotina
  Detecta e responde padrões de procrastinação
  Cria rotinas estruturadas automaticamente

FASE 4 — Modelo próprio (avançado)
  Use LLaMA 3 ou Mistral open source
  Fine-tune localmente (GPU necessária)
  Custo zero por requisição
```

---

## 🔧 Conectar ao Frontend

No frontend HTML da Beauti, atualize a URL do fetch:
```javascript
// Troque a URL da Anthropic API pela sua API local:
const response = await fetch("http://localhost:8000/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    usuario_id: "usuario1",
    mensagem: userMessage,
    historico: conversationHistory
  })
});
const data = await response.json();
const reply = data.resposta;
```
