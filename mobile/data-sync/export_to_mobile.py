#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para exportar dados do MongoDB (desktop) para SQLite (mobile)
Executa a partir do diretório raiz do projeto: python mobile/data-sync/export_to_mobile.py
"""

import asyncio
import sqlite3
import numpy as np
import os
import sys
from pathlib import Path
from datetime import datetime

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

# Adicionar o diretório raiz ao path para importar módulos do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.mongodb_database import MongoDatabase
from app.services.embedding_service import EmbeddingService

def create_mobile_database_schema(db_path: str):
    """Criar schema SQLite otimizado para mobile"""
    print(f"Criando base de dados mobile: {db_path}")

    # Garantir que o diretório existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Conectar ao SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Apagar tabelas existentes
    cursor.execute("DROP TABLE IF EXISTS records")
    cursor.execute("DROP TABLE IF EXISTS metadata")

    # Tabela principal de registros
    cursor.execute("""
        CREATE TABLE records (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding BLOB,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Tabela de metadados
    cursor.execute("""
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Índices para otimizar buscas
    cursor.execute("CREATE INDEX idx_records_title ON records(title)")
    cursor.execute("CREATE INDEX idx_records_created_at ON records(created_at)")

    conn.commit()
    conn.close()

    print("Schema SQLite criado com sucesso")

def serialize_embedding(embedding: list) -> bytes:
    """Serializar embedding para bytes"""
    try:
        if not embedding:
            return b''

        # Converter para numpy array e depois para bytes
        arr = np.array(embedding, dtype=np.float64)
        return arr.tobytes()
    except Exception as e:
        print(f"Erro ao serializar embedding: {e}")
        return b''

async def export_records_to_mobile():
    """Função principal de export"""
    db_path = "mobile/bible_search_app/assets/database/bible_records.db"

    try:
        print("Iniciando export de dados para mobile...")

        # Conectar ao MongoDB
        print("Conectando ao MongoDB...")
        database = MongoDatabase()
        await database.connect()

        # Buscar registros
        print("Buscando registros...")
        records = await database.get_all_records()

        if not records:
            print("Nenhum registro encontrado. Certifique-se de que há dados no MongoDB.")
            return False

        print(f"Encontrados {len(records)} registros")

        # Inicializar serviço de embeddings
        embedding_service = EmbeddingService()

        # Verificar e gerar embeddings se necessário
        print("Verificando embeddings...")
        records_processed = 0

        for i, record in enumerate(records, 1):
            print(f"Processando registro {i}/{len(records)}: {record.get('title', 'Sem título')[:30]}...")

            # Obter conteúdo (pode ser 'content' ou 'extracted_text')
            content = record.get('content') or record.get('extracted_text')
            if not content:
                print(f"  Registro sem conteúdo")
                continue

            # Verificar se já tem embedding
            if not record.get('embedding'):
                print(f"  Gerando embedding para: {record.get('title', 'Sem título')[:30]}...")

                try:
                    # Gerar embedding
                    embedding = await embedding_service.generate_embedding(content)
                    if embedding is not None and len(embedding) > 0:
                        # Adicionar embedding ao registro para SQLite (sem salvar no MongoDB por enquanto)
                        record['embedding'] = embedding.tolist()
                        print(f"  Embedding gerado e pronto para export")
                    else:
                        print(f"  Falha ao gerar embedding")
                        continue
                except Exception as e:
                    print(f"  Erro ao gerar embedding: {e}")
                    continue
            else:
                print(f"  Embedding já existe")

            records_processed += 1

        # Criar base de dados SQLite
        create_mobile_database_schema(db_path)

        # Conectar ao SQLite e inserir dados
        print("Inserindo dados no SQLite...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Inserir metadados
        metadata = [
            ('export_date', datetime.now().isoformat()),
            ('version', '1.0'),
            ('total_records', str(len(records))),
            ('records_with_embeddings', str(records_processed)),
        ]

        cursor.executemany("INSERT INTO metadata (key, value) VALUES (?, ?)", metadata)

        # Inserir registros
        inserted_count = 0
        for record in records:
            try:
                # Serializar embedding
                embedding_bytes = b''
                if record.get('embedding'):
                    embedding_bytes = serialize_embedding(record['embedding'])

                # Obter conteúdo (content ou extracted_text)
                content = record.get('content') or record.get('extracted_text', '')

                cursor.execute("""
                    INSERT INTO records (id, title, content, embedding, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    str(record.get('_id', record.get('id', ''))),
                    record.get('title', ''),
                    content,
                    embedding_bytes,
                    record.get('created_at', datetime.now()).isoformat() if hasattr(record.get('created_at'), 'isoformat') else str(record.get('created_at', datetime.now())),
                    record.get('updated_at', datetime.now()).isoformat() if hasattr(record.get('updated_at'), 'isoformat') else str(record.get('updated_at', datetime.now())),
                ))
                inserted_count += 1

            except Exception as e:
                print(f"Erro ao inserir registro {record.get('title', 'Unknown')}: {e}")
                continue

        conn.commit()
        conn.close()

        print(f"Export concluído com sucesso!")
        print(f"Total de registros exportados: {inserted_count}")
        print(f"Base de dados mobile criada: {db_path}")

        # Mostrar tamanho do arquivo
        if os.path.exists(db_path):
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            print(f"Tamanho do arquivo: {size_mb:.2f} MB")

        if hasattr(database, 'client') and database.client:
            database.client.close()
        return True

    except Exception as e:
        print(f"Erro durante o export: {e}")
        return False

async def test_mobile_database():
    """Testar base de dados mobile criada"""
    db_path = "mobile/bible_search_app/assets/database/bible_records.db"

    try:
        print("Testando base de dados mobile...")

        if not os.path.exists(db_path):
            print("Base de dados mobile não encontrada")
            return False

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar metadados
        cursor.execute("SELECT key, value FROM metadata")
        metadata = dict(cursor.fetchall())
        print("Metadados:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM records")
        total_records = cursor.fetchone()[0]
        print(f"Total de registros: {total_records}")

        # Mostrar amostra de registros
        cursor.execute("""
            SELECT id, title, LENGTH(embedding) as embedding_size
            FROM records
            LIMIT 3
        """)
        samples = cursor.fetchall()
        print("Amostras de registros:")
        for record_id, title, embedding_size in samples:
            print(f"  ID: {record_id[:10]}... | Título: {title[:30]}... | Embedding: {embedding_size} bytes")

        conn.close()

        print("Teste da base de dados mobile passou")
        return True

    except Exception as e:
        print(f"Erro ao testar base de dados mobile: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("EXPORT DE DADOS DESKTOP -> MOBILE")
    print("=" * 60)

    # Executar export
    success = asyncio.run(export_records_to_mobile())

    if success:
        # Testar base de dados criada
        print("\n" + "=" * 60)
        print("TESTE DA BASE DE DADOS MOBILE")
        print("=" * 60)

        test_success = asyncio.run(test_mobile_database())

        if test_success:
            print("\n" + "PROCESSO CONCLUÍDO COM SUCESSO!")
            print("A base de dados está pronta para ser usada no app mobile.")
            print(f"Localização: mobile/bible_search_app/assets/database/bible_records.db")
        else:
            print("\n" + "PROCESSO FALHOU")
            print("A base de dados foi criada mas o teste falhou.")
    else:
        print("\n" + "PROCESSO FALHOU")
        print("Não foi possível criar a base de dados mobile.")