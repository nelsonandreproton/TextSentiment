# Sistema de Busca Bíblica Semântica

Uma aplicação web que permite adicionar registros de texto manualmente e buscar por textos similares usando citações bíblicas ou qualquer consulta de texto, utilizando embeddings vetoriais para busca semântica.

## Funcionalidades

- **Adição Manual de Registros**: Interface simples para adicionar título e conteúdo de texto
- **Busca por Citações Bíblicas**: Digite citações como "Lucas 2,15" e busque registros similares ao versículo
- **Busca Semântica**: Busque por textos similares usando qualquer consulta de texto
- **Armazenamento Vetorial**: Usa MongoDB para armazenamento eficiente e busca por similaridade
- **IA Local**: Usa Ollama para gerar embeddings (focado na privacidade)
- **Interface em Português**: Interface completamente traduzida para português brasileiro

## Pré-requisitos

### Software Necessário
1. **Python 3.8+**
2. **MongoDB**
3. **Ollama** com modelo `nomic-embed-text`

### Instruções de Instalação

#### 1. MongoDB
- **Windows**: Download do [MongoDB.com](https://www.mongodb.com/download)
- **Linux**: `sudo apt-get install mongodb`
- **macOS**: `brew install mongodb/brew/mongodb-community`

#### 2. Ollama
- Download do [Ollama.ai](https://ollama.ai/download)
- Após instalação: `ollama pull nomic-embed-text`

## Configuração

1. **Clone/Download do projeto**
   ```bash
   cd TextSentiment
   ```

2. **Instalar dependências**
   ```bash
   pip install -r config/requirements.txt
   ```

3. **Configurar variáveis de ambiente**
   ```bash
   cp config/.env.example .env
   # Edite .env com suas credenciais do MongoDB
   ```

4. **Iniciar serviços**
   ```bash
   # Iniciar MongoDB (se não estiver rodando)
   # Iniciar Ollama (se não estiver rodando)
   ollama serve
   ```

5. **Executar a aplicação**
   ```bash
   python main.py
   ```

## Uso

### Adicionar Registros
1. Navegue para `http://localhost:8000`
2. Use o formulário "Adicionar Novo Registro" para:
   - Inserir um título para o registro
   - Adicionar o conteúdo do texto
3. O sistema irá:
   - Gerar embeddings vetoriais para busca semântica
   - Verificar títulos duplicados
   - Armazenar o registro no MongoDB

### Busca por Citações Bíblicas
1. Digite uma citação bíblica na caixa de busca (ex: "Lucas 2,15", "João 3:16", "Mateus 5.3")
2. O sistema irá:
   - Detectar automaticamente que é uma citação bíblica
   - Buscar o texto do versículo usando a API bíblica
   - Encontrar registros similares ao conteúdo do versículo
3. Resultados mostram título, prévia e porcentagem de similaridade

### Busca Semântica por Texto
1. Digite qualquer texto na caixa de busca
2. O sistema retorna textos similares classificados por pontuação de similaridade
3. Resultados mostram título, prévia e porcentagem de similaridade

### Gerenciar Registros
- Visualizar todos os registros carregados
- Editar registros existentes
- Excluir registros indesejados
- Ver carimbos de data/hora de criação

## Detalhes da API Bíblica

A aplicação integra com a API Bolls Bible para citações bíblicas em português:
- **Suporte a múltiplas traduções**: ARA (Almeida Revista e Atualizada) como padrão
- **Formatos de citação suportados**: Lucas 2,15 • João 3:16 • Mateus 5.3 • 1 Coríntios 13,4
- **Mapeamento completo de livros**: 66 livros bíblicos em português
- **Detecção automática**: Sistema detecta automaticamente citações bíblicas vs. texto livre

## Endpoints da API

- `GET /` - Interface web principal
- `POST /add-record` - Adicionar novo registro manualmente
- `POST /search` - Buscar por textos similares (citações bíblicas ou texto)
- `GET /api/records` - Obter todos os registros
- `GET /api/records/{id}` - Obter detalhes de um registro específico
- `PUT /records/{id}` - Atualizar um registro
- `DELETE /records/{id}` - Excluir um registro
- `GET /health` - Verificação de integridade

## Configuração

Edite o arquivo `.env`:
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=bible_search
OLLAMA_URL=http://localhost:11434
MAX_FILE_SIZE_MB=10
UPLOAD_DIR=uploads
```

## Solução de Problemas

### Problemas Comuns

1. **Conexão com MongoDB falhou**
   - Verifique se o MongoDB está rodando
   - Verifique as credenciais do MongoDB no `.env`
   - Certifique-se de que o banco de dados existe

2. **Modelo Ollama não disponível**
   - Execute: `ollama pull nomic-embed-text`
   - Verifique o serviço Ollama: `ollama serve`

3. **API Bíblica não responde**
   - Verifique a conexão com a internet
   - API usa bolls.life - sem necessidade de chave de API

### Verificação de Integridade
Visite `http://localhost:8000/health` para verificar o status do sistema.

## Estrutura do Projeto

```
TextSentiment/
├── main.py                     # Ponto de entrada da aplicação
├── MONGODB_SETUP_GUIDE.md      # Guia de configuração do MongoDB
├── README.md                   # Este arquivo
│
├── app/                        # Pacote principal da aplicação
│   └── services/               # Serviços de lógica de negócio
│       ├── bible_service.py    # Integração com API bíblica
│       ├── embedding_service.py # Integração com Ollama
│       ├── image_processor.py  # Processamento de imagem (legado)
│       ├── mongodb_database.py # Operações do MongoDB
│       └── vision_ocr.py       # OCR com visão (legado)
│
├── config/                     # Arquivos de configuração
│   ├── settings.py             # Configurações da aplicação
│   ├── requirements.txt        # Dependências Python
│   └── .env.example           # Template de ambiente
│
├── templates/                  # Templates HTML
│   ├── index.html             # Página principal
│   ├── records.html           # Lista de registros
│   └── record_detail.html     # Detalhes do registro
│
├── uploads/                    # Imagens carregadas (legado)
└── logs/                      # Logs da aplicação
```

## Recursos de Segurança

- Validação de tipo de arquivo
- Limites de tamanho de arquivo
- Prevenção de injeção SQL usando consultas parametrizadas
- Sanitização de entrada
- Sem registro de dados sensíveis
- Processamento local (nenhum dado enviado para serviços externos)

## Notas de Performance

- Busca de similaridade vetorial otimizada com índices MongoDB
- Processamento local para privacidade
- Limites configuráveis de busca de similaridade
- Cache de embeddings para consultas repetidas

## Recursos da API Bíblica

### Traduções Suportadas
- ARA (Almeida Revista e Atualizada) - Padrão
- ARC09 (Almeida Revista e Corrigida 2009)
- ACF11 (Almeida Corrigida Fiel 2011)
- NAA (Nova Almeida Atualizada 2017)
- E mais 12 outras traduções portuguesas

### Exemplos de Citações
```
Lucas 2,15    # Formato com vírgula
João 3:16     # Formato com dois pontos
Mateus 5.3    # Formato com ponto
1 Coríntios 13,4  # Com números de capítulo
```

## Licença

Este projeto usa tecnologias de código aberto e é gratuito para uso.