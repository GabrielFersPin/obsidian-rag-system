#!/usr/bin/env python3
"""
Script de entry point para el sistema RAG de Obsidian.

Uso:
    python run_rag.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Asegurar que estamos en el directorio correcto
project_root = Path(__file__).parent
os.chdir(project_root)

# Cargar variables de entorno
load_dotenv()

# Importar el sistema RAG
from src.rag_chain import ObsidianRAGSystem


def print_header():
    """Imprime header del sistema."""
    print("\n" + "=" * 60)
    print("🧠 SISTEMA RAG DE OBSIDIAN")
    print("=" * 60)
    vault_path = os.getenv('OBSIDIAN_VAULT_PATH', './data/vault')
    print(f"📁 Vault: {vault_path}")
    print(f"💾 Base de datos: ./chroma_db\n")


def print_menu():
    """Imprime el menú principal."""
    print("\n" + "=" * 60)
    print("MENÚ PRINCIPAL")
    print("=" * 60)
    print("1. 📊 Ver estadísticas del sistema")
    print("2. 🔄 Indexar vault (primera vez o actualizar)")
    print("3. 🔍 Búsqueda interactiva")
    print("4. 💬 Query única")
    print("5. 🧪 Ejemplos de queries")
    print("6. 🚪 Salir")
    print("=" * 60)


def main():
    """Función principal del script."""
    
    # Obtener vault path del .env
    vault_path = os.getenv('OBSIDIAN_VAULT_PATH', './data/vault')
    
    print_header()
    
    # Verificar que el vault existe
    if not Path(vault_path).exists():
        print(f"❌ Error: Vault no encontrado en {vault_path}")
        print(f"\nAsegúrate de:")
        print(f"  1. Tener el symlink: ln -s ~/Documents/Segundo_Cerebro ./data/vault")
        print(f"  2. O actualizar OBSIDIAN_VAULT_PATH en .env")
        sys.exit(1)
    
    # Crear sistema RAG UNA SOLA VEZ (esto es clave!)
    print("🚀 Inicializando sistema RAG...")
    rag = ObsidianRAGSystem(vault_path=vault_path)
    
    # Loop del menú principal
    while True:
        print_menu()
        
        opcion = input("\nSelecciona una opción (1-6): ").strip()
        
        if opcion == '1':
            # ============================================
            # OPCIÓN 1: ESTADÍSTICAS
            # ============================================
            print("\n📊 ESTADÍSTICAS DEL SISTEMA")
            print("=" * 60)
            info = rag.get_system_info()
            
            print(f"📁 Vault: {info['vault_path']}")
            print(f"📚 Notas indexadas: {info['indexed_notes']}")
            print(f"🕐 Última indexación: {info['last_index_time'] or 'Nunca'}")
            print(f"🧮 Modelo: {info['embedding_model']}")
            print(f"📏 Dimensión: {info['embedding_dimension']}")
            
            if info['by_deck']:
                print(f"\n🎴 Distribución por asignatura:")
                for deck, count in sorted(info['by_deck'].items(), key=lambda x: -x[1]):
                    print(f"   {deck:25} {count:3} notas")
            else:
                print(f"\n⚠️  No hay notas indexadas aún")
            
            print("=" * 60)
            input("\nPresiona Enter para continuar...")
        
        elif opcion == '2':
            # ============================================
            # OPCIÓN 2: INDEXAR
            # ============================================
            print("\n🔄 INDEXAR VAULT")
            print("=" * 60)
            print("⚠️  Esto puede tardar varios minutos")
            print("    dependiendo del tamaño de tu vault\n")
            
            # Verificar si ya existe indexación
            info = rag.get_system_info()
            if info['indexed_notes'] > 0:
                print(f"📊 Hay {info['indexed_notes']} notas ya indexadas")
                print(f"🕐 Última indexación: {info['last_index_time']}\n")
            
            confirmar = input("¿Continuar con la indexación? (s/N): ").lower()
            
            if confirmar == 's':
                print("\n⏳ Iniciando indexación...\n")
                stats = rag.index_vault()
                
                if stats.get('skipped'):
                    print("\n⚠️  Indexación omitida")
                elif stats['notes_indexed'] > 0:
                    print(f"\n✅ ¡Indexación completada!")
                    print(f"   📚 Notas procesadas: {stats['notes_indexed']}")
                    print(f"   ⏱️  Tiempo total: {stats['time_taken']:.2f}s")
                    print(f"\n💡 Ahora puedes hacer búsquedas (opción 3 o 4)")
                else:
                    print("\n⚠️  No se indexaron notas")
            else:
                print("\n❌ Indexación cancelada")
            
            input("\nPresiona Enter para continuar...")
        
        elif opcion == '3':
            # ============================================
            # OPCIÓN 3: BÚSQUEDA INTERACTIVA
            # ============================================
            # Verificar primero que hay notas indexadas
            info = rag.get_system_info()
            if info['indexed_notes'] == 0:
                print("\n⚠️  No hay notas indexadas")
                print("   Primero ejecuta la opción 2 (Indexar vault)")
                input("\nPresiona Enter para continuar...")
                continue
            
            # Iniciar modo interactivo
            rag.interactive_query()
        
        elif opcion == '4':
            # ============================================
            # OPCIÓN 4: QUERY ÚNICA
            # ============================================
            # Verificar que hay notas indexadas
            info = rag.get_system_info()
            if info['indexed_notes'] == 0:
                print("\n⚠️  No hay notas indexadas")
                print("   Primero ejecuta la opción 2 (Indexar vault)")
                input("\nPresiona Enter para continuar...")
                continue
            
            print("\n💬 QUERY ÚNICA")
            print("=" * 60)
            question = input("💭 Tu pregunta: ").strip()
            
            if not question:
                print("⚠️  Pregunta vacía")
                input("\nPresiona Enter para continuar...")
                continue
            
            deck = input("🎴 Filtrar por asignatura (Enter para todas): ").strip()
            deck_filter = deck if deck else None
            
            print("\n🔍 Buscando...")
            result = rag.query(
                question=question,
                n_results=5,
                deck_filter=deck_filter
            )
            
            if 'error' in result:
                print(f"\n❌ Error: {result['error']}")
            else:
                print("\n📝 CONTEXTO RECUPERADO:")
                print("=" * 60)
                print(result['context'])
                
                if result.get('sources'):
                    print("\n📚 FUENTES:")
                    for i, source in enumerate(result['sources'], 1):
                        print(f"   {i}. [{source['deck']}] {source['file_name']}")
                        print(f"      Relevancia: {1 - source['distance']:.2%}")
                
                print("=" * 60)
            
            input("\nPresiona Enter para continuar...")
        
        elif opcion == '5':
            # ============================================
            # OPCIÓN 5: EJEMPLOS
            # ============================================
            # Verificar que hay notas indexadas
            info = rag.get_system_info()
            if info['indexed_notes'] == 0:
                print("\n⚠️  No hay notas indexadas")
                print("   Primero ejecuta la opción 2 (Indexar vault)")
                input("\nPresiona Enter para continuar...")
                continue
            
            print("\n🧪 EJEMPLOS DE QUERIES")
            print("=" * 60)
            
            ejemplos = [
                ("¿Qué es QuickSort?", None),
                ("Explica Docker y contenedores", "Nube"),
                ("¿Cómo funciona el pipeline en CPU?", "Arquitectura"),
                ("¿Qué son los embeddings?", "DataScience")
            ]
            
            for i, (pregunta, deck) in enumerate(ejemplos, 1):
                print(f"\n{i}. {pregunta}")
                if deck:
                    print(f"   (filtrado por: {deck})")
            
            print("\n0. Volver al menú")
            
            seleccion = input("\nEjecutar ejemplo (0-4): ").strip()
            
            if seleccion in ['1', '2', '3', '4']:
                idx = int(seleccion) - 1
                pregunta, deck = ejemplos[idx]
                
                print(f"\n🔍 Ejecutando: {pregunta}")
                if deck:
                    print(f"   Filtro: {deck}")
                
                print("\n⏳ Buscando...")
                result = rag.query(
                    question=pregunta,
                    n_results=3,
                    deck_filter=deck
                )
                
                if 'error' not in result:
                    print("\n📝 CONTEXTO:")
                    print("=" * 60)
                    # Mostrar solo los primeros 800 caracteres
                    context = result['context']
                    if len(context) > 800:
                        print(context[:800] + "\n...\n[Contenido truncado]")
                    else:
                        print(context)
                    
                    if result.get('sources'):
                        print("\n📚 FUENTES:")
                        for i, source in enumerate(result['sources'], 1):
                            print(f"   {i}. [{source['deck']}] {source['file_name']}")
                    
                    print("=" * 60)
                else:
                    print(f"\n❌ {result['error']}")
                
                input("\nPresiona Enter para continuar...")
            elif seleccion == '0':
                continue
            else:
                print("\n⚠️  Opción inválida")
                input("\nPresiona Enter para continuar...")
        
        elif opcion == '6':
            # ============================================
            # OPCIÓN 6: SALIR
            # ============================================
            print("\n👋 ¡Hasta luego!")
            print("=" * 60)
            break
        
        else:
            print("\n⚠️  Opción inválida. Por favor selecciona 1-6.")
            input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrumpido por usuario. ¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)