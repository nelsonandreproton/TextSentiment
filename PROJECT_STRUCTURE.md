# Estrutura do Projeto - Busca Bíblica Semântica

## 📁 Arquivos Principais

```
TextSentiment/
├── 🐍 main.py                     # Aplicação FastAPI principal
├── 📖 README.md                   # Documentação completa
├── 📖 MONGODB_SETUP_GUIDE.md      # Guia de configuração MongoDB
├── 🔧 .env                        # Configurações de ambiente
└── 📋 .gitignore                  # Arquivos ignorados pelo Git
```

## 📁 Estrutura de Códigos

```
├── 📦 app/                        # Pacote principal da aplicação
│   ├── __init__.py
│   └── 🛠️ services/               # Serviços de lógica de negócio
│       ├── __init__.py
│       ├── 📖 bible_service.py    # API bíblica (Bolls Bible)
│       ├── 🤖 embedding_service.py # Integração Ollama
│       ├── 🗄️ mongodb_database.py # Operações MongoDB
│       └── ⚙️ services_manager.py # Auto-start de serviços
│
├── ⚙️ config/                     # Configurações
│   ├── __init__.py
│   ├── 📋 requirements.txt        # Dependências Python
│   └── ⚙️ settings.py             # Configurações da aplicação
│
└── 🎨 templates/                  # Templates HTML
    ├── 🏠 index.html              # Página principal
    ├── 📄 records.html            # Lista de registros
    └── 📋 record_detail.html      # Detalhes do registro
```

## 📁 Diretórios de Suporte

```
├── 📂 logs/                       # Logs da aplicação (vazio)
├── 📂 static/                     # Arquivos estáticos (vazio)
├── 📂 uploads/                    # Upload legacy (mantido por compatibilidade)
└── 📂 venv/                       # Ambiente virtual Python
```

## 🧹 Arquivos Removidos (Limpeza)

### ❌ Código OCR Removido
- `app/services/image_processor.py` - Processamento de imagem
- `app/services/vision_ocr.py` - OCR com visão
- `app/services/ollama_manager.py` - Antigo gerenciador (substituído)

### ❌ Setup Files Removidos
- `setup.py` - Setup script
- `setup_mongodb.py` - Setup MongoDB script
- `install_deps.py` - Instalador de dependências
- `test_mongodb.py` - Testes MongoDB
- `pyproject.toml` - Configuração projeto

### ❌ Cache Removido
- `__pycache__/` - Cache Python

## 🎯 Funcionalidades Ativas

### ✅ Core Features
- ✨ **Input Manual**: Adicionar registros com título e conteúdo
- 🔍 **Busca Semântica**: Busca por similaridade vetorial
- 📖 **Citações Bíblicas**: Detecção automática e busca de versículos
- ⏱️ **Timer Dinâmico**: Tempo de resposta em tempo real
- 🎨 **Interface Limpa**: Só título + percentagem nos resultados

### ✅ Services
- 🗄️ **MongoDB**: Armazenamento de documentos e vetores
- 🤖 **Ollama**: Geração de embeddings local
- 📖 **Bible API**: Integração com Bolls Bible
- ⚙️ **Auto-Start**: Inicialização automática de serviços

### ✅ Technical Features
- 🇧🇷 **Interface Portuguesa**: 100% traduzida
- 🛡️ **Graceful Shutdown**: Ctrl+C para parar todos os serviços
- 📊 **Performance Monitoring**: Logs detalhados e timeouts
- 🔄 **Retry Logic**: Resiliência em requests

## 📊 Estatísticas do Projeto

- **Arquivos Python**: 6 arquivos principais
- **Templates HTML**: 3 páginas
- **Dependências**: 11 packages essenciais
- **Funcionalidades OCR**: Completamente removidas
- **Linhas de Código**: ~2000 linhas (estimativa)

## 🔧 Tecnologias Utilizadas

- **Backend**: FastAPI + Python 3.8+
- **Database**: MongoDB com Motor (async)
- **AI/ML**: Ollama + nomic-embed-text
- **Frontend**: Bootstrap + Vanilla JS
- **APIs**: Bolls Bible API (português)