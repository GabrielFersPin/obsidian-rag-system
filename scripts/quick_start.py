#!/usr/bin/env python3
"""
Quick Start para Obsidian RAG System

Script simple para empezar rápidamente con el sistema RAG.

Uso:
    python scripts/quick_start.py /path/to/vault

Autor: Gabriel
Fecha: 2025-01
"""

import os
import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from rag_chain import ObsidianRAG


def main():
    """Quick start del sistema RAG."""

    print("🧠 Obsidian RAG System - Quick Start\n")

    # Verificar argumentos
    if len(sys.argv) < 2:
        print("❌ Error: Debes proporcionar el path al vault")
        print("\nUso:")
        print("    python scripts/quick_start.py /path/to/vault")
        print("\nEjemplo:")
        print("    python scripts/quick_start.py ~/Documents/ObsidianVault")
        sys.exit(1)

    vault_path = sys.argv[1]

    # Verificar API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY no configurada")
        print("\nConfigura tu API key:")
        print("    export ANTHROPIC_API_KEY=sk-ant-api03-...")
        print("\nO crea un archivo .env con:")
        print("    ANTHROPIC_API_KEY=sk-ant-api03-...")
        sys.exit(1)

    # Inicializar sistema
    print("🚀 Inicializando sistema RAG...\n")

    try:
        rag = ObsidianRAG(
            vault_path=vault_path,
            collection_name="quick_start_demo",
            claude_model="haiku"  # Usar haiku para quick start (más rápido y económico)
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    # Indexar vault
    print("📚 Indexando vault (esto puede tardar un momento)...\n")

    try:
        stats = rag.index_vault()
        print(f"✅ Indexadas {stats['notes_indexed']} notas en {stats['total_time']:.2f}s\n")
    except Exception as e:
        print(f"❌ Error indexando: {e}")
        sys.exit(1)

    # Modo interactivo
    print("💬 Modo interactivo iniciado")
    print("   Escribe tus preguntas (o 'salir' para terminar)\n")
    print("-" * 60)

    while True:
        try:
            # Obtener pregunta del usuario
            question = input("\n🙋 Tu pregunta: ").strip()

            if not question:
                continue

            if question.lower() in ['salir', 'exit', 'quit', 'q']:
                print("\n👋 ¡Hasta luego!")
                break

            # Comandos especiales
            if question.lower() == 'stats':
                stats = rag.get_stats()
                print(f"\n📊 Estadísticas:")
                print(f"   Total notas: {stats['total_notes']}")
                print(f"   Por deck: {stats['notes_by_deck']}")
                continue

            if question.lower() == 'help':
                print("\n📖 Comandos disponibles:")
                print("   stats  - Ver estadísticas del sistema")
                print("   help   - Mostrar esta ayuda")
                print("   salir  - Salir del programa")
                continue

            # Hacer query
            print("\n🤖 Pensando...", end="", flush=True)

            result = rag.query(
                question=question,
                top_k=3
            )

            print("\r" + " " * 20 + "\r", end="")  # Limpiar "Pensando..."

            # Mostrar respuesta
            print(f"🤖 Respuesta:\n")
            print(result.answer)
            print(f"\n📚 Fuentes: {len(result.retrieved_docs)} documentos consultados")
            print(f"⚡ {result.tokens_used} tokens | {result.generation_time:.2f}s")

        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

    # Cleanup
    print("\n🗑️ Limpiando...")
    try:
        rag.vector_store.delete_collection("quick_start_demo")
    except:
        pass


if __name__ == "__main__":
    # Intentar cargar .env si existe
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv no instalado, no pasa nada

    main()
