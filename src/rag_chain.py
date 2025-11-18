"""
Pipeline RAG completo para Obsidian

Este módulo integra todos los componentes.

Autor: Gabriel
Fecha: 2025-01
"""

import os
import sys
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import json
import logging
from tqdm import tqdm

# Fix imports para ejecutar directamente o como módulo
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.obsidian_loader import ObsidianLoader
    from src.embeddings import EmbeddingGenerator
    from src.vectorstore import ObsidianVectorStore, format_search_results
else:
    from .obsidian_loader import ObsidianLoader
    from .embeddings import EmbeddingGenerator
    from .vectorstore import ObsidianVectorStore, format_search_results

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ObsidianRAGSystem:
    """Sistema RAG completo para notas de Obsidian."""
    
    def __init__(
        self,
        vault_path: str,
        collection_name: str = "obsidian_notes",
        persist_dir: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """Inicializa el sistema RAG."""
        self.vault_path = Path(vault_path)
        self.collection_name = collection_name
        self.persist_dir = Path(persist_dir)
        
        logger.info("🚀 Inicializando Obsidian RAG System")
        logger.info(f"📁 Vault: {self.vault_path}")
        logger.info(f"💾 Persist dir: {self.persist_dir}")
        
        # Inicializar componentes
        logger.info("📦 Inicializando componentes...")
        
        self.loader = ObsidianLoader(str(self.vault_path))
        logger.info("   ✅ Loader inicializado")
        
        self.embedder = EmbeddingGenerator(
            model_name=embedding_model,
            cache_folder=str(self.persist_dir / "models")
        )
        logger.info("   ✅ Embedder inicializado")
        
        self.store = ObsidianVectorStore(
            persist_directory=str(self.persist_dir)
        )
        logger.info("   ✅ Vector store inicializado")
        
        # Metadata
        self.indexed_notes = 0
        self.last_index_time = None
        self._load_metadata()
        
        logger.info("✅ Sistema RAG listo\n")
    
    def _load_metadata(self):
        """Carga metadata de indexación previa."""
        metadata_file = self.persist_dir / "rag_metadata.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    self.indexed_notes = metadata.get('indexed_notes', 0)
                    self.last_index_time = metadata.get('last_index_time')
                    if self.indexed_notes > 0:
                        logger.info(f"📊 Metadata cargada: {self.indexed_notes} notas indexadas")
            except Exception as e:
                logger.warning(f"⚠️ Error cargando metadata: {e}")
    
    def _save_metadata(self):
        """Guarda metadata de indexación."""
        metadata_file = self.persist_dir / "rag_metadata.json"
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            'indexed_notes': self.indexed_notes,
            'last_index_time': self.last_index_time,
            'vault_path': str(self.vault_path),
            'collection_name': self.collection_name
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def index_vault(self, force_reindex: bool = False, batch_size: int = 32) -> Dict:
        """Indexa todas las notas del vault."""
        logger.info("=" * 60)
        logger.info("🔄 INICIANDO INDEXACIÓN DEL VAULT")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # 1. CARGAR NOTAS
        logger.info("\n📚 Paso 1/5: Cargando notas del vault...")
        notas = self.loader.load_notes()
        
        if not notas:
            logger.warning("⚠️ No se encontraron notas para indexar")
            return {'notes_indexed': 0, 'time_taken': 0}
        
        logger.info(f"   ✅ {len(notas)} notas cargadas")
        
        # 1.5 FILTRAR NOTAS VÁLIDAS
        logger.info("\n🔍 Paso 2/5: Filtrando notas válidas...")
        notas_validas = []
        notas_descartadas = 0
        
        for nota in notas:
            content = nota.get('content', '').strip()
            
            if not content or len(content) < 10:
                logger.warning(f"   ⚠️ Descartando: {nota.get('file_name', 'unknown')}")
                notas_descartadas += 1
                continue
            
            notas_validas.append(nota)
        
        logger.info(f"   ✅ {len(notas_validas)} notas válidas")
        if notas_descartadas > 0:
            logger.warning(f"   ⚠️ {notas_descartadas} notas descartadas")
        
        if not notas_validas:
            logger.error("❌ No hay notas válidas para indexar")
            return {'notes_indexed': 0, 'time_taken': 0}
        
        notas = notas_validas
        
        # 2. VERIFICAR COLLECTION EXISTENTE
        existing_collections = self.store.list_collections()
        
        if self.collection_name in existing_collections and not force_reindex:
            logger.info(f"\n⚠️ Collection '{self.collection_name}' ya existe")
            stats = self.store.get_collection_stats(self.collection_name)
            existing_count = stats['total_documents']
            
            if existing_count > 0:
                logger.info(f"   Documentos existentes: {existing_count}")
                response = input("\n¿Reindexar? (s/N): ").lower()
                if response != 's':
                    logger.info("❌ Indexación cancelada")
                    return {'notes_indexed': 0, 'skipped': True}
                
                logger.info("🗑️ Eliminando collection existente...")
                self.store.delete_collection(self.collection_name)
        
        # 3. CREAR COLLECTION
        logger.info(f"\n📝 Paso 3/5: Creando collection '{self.collection_name}'...")
        self.store.create_collection(
            self.collection_name,
            metadata={
                'description': 'Notas de Obsidian para RAG',
                'created_at': datetime.now().isoformat()
            }
        )
        logger.info("   ✅ Collection creada")
        
        # 4. GENERAR EMBEDDINGS
        logger.info(f"\n🧮 Paso 4/5: Generando embeddings...")
        logger.info(f"   Modelo: {self.embedder.model_name}")
        logger.info(f"   Dimensiones: {self.embedder.dimension}")
        
        contents = [nota['content'] for nota in notas]
        embeddings = self.embedder.embed_batch(contents, batch_size=batch_size, show_progress=True)
        
        logger.info("   ✅ Embeddings generados")
        
        # 5. GUARDAR EN VECTOR STORE
        logger.info(f"\n💾 Paso 5/5: Guardando en vector database...")
        self.store.add_notes(
            collection_name=self.collection_name,
            notes=notas,
            embeddings=embeddings
        )
        logger.info("   ✅ Notas guardadas")
        
        # 6. ACTUALIZAR METADATA
        self.indexed_notes = len(notas)
        self.last_index_time = datetime.now().isoformat()
        self._save_metadata()
        
        # 7. ESTADÍSTICAS
        end_time = datetime.now()
        time_taken = (end_time - start_time).total_seconds()
        stats = self.store.get_collection_stats(self.collection_name)
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ INDEXACIÓN COMPLETADA")
        logger.info("=" * 60)
        logger.info(f"📊 Estadísticas:")
        logger.info(f"   Total notas: {self.indexed_notes}")
        logger.info(f"   Por deck: {stats['by_deck']}")
        logger.info(f"   Tiempo total: {time_taken:.2f}s")
        logger.info(f"   Promedio: {time_taken/len(notas):.3f}s por nota")
        logger.info("=" * 60 + "\n")
        
        return {
            'notes_indexed': self.indexed_notes,
            'time_taken': time_taken,
            'by_deck': stats['by_deck']
        }
    
    def query(
        self,
        question: str,
        n_results: int = 5,
        deck_filter: Optional[str] = None,
        return_sources: bool = True
    ) -> Dict:
        """Realiza una consulta RAG."""
        logger.info(f"🔍 Query: '{question}'")
        if deck_filter:
            logger.info(f"   Filtro: deck='{deck_filter}'")
        
        # Verificar que hay notas indexadas
        try:
            collection = self.store.get_collection(self.collection_name)
            if collection.count() == 0:
                return {
                    'error': 'No hay notas indexadas. Ejecuta index_vault() primero.',
                    'context': '',
                    'sources': []
                }
        except:
            return {
                'error': 'Collection no existe. Ejecuta index_vault() primero.',
                'context': '',
                'sources': []
            }
        
        # Generar embedding
        query_embedding = self.embedder.embed_text(question)
        
        # Buscar
        where_filter = {'deck': deck_filter} if deck_filter else None
        results = self.store.search(
            collection_name=self.collection_name,
            query_embedding=query_embedding,
            n_results=n_results,
            where=where_filter
        )
        
        # Formatear
        formatted_results = format_search_results(results)
        
        if not formatted_results:
            return {'context': '', 'sources': [], 'question': question}
        
        logger.info(f"✅ {len(formatted_results)} documentos encontrados\n")
        
        # Construir contexto
        context = self._build_context(formatted_results)
        
        response = {
            'question': question,
            'context': context,
            'n_results': len(formatted_results),
            'deck_filter': deck_filter
        }
        
        if return_sources:
            response['sources'] = [
                {
                    'file_name': res['metadata']['file_name'],
                    'deck': res['metadata']['deck'],
                    'distance': res['distance'],
                    'snippet': res['document'][:200] + '...'
                }
                for res in formatted_results
            ]
        
        return response
    
    def _build_context(self, results: List[Dict]) -> str:
        """Construye contexto para el LLM."""
        context_parts = []
        
        for i, result in enumerate(results, 1):
            context_parts.append(f"""
## Fuente {i}: {result['metadata']['file_name']}
**Asignatura**: {result['metadata']['deck']}
**Relevancia**: {1 - result['distance']:.2f}

{result['document']}

---
""")
        
        return "\n".join(context_parts)
    
    def interactive_query(self):
        """Modo interactivo de consulta."""
        logger.info("\n" + "=" * 60)
        logger.info("🤖 MODO INTERACTIVO RAG")
        logger.info("=" * 60)
        logger.info("Comandos:")
        logger.info("  - Escribe tu pregunta")
        logger.info("  - 'deck:Algoritmos pregunta' para filtrar")
        logger.info("  - 'stats' para estadísticas")
        logger.info("  - 'salir' para terminar")
        logger.info("=" * 60 + "\n")
        
        while True:
            try:
                user_input = input("💭 Tu pregunta: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    logger.info("\n👋 ¡Hasta luego!")
                    break
                
                if user_input.lower() == 'stats':
                    self._print_stats()
                    continue
                
                # Parsear deck filter
                deck_filter = None
                question = user_input
                
                if user_input.startswith('deck:'):
                    parts = user_input.split(' ', 1)
                    if len(parts) == 2:
                        deck_filter = parts[0].replace('deck:', '')
                        question = parts[1]
                
                # Query
                print()
                result = self.query(question, n_results=5, deck_filter=deck_filter)
                
                if 'error' in result:
                    print(f"❌ Error: {result['error']}\n")
                    continue
                
                print("📝 CONTEXTO:")
                print("=" * 60)
                print(result['context'])
                
                if result.get('sources'):
                    print("\n📚 FUENTES:")
                    for source in result['sources']:
                        print(f"   - [{source['deck']}] {source['file_name']} "
                              f"(relevancia: {1 - source['distance']:.2f})")
                
                print("\n" + "=" * 60 + "\n")
                
            except KeyboardInterrupt:
                logger.info("\n\n👋 Interrumpido")
                break
            except Exception as e:
                logger.error(f"\n❌ Error: {e}\n")
    
    def _print_stats(self):
        """Imprime estadísticas."""
        print("\n📊 ESTADÍSTICAS")
        print("=" * 60)
        
        try:
            stats = self.store.get_collection_stats(self.collection_name)
            print(f"📚 Total notas: {stats['total_documents']}")
            print(f"🕐 Última indexación: {self.last_index_time}")
            print(f"\n🎴 Por asignatura:")
            for deck, count in sorted(stats['by_deck'].items(), key=lambda x: -x[1]):
                print(f"   {deck:20} {count:3} notas")
        except:
            print("❌ Error obteniendo estadísticas")
        
        print("=" * 60 + "\n")
    
    def get_system_info(self) -> Dict:
        """Info del sistema."""
        info = {
            'vault_path': str(self.vault_path),
            'collection_name': self.collection_name,
            'indexed_notes': self.indexed_notes,
            'last_index_time': self.last_index_time,
            'embedding_model': self.embedder.model_name,
            'embedding_dimension': self.embedder.dimension
        }
        
        try:
            stats = self.store.get_collection_stats(self.collection_name)
            info['by_deck'] = stats['by_deck']
            info['total_documents'] = stats['total_documents']
        except:
            info['by_deck'] = {}
            info['total_documents'] = 0
        
        return info


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    vault_path = os.getenv('OBSIDIAN_VAULT_PATH', './data/vault')
    
    print("\n🧪 PROBANDO RAG SYSTEM\n")
    
    rag = ObsidianRAGSystem(vault_path=vault_path)
    
    print("\n1. Indexar vault")
    print("2. Consulta interactiva")
    print("3. Salir")
    
    opcion = input("\nOpción: ").strip()
    
    if opcion == '1':
        stats = rag.index_vault()
    elif opcion == '2':
        rag.interactive_query()
    else:
        print("👋 Adiós")
