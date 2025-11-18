#!/usr/bin/env python3
"""
Script para indexar un vault de Obsidian

Este script indexa todas las notas de un vault en el vector store.
Útil para la configuración inicial o para reindexar después de cambios.

Uso:
    python scripts/index_vault.py /path/to/vault [opciones]

Opciones:
    --force         Fuerza reindexación (elimina índice existente)
    --collection    Nombre de la collection (default: obsidian_notes)
    --batch-size    Tamaño de batch para embeddings (default: 32)

Ejemplos:
    # Indexar vault
    python scripts/index_vault.py ~/Documents/ObsidianVault

    # Forzar reindexación
    python scripts/index_vault.py ~/Documents/ObsidianVault --force

    # Usar collection custom
    python scripts/index_vault.py ~/vault --collection my_notes

Autor: Gabriel
Fecha: 2025-01
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from obsidian_loader import ObsidianLoader
from embeddings import EmbeddingGenerator
from vectorstore import ObsidianVectorStore


def parse_args():
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Indexa un vault de Obsidian en el vector store",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s ~/Documents/ObsidianVault
  %(prog)s ~/vault --force --collection my_notes
  %(prog)s ~/vault --batch-size 64
        """
    )

    parser.add_argument(
        'vault_path',
        help='Path al vault de Obsidian'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Fuerza reindexación (elimina índice existente)'
    )

    parser.add_argument(
        '--collection',
        default='obsidian_notes',
        help='Nombre de la collection (default: obsidian_notes)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Tamaño de batch para embeddings (default: 32)'
    )

    parser.add_argument(
        '--chroma-dir',
        default='./chroma_db',
        help='Directorio de ChromaDB (default: ./chroma_db)'
    )

    parser.add_argument(
        '--models-dir',
        default='./models',
        help='Directorio para modelos (default: ./models)'
    )

    parser.add_argument(
        '--embedding-model',
        default='sentence-transformers/all-MiniLM-L6-v2',
        help='Modelo de embeddings (default: all-MiniLM-L6-v2)'
    )

    return parser.parse_args()


def main():
    """Función principal."""

    print("=" * 60)
    print("  📚 Obsidian Vault Indexer")
    print("=" * 60)
    print()

    # Parsear argumentos
    args = parse_args()

    # Validar vault
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"❌ Error: El vault no existe: {args.vault_path}")
        sys.exit(1)

    if not vault_path.is_dir():
        print(f"❌ Error: El path no es un directorio: {args.vault_path}")
        sys.exit(1)

    # Mostrar configuración
    print("📋 Configuración:")
    print(f"   Vault: {vault_path}")
    print(f"   Collection: {args.collection}")
    print(f"   Batch size: {args.batch_size}")
    print(f"   Embedding model: {args.embedding_model}")
    print(f"   ChromaDB dir: {args.chroma_dir}")
    print(f"   Force reindex: {'Sí' if args.force else 'No'}")
    print()

    try:
        # 1. Inicializar componentes
        print("🚀 Inicializando componentes...")

        # Loader
        loader = ObsidianLoader(vault_path=str(vault_path))

        # Embedding generator
        os.environ['MODELS_CACHE_DIR'] = args.models_dir
        embedding_generator = EmbeddingGenerator(
            model_name=args.embedding_model,
            cache_folder=args.models_dir
        )

        # Vector store
        vector_store = ObsidianVectorStore(persist_directory=args.chroma_dir)

        print("✅ Componentes inicializados\n")

        # 2. Manejar collection
        if args.force:
            print(f"🗑️ Eliminando collection existente '{args.collection}'...")
            try:
                vector_store.delete_collection(args.collection)
                print("   Collection eliminada")
            except Exception as e:
                print(f"   ⚠️ No se pudo eliminar (puede que no exista): {e}")

        # Crear/obtener collection
        print(f"📝 Creando/obteniendo collection '{args.collection}'...")
        vector_store.create_collection(
            name=args.collection,
            metadata={
                'vault_path': str(vault_path),
                'indexed_at': datetime.now().isoformat(),
                'embedding_model': args.embedding_model
            }
        )
        print("✅ Collection lista\n")

        # 3. Cargar notas
        print("📖 Cargando notas del vault...")
        notes = loader.load_notes()

        if not notes:
            print("⚠️ No se encontraron notas para indexar")
            sys.exit(0)

        print(f"✅ {len(notes)} notas cargadas\n")

        # 4. Generar embeddings
        print(f"🧮 Generando embeddings (batch size: {args.batch_size})...")
        import time
        start_time = time.time()

        contents = [note['content'] for note in notes]
        embeddings = embedding_generator.embed_batch(
            contents,
            batch_size=args.batch_size,
            show_progress=True
        )

        embedding_time = time.time() - start_time
        print(f"✅ Embeddings generados en {embedding_time:.2f}s")
        print(f"   Velocidad: {len(notes) / embedding_time:.1f} notas/s\n")

        # 5. Almacenar en vector store
        print(f"💾 Almacenando en vector store...")
        start_time = time.time()

        vector_store.add_notes(
            collection_name=args.collection,
            notes=notes,
            embeddings=embeddings
        )

        store_time = time.time() - start_time
        print(f"✅ Notas almacenadas en {store_time:.2f}s\n")

        # 6. Verificar y mostrar estadísticas
        print("📊 Estadísticas de indexación:")
        stats = vector_store.get_collection_stats(args.collection)

        print(f"   Total documentos: {stats['total_documents']}")
        print(f"\n   Por deck:")
        for deck, count in stats['by_deck'].items():
            print(f"      - {deck}: {count} notas")

        print(f"\n   Notas con flashcards: {stats.get('with_flashcards', 0)}")

        print(f"\n⏱️ Tiempos:")
        print(f"   Embeddings: {embedding_time:.2f}s")
        print(f"   Almacenamiento: {store_time:.2f}s")
        print(f"   Total: {embedding_time + store_time:.2f}s")

        # 7. Guardar metadata de indexación
        metadata_file = Path(args.chroma_dir) / f"{args.collection}_index_metadata.json"
        import json

        metadata = {
            'vault_path': str(vault_path),
            'collection_name': args.collection,
            'indexed_at': datetime.now().isoformat(),
            'total_notes': len(notes),
            'embedding_model': args.embedding_model,
            'embedding_dimension': embedding_generator.dimension,
            'stats': stats,
            'times': {
                'embedding_time': embedding_time,
                'store_time': store_time,
                'total_time': embedding_time + store_time
            }
        }

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n💾 Metadata guardada en: {metadata_file}")

        print("\n" + "=" * 60)
        print("✅ Indexación completada exitosamente")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n⚠️ Indexación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante la indexación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Intentar cargar .env si existe
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    main()
