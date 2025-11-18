#!/usr/bin/env python3
"""
Script de ejemplo de uso del Obsidian RAG System

Este script demuestra cómo usar el sistema RAG completo para:
1. Indexar un vault de Obsidian
2. Hacer queries y obtener respuestas
3. Usar modo conversacional
4. Encontrar notas relacionadas
5. Obtener estadísticas

Autor: Gabriel
Fecha: 2025-01
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Añadir el directorio padre al path para que src sea un paquete
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_chain import ObsidianRAG


def print_header(text: str) -> None:
    """Imprime un header bonito."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def main():
    """Función principal del ejemplo."""

    print_header("🧠 Obsidian RAG System - Ejemplo de Uso")

    # 1. Cargar variables de entorno
    print("📝 Cargando configuración...")
    load_dotenv()

    # Verificar API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY no configurada")
        print("   Copia .env.example a .env y configura tu API key")
        sys.exit(1)

    # Obtener configuración
    vault_path = os.getenv('VAULT_PATH', './data/vault')
    collection_name = os.getenv('COLLECTION_NAME', 'obsidian_notes')
    claude_model = os.getenv('CLAUDE_MODEL', 'sonnet')
    top_k = int(os.getenv('DEFAULT_TOP_K', '5'))

    print(f"   Vault: {vault_path}")
    print(f"   Collection: {collection_name}")
    print(f"   Modelo Claude: {claude_model}")

    # 2. Inicializar sistema RAG
    print_header("🚀 Inicializando Sistema RAG")

    try:
        rag = ObsidianRAG(
            vault_path=vault_path,
            collection_name=collection_name,
            claude_model=claude_model,
            anthropic_api_key=api_key
        )
        print("✅ Sistema RAG inicializado correctamente")
    except Exception as e:
        print(f"❌ Error inicializando RAG: {e}")
        sys.exit(1)

    # 3. Indexar vault (solo si está vacío o se fuerza)
    print_header("📚 Indexando Vault")

    try:
        # Verificar si ya está indexado
        stats = rag.get_stats()
        if stats['total_notes'] == 0:
            print("📖 Vault no indexado. Indexando...")
            index_stats = rag.index_vault()
            print(f"✅ Indexación completada:")
            print(f"   Notas indexadas: {index_stats['notes_indexed']}")
            print(f"   Tiempo: {index_stats['total_time']:.2f}s")
        else:
            print(f"✅ Vault ya indexado con {stats['total_notes']} notas")
            print(f"   Para reindexar, usa: rag.index_vault(force_reindex=True)")
    except Exception as e:
        print(f"❌ Error indexando: {e}")
        sys.exit(1)

    # 4. Ejemplo 1: Query simple
    print_header("❓ Ejemplo 1: Query Simple")

    query1 = "¿Qué conceptos de algoritmos tengo en mis notas?"
    print(f"Pregunta: {query1}\n")

    try:
        result1 = rag.query(
            question=query1,
            top_k=top_k,
            deck_filter="Algoritmos"  # Opcional: filtrar por deck
        )

        print(f"Respuesta:\n{result1.answer}\n")
        print(f"{result1.format_sources()}")
        print(f"\n📊 Métricas:")
        print(f"   Documentos recuperados: {len(result1.retrieved_docs)}")
        print(f"   Tokens usados: {result1.tokens_used}")
        print(f"   Tiempo retrieval: {result1.retrieval_time:.2f}s")
        print(f"   Tiempo generación: {result1.generation_time:.2f}s")
    except Exception as e:
        print(f"❌ Error en query: {e}")

    # 5. Ejemplo 2: Query específica
    print_header("❓ Ejemplo 2: Query Específica")

    query2 = "Explícame QuickSort con ejemplos de mis notas"
    print(f"Pregunta: {query2}\n")

    try:
        result2 = rag.query(
            question=query2,
            top_k=3,
            max_context_chars=2000  # Limitar contexto
        )

        print(f"Respuesta:\n{result2.answer}\n")
        print(f"Tokens usados: {result2.tokens_used}")
    except Exception as e:
        print(f"❌ Error en query: {e}")

    # 6. Ejemplo 3: Modo conversacional
    print_header("💬 Ejemplo 3: Modo Conversacional")

    print("Iniciando conversación...\n")

    try:
        # Primera pregunta
        chat1 = rag.chat(
            "¿Qué algoritmos de ordenamiento tengo documentados?",
            top_k=3
        )
        print(f"Usuario: ¿Qué algoritmos de ordenamiento tengo documentados?")
        print(f"Claude: {chat1.answer}\n")

        # Pregunta de seguimiento (usa historial)
        chat2 = rag.chat(
            "¿Cuál es el más eficiente?",
            retrieve_context=False  # No recuperar nuevo contexto
        )
        print(f"Usuario: ¿Cuál es el más eficiente?")
        print(f"Claude: {chat2.answer}\n")

        # Limpiar historial
        rag.clear_conversation()
        print("🗑️ Historial de conversación limpiado")
    except Exception as e:
        print(f"❌ Error en chat: {e}")

    # 7. Ejemplo 4: Encontrar notas relacionadas
    print_header("🔗 Ejemplo 4: Notas Relacionadas")

    try:
        note_name = "QuickSort"  # Cambiar por una nota que exista en tu vault
        print(f"Buscando notas relacionadas a '{note_name}'...\n")

        related = rag.find_related_notes(note_name, top_k=3)

        if related:
            print(f"Notas relacionadas encontradas:")
            for i, note in enumerate(related, 1):
                file_name = note.metadata.get('file_name', 'unknown')
                deck = note.metadata.get('deck', 'general')
                print(f"  {i}. {file_name} (Deck: {deck}, Score: {note.score:.3f})")
        else:
            print(f"No se encontraron notas relacionadas (o '{note_name}' no existe)")
    except Exception as e:
        print(f"❌ Error buscando relacionadas: {e}")

    # 8. Estadísticas finales
    print_header("📊 Estadísticas del Sistema")

    try:
        final_stats = rag.get_stats()

        print(f"Vault: {final_stats['vault_path']}")
        print(f"Total de notas: {final_stats['total_notes']}")
        print(f"\nNotas por deck:")
        for deck, count in final_stats['notes_by_deck'].items():
            print(f"  - {deck}: {count} notas")
        print(f"\nNotas con flashcards: {final_stats['notes_with_flashcards']}")
        print(f"Modelo de embeddings: {final_stats['embedding_model']}")
        print(f"Dimensión: {final_stats['embedding_dimension']}")
        print(f"Modelo Claude: {final_stats['claude_model']}")

        # Exportar estadísticas
        stats_file = "rag_stats.json"
        rag.export_stats(stats_file)
        print(f"\n💾 Estadísticas exportadas a: {stats_file}")
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")

    print_header("✅ Ejemplo Completado")
    print("Para más información, consulta la documentación en docs/")


if __name__ == "__main__":
    main()
