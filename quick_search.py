#!/usr/bin/env python3
"""Script rápido para buscar en el vault."""
import sys
from src.rag_chain import ObsidianRAGSystem

def main():
    if len(sys.argv) < 2:
        print("Uso: python quick_search.py 'tu pregunta' [asignatura]")
        sys.exit(1)
    
    query = sys.argv[1]
    deck = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"\n🔍 Buscando: {query}")
    if deck:
        print(f"📚 Asignatura: {deck}")
    print("-" * 60)
    
    rag = ObsidianRAGSystem(vault_path='data/vault')
    result = rag.query(question=query, n_results=3, deck_filter=deck)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("\n📝 RESULTADOS:\n")
        print(result['context'][:500])
        if len(result['context']) > 500:
            print("\n... (truncado)")
        
        if result.get('sources'):
            print(f"\n\n📚 FUENTES:")
            for i, source in enumerate(result['sources'], 1):
                relevance = (1 - source['distance']) * 100
                print(f"   {i}. {source['file_name']} ({relevance:.1f}% relevante)")
                print(f"      Asignatura: {source['deck']}")

if __name__ == "__main__":
    main()
