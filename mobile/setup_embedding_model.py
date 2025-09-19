#!/usr/bin/env python3
"""
Script to download and setup TensorFlow Lite embedding model for mobile app
"""

import os
import sys
import urllib.request
import tempfile
import zipfile
import shutil
from pathlib import Path

def download_universal_sentence_encoder():
    """Download Universal Sentence Encoder Lite model"""
    print("🤖 Baixando Universal Sentence Encoder Lite...")

    model_url = "https://tfhub.dev/google/universal-sentence-encoder-lite/2?tf-hub-format=compressed"

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "model.tar.gz")

        try:
            print(f"📥 Fazendo download de: {model_url}")
            urllib.request.urlretrieve(model_url, zip_path)
            print("✅ Download concluído")

            # Extract
            print("📦 Extraindo modelo...")
            shutil.unpack_archive(zip_path, temp_dir)

            # Find .tflite file
            tflite_files = list(Path(temp_dir).rglob("*.tflite"))

            if not tflite_files:
                print("❌ Arquivo .tflite não encontrado no modelo baixado")
                return False

            tflite_file = tflite_files[0]
            print(f"📁 Encontrado: {tflite_file}")

            # Copy to mobile app assets
            models_dir = Path("mobile/bible_search_app/assets/models")
            models_dir.mkdir(parents=True, exist_ok=True)

            target_path = models_dir / "universal_sentence_encoder.tflite"
            shutil.copy2(tflite_file, target_path)

            print(f"✅ Modelo copiado para: {target_path}")
            print(f"📊 Tamanho do arquivo: {target_path.stat().st_size / (1024*1024):.1f} MB")

            return True

        except Exception as e:
            print(f"❌ Erro no download: {e}")
            return False

def download_sentence_transformer_lite():
    """Download pre-converted sentence transformer model"""
    print("🤖 Baixando Sentence Transformer Lite...")

    # This is a placeholder - you'd need to find a pre-converted model
    # or convert one yourself using the conversion script below
    models = [
        {
            "name": "all-MiniLM-L6-v2.tflite",
            "url": "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/onnx/model.onnx",
            "description": "Sentence Transformer (requires conversion)"
        }
    ]

    print("⚠️  Modelos sentence-transformer requerem conversão manual.")
    print("📖 Use o script de conversão abaixo ou baixe um modelo pré-convertido.")
    return False

def create_conversion_script():
    """Create a Python script to convert sentence-transformers to TFLite"""

    script_content = '''#!/usr/bin/env python3
"""
Script para converter sentence-transformers para TensorFlow Lite
Requer: pip install sentence-transformers tensorflow
"""

import tensorflow as tf
from sentence_transformers import SentenceTransformer
import numpy as np

def convert_sentence_transformer_to_tflite(model_name="all-MiniLM-L6-v2"):
    print(f"🔄 Convertendo {model_name} para TensorFlow Lite...")

    # Carregar modelo sentence-transformers
    model = SentenceTransformer(model_name)

    # Criar uma função TensorFlow
    @tf.function
    def encode_text(text):
        # Simplificação - precisaria implementar tokenização completa
        return model.encode([text.numpy().decode()])[0]

    # Converter para TFLite
    converter = tf.lite.TFLiteConverter.from_concrete_functions([encode_text.get_concrete_function(
        tf.TensorSpec(shape=[], dtype=tf.string)
    )])

    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    # Salvar
    output_path = f"mobile/bible_search_app/assets/models/{model_name}.tflite"
    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    print(f"✅ Modelo convertido salvo em: {output_path}")
    print(f"📊 Tamanho: {len(tflite_model) / (1024*1024):.1f} MB")

if __name__ == "__main__":
    convert_sentence_transformer_to_tflite()
'''

    script_path = Path("mobile/convert_model.py")
    script_path.write_text(script_content)
    print(f"📝 Script de conversão criado: {script_path}")

def main():
    print("🚀 Setup do Modelo de Embedding para App Mobile")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("mobile/bible_search_app").exists():
        print("❌ Execute este script da pasta raiz do projeto (onde está a pasta 'mobile')")
        return

    print("\n📋 Opções disponíveis:")
    print("1. Universal Sentence Encoder Lite (Google) - Recomendado")
    print("2. Criar script de conversão para Sentence Transformers")
    print("3. Mostrar instruções manuais")

    choice = input("\n🔢 Escolha uma opção (1-3): ").strip()

    if choice == "1":
        success = download_universal_sentence_encoder()
        if success:
            print("\n🎉 Modelo configurado com sucesso!")
            print("📱 Agora você pode testar a busca semântica no app.")
        else:
            print("\n❌ Falha na configuração. Tente a opção 3 para instruções manuais.")

    elif choice == "2":
        create_conversion_script()
        print("\n📖 Para usar o script de conversão:")
        print("   1. pip install sentence-transformers tensorflow")
        print("   2. python mobile/convert_model.py")

    elif choice == "3":
        print("\n📖 Instruções Manuais:")
        print("1. Baixe um modelo TFLite de embeddings")
        print("2. Coloque-o em: mobile/bible_search_app/assets/models/")
        print("3. Renomeie para: universal_sentence_encoder.tflite")
        print("\n🔗 URLs úteis:")
        print("   - TensorFlow Hub: https://tfhub.dev/")
        print("   - HuggingFace Models: https://huggingface.co/models")

    else:
        print("❌ Opção inválida")

if __name__ == "__main__":
    main()