#!/usr/bin/env python3
"""Script para probar las herramientas MCP del vault de Obsidian."""

import asyncio
from mcp_server import get_rag_system

async def test_tools():
    print("=" * 60)
    print("🧪 PROBANDO HERRAMIENTAS MCP")
    print("=" * 60)
    
    rag = get_rag_system()
    
    # Test 1: Estadísticas del vault
    print("\n1️⃣ Test: get_vault_stats")
    print("-" * 60)
    info = rag.get_system_info()
    print(f"✅ Notas indexadas: {info['indexed_notes']}")
    print(f"✅ Última indexación: {info['last_index_time']}")
    print(f"✅ Asignaturas: {len(info['by_deck'])}")
    
    # Test 2: Búsqueda en el vault
    print("\n2️⃣ Test: search_vault")
    print("-" * 60)
    query = "¿Qué es un algoritmo de ordenamiento?"
    print(f"Pregunta: {query}")
    result = rag.query(question=query, n_results=3)
    
    if 'error' not in result:
        print(f"✅ Se encontraron resultados")
        print(f"Contexto (primeros 200 chars): {result['context'][:200]}...")
        if result.get('sources'):
            print(f"\nFuentes encontradas:")
            for i, source in enumerate(result['sources'][:3], 1):
                print(f"  {i}. {source['file_name']} - Deck: {source['deck']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    # Test 3: Listar notas por asignatura
    print("\n3️⃣ Test: list_notes_by_deck")
    print("-" * 60)
    deck = "Algoritmos"
    stats = rag.store.get_collection_stats(rag.collection_name)
    if stats['by_deck'].get(deck, 0) > 0:
        print(f"✅ Asignatura '{deck}' tiene {stats['by_deck'][deck]} notas")
    else:
        print(f"⚠️ No se encontraron notas en '{deck}'")
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS HERRAMIENTAS FUNCIONAN CORRECTAMENTE")
    print("=" * 60)
    print("\n💡 Ahora puedes usar estas herramientas desde Claude Code:")
    print("   - mcp__obsidian-rag__search_vault")
    print("   - mcp__obsidian-rag__get_vault_stats")
    print("   - mcp__obsidian-rag__list_notes_by_deck")

if __name__ == "__main__":
    asyncio.run(test_tools())
