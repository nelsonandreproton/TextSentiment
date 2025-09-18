# Guia de Configuração do MongoDB para Busca Bíblica Semântica

Este guia fornece instruções passo a passo para instalar e configurar todo o software necessário para a aplicação de Busca Bíblica Semântica usando MongoDB.

## 📋 **Requisitos de Software**

Você precisa instalar 3 softwares:
1. **MongoDB Community Server** (Banco de dados)
2. **Ollama** (IA para embeddings)
3. **Dependências Python** (Tratadas automaticamente)

---

## 🗄️ **1. Instalação do MongoDB Community Server**

### **Windows:**
1. **Download do MongoDB:**
   - Vá para: https://www.mongodb.com/try/download/community
   - Selecione: `Windows x64`
   - Clique: `Download`

2. **Instalar MongoDB:**
   - Execute o arquivo `.msi` baixado
   - Escolha: instalação `Complete`
   - ✅ **Marque:** "Install MongoDB as a Service"
   - ✅ **Marque:** "Run service as Network Service user"
   - ✅ **Marque:** "Install MongoDB Compass" (GUI opcional)
   - Clique: `Install`

3. **Verificar Instalação:**
   ```bash
   # Abra o Prompt de Comando e teste:
   mongo --version
   # Ou para versões mais novas:
   mongosh --version
   ```

### **Linux (Ubuntu/Debian):**
```bash
# Importar chave pública do MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Adicionar repositório do MongoDB
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Atualizar pacotes e instalar
sudo apt update
sudo apt install -y mongodb-org

# Iniciar serviço do MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

### **macOS:**
```bash
# Usando Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

---

## 🤖 **2. Instalação do Ollama**

### **Windows:**
1. **Download do Ollama:**
   - Vá para: https://ollama.ai/download
   - Clique: `Download for Windows`

2. **Instalar Ollama:**
   - Execute o instalador baixado
   - Siga o assistente de instalação

3. **Instalar o modelo de embedding:**
   ```bash
   # Abra o Prompt de Comando e execute:
   ollama pull nomic-embed-text
   ```

### **Linux:**
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Baixar o modelo de embedding
ollama pull nomic-embed-text

# Iniciar serviço Ollama (se necessário)
ollama serve
```

### **macOS:**
```bash
# Download de https://ollama.ai/download ou use:
brew install ollama

# Baixar o modelo de embedding
ollama pull nomic-embed-text
```

---

## 🐍 **3. Configuração do Projeto Python**

### **Passo 1: Instalar Dependências**
```bash
cd TextSentiment
pip install -r config/requirements.txt
```

### **Passo 2: Configurar Variáveis de Ambiente**
```bash
# Copie o arquivo de exemplo
cp config/.env.example .env

# Edite o arquivo .env com suas configurações
```

### **Passo 3: Iniciar a Aplicação**
```bash
python main.py
```

---

## ✅ **Lista de Verificação**

Execute estes comandos para verificar se tudo está funcionando:

### **MongoDB:**
```bash
# Testar conexão MongoDB
mongosh --eval "db.runCommand('ping')"
```

### **Ollama:**
```bash
# Testar Ollama
ollama list
# Deve mostrar "nomic-embed-text" na lista
```

### **Aplicação:**
```bash
# Testar a aplicação
python main.py
# Deve iniciar o servidor na porta 8000
```

---

## 🚀 **Resumo de Início Rápido**

1. **Instalar MongoDB Community Server** → Iniciar serviço
2. **Instalar Ollama** → Baixar modelo `nomic-embed-text`
3. **Executar:** `pip install -r config/requirements.txt`
4. **Configurar:** arquivo `.env`
5. **Executar:** `python main.py`
6. **Abrir:** http://localhost:8000

---

## 🔧 **Configuração**

### **Configurações do MongoDB (opcional):**
Edite o arquivo `.env` se necessário:
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=bible_search
OLLAMA_URL=http://localhost:11434
```

### **Para MongoDB com Autenticação:**
```env
MONGODB_URL=mongodb://username:password@localhost:27017
```

---

## 🆘 **Solução de Problemas**

### **Problemas de Conexão MongoDB:**
```bash
# Verificar se MongoDB está rodando
# Windows:
net start MongoDB

# Linux/macOS:
sudo systemctl status mongod
```

### **Modelo Ollama Ausente:**
```bash
ollama pull nomic-embed-text
```

### **Conflitos de Porta:**
- MongoDB porta padrão: `27017`
- Ollama porta padrão: `11434`
- App porta padrão: `8000`

---

## 📊 **Portas Padrão Utilizadas**

| Serviço | Porta | Propósito |
|---------|-------|-----------|
| MongoDB | 27017 | Banco de dados |
| Ollama | 11434 | IA Embeddings |
| Web App | 8000 | Interface do usuário |

---

## 🎯 **Próximos Passos**

Após configuração bem-sucedida:
1. **Adicionar registros de teste** com títulos e conteúdo
2. **Testar detecção de duplicatas** adicionando o mesmo título duas vezes
3. **Testar busca semântica** com versículos bíblicos
4. **Navegar pela página de registros** para gerenciar seus dados
5. **Testar citações bíblicas** como "Lucas 2,15" ou "João 3:16"

## 💡 **Recursos da Aplicação**

### **Busca por Citações Bíblicas:**
- Digite citações como: `Lucas 2,15`, `João 3:16`, `Mateus 5.3`
- O sistema automaticamente busca o versículo e encontra textos similares
- Suporta todas as traduções portuguesas da Bíblia

### **Gerenciamento de Registros:**
- Interface completamente em português
- Adicionar, editar e excluir registros
- Busca semântica avançada
- Detecção automática de duplicatas

### **API Bíblica Integrada:**
- 16 traduções portuguesas disponíveis
- Detecção automática de citações vs. texto livre
- Mapeamento completo dos 66 livros bíblicos

A versão MongoDB é muito mais simples de configurar e oferece excelente performance para seu caso de uso!