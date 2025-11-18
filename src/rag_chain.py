"""
Módulo RAG Chain para Obsidian RAG System

Este módulo integra todos los componentes para crear un pipeline RAG completo:
1. Carga de notas (ObsidianLoader)
2. Generación de embeddings (EmbeddingGenerator)
3. Almacenamiento vectorial (ObsidianVectorStore)
4. Recuperación semántica (ObsidianRetriever)
5. Generación de respuestas (ClaudeClient)

Este es el módulo principal que orquesta todo el sistema.

Autor: Gabriel
Fecha: 2025-01
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging
from datetime import datetime
import json

from .obsidian_loader import ObsidianLoader
from .embeddings import EmbeddingGenerator
from .vectorstore import ObsidianVectorStore
from .retriever import ObsidianRetriever, RetrievalResult
from .claude_client import ClaudeClient, ClaudeResponse

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    """
    Resultado completo de una query RAG.

    Attributes:
        query: Query original del usuario
        answer: Respuesta generada por Claude
        retrieved_docs: Documentos recuperados
        tokens_used: Tokens totales usados
        retrieval_time: Tiempo de retrieval (segundos)
        generation_time: Tiempo de generación (segundos)
        metadata: Metadata adicional
    """
    query: str
    answer: str
    retrieved_docs: List[RetrievalResult]
    tokens_used: int
    retrieval_time: float
    generation_time: float
    metadata: Dict[str, Any]

    def __repr__(self) -> str:
        return (
            f"RAGResult(query='{self.query[:30]}...', "
            f"docs={len(self.retrieved_docs)}, "
            f"tokens={self.tokens_used})"
        )

    def format_sources(self) -> str:
        """
        Formatea las fuentes usadas.

        Returns:
            String con fuentes formateadas
        """
        if not self.retrieved_docs:
            return "No se usaron fuentes."

        sources = ["Fuentes consultadas:"]
        for doc in self.retrieved_docs:
            file_name = doc.metadata.get('file_name', 'unknown')
            deck = doc.metadata.get('deck', 'general')
            sources.append(f"  - {file_name} (Deck: {deck}, Relevancia: {doc.score:.2f})")

        return "\n".join(sources)


class ObsidianRAG:
    """
    Sistema RAG completo para notas de Obsidian.

    Esta clase orquesta todos los componentes del sistema para proporcionar
    una interfaz simple de preguntas y respuestas sobre tus notas.

    Attributes:
        vault_path: Path al vault de Obsidian
        collection_name: Nombre de la collection en vector store
        loader: ObsidianLoader instance
        embedding_generator: EmbeddingGenerator instance
        vector_store: ObsidianVectorStore instance
        retriever: ObsidianRetriever instance
        claude_client: ClaudeClient instance

    Example:
        >>> rag = ObsidianRAG(
        ...     vault_path="/path/to/vault",
        ...     collection_name="mis_notas"
        ... )
        >>> rag.index_vault()  # Una vez al inicio
        >>> result = rag.query("¿Qué es QuickSort?")
        >>> print(result.answer)
    """

    def __init__(
        self,
        vault_path: str,
        collection_name: str = "obsidian_notes",
        chroma_persist_dir: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        claude_model: str = "sonnet",
        anthropic_api_key: Optional[str] = None,
        models_cache_dir: str = "./models"
    ):
        """
        Inicializa el sistema RAG completo.

        Args:
            vault_path: Path al vault de Obsidian
            collection_name: Nombre para la collection de ChromaDB
            chroma_persist_dir: Directorio de persistencia de ChromaDB
            embedding_model: Modelo de embeddings a usar
            claude_model: Modelo de Claude ('haiku', 'sonnet', 'opus')
            anthropic_api_key: API key de Anthropic (o usa env var)
            models_cache_dir: Directorio para cachear modelos de embeddings

        Raises:
            ValueError: Si el vault_path no existe o falta API key
        """
        logger.info("🚀 Inicializando Obsidian RAG System...")

        self.vault_path = Path(vault_path)
        self.collection_name = collection_name

        # Validar vault
        if not self.vault_path.exists():
            raise ValueError(f"Vault path no existe: {vault_path}")

        # 1. Inicializar ObsidianLoader
        logger.info("📁 Inicializando loader...")
        self.loader = ObsidianLoader(vault_path=str(self.vault_path))

        # 2. Inicializar EmbeddingGenerator
        logger.info("🧮 Inicializando generador de embeddings...")
        os.environ['MODELS_CACHE_DIR'] = models_cache_dir
        self.embedding_generator = EmbeddingGenerator(
            model_name=embedding_model,
            cache_folder=models_cache_dir
        )

        # 3. Inicializar VectorStore
        logger.info("💾 Inicializando vector store...")
        self.vector_store = ObsidianVectorStore(
            persist_directory=chroma_persist_dir
        )

        # Crear o recuperar collection
        self.vector_store.create_collection(
            name=collection_name,
            metadata={
                'vault_path': str(self.vault_path),
                'created_at': datetime.now().isoformat()
            }
        )

        # 4. Inicializar Retriever
        logger.info("🔍 Inicializando retriever...")
        self.retriever = ObsidianRetriever(
            embedding_generator=self.embedding_generator,
            vector_store=self.vector_store,
            collection_name=collection_name
        )

        # 5. Inicializar ClaudeClient
        logger.info("🤖 Inicializando Claude client...")
        self.claude_client = ClaudeClient(
            api_key=anthropic_api_key,
            model=claude_model
        )

        logger.info("✅ Obsidian RAG System inicializado correctamente")

    def index_vault(
        self,
        force_reindex: bool = False,
        batch_size: int = 32,
        file_extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Indexa todas las notas del vault en el vector store.

        Args:
            force_reindex: Si True, elimina índice existente y reindexa
            batch_size: Tamaño de batch para embeddings
            file_extensions: Extensiones a indexar (default: ['.md'])

        Returns:
            Diccionario con estadísticas de indexación

        Example:
            >>> stats = rag.index_vault()
            >>> print(f"Indexadas {stats['notes_indexed']} notas")
        """
        logger.info("📚 Indexando vault...")

        # Si force_reindex, eliminar collection y recrear
        if force_reindex:
            logger.warning("🗑️ Forzando reindexación (eliminando índice existente)")
            try:
                self.vector_store.delete_collection(self.collection_name)
                self.vector_store.create_collection(
                    name=self.collection_name,
                    metadata={
                        'vault_path': str(self.vault_path),
                        'reindexed_at': datetime.now().isoformat()
                    }
                )
            except Exception as e:
                logger.warning(f"⚠️ Error eliminando collection: {e}")

        # Cargar notas
        logger.info("📖 Cargando notas del vault...")
        notes = self.loader.load_notes(file_extensions=file_extensions)

        if not notes:
            logger.warning("⚠️ No se encontraron notas para indexar")
            return {
                'notes_indexed': 0,
                'embeddings_generated': 0,
                'total_time': 0
            }

        # Generar embeddings
        logger.info(f"🧮 Generando embeddings para {len(notes)} notas...")
        import time
        start_time = time.time()

        contents = [note['content'] for note in notes]
        embeddings = self.embedding_generator.embed_batch(
            contents,
            batch_size=batch_size,
            show_progress=True
        )

        embedding_time = time.time() - start_time
        logger.info(f"   Tiempo de embeddings: {embedding_time:.2f}s")

        # Añadir al vector store
        logger.info(f"💾 Almacenando en vector store...")
        start_time = time.time()

        self.vector_store.add_notes(
            collection_name=self.collection_name,
            notes=notes,
            embeddings=embeddings
        )

        store_time = time.time() - start_time
        logger.info(f"   Tiempo de almacenamiento: {store_time:.2f}s")

        total_time = embedding_time + store_time

        stats = {
            'notes_indexed': len(notes),
            'embeddings_generated': len(embeddings),
            'embedding_time': embedding_time,
            'store_time': store_time,
            'total_time': total_time,
            'indexed_at': datetime.now().isoformat()
        }

        logger.info(f"✅ Indexación completada en {total_time:.2f}s")

        return stats

    def query(
        self,
        question: str,
        top_k: int = 5,
        deck_filter: Optional[str] = None,
        include_sources: bool = True,
        max_context_chars: Optional[int] = None,
        claude_temperature: Optional[float] = None
    ) -> RAGResult:
        """
        Realiza una query completa RAG.

        Args:
            question: Pregunta del usuario
            top_k: Número de documentos a recuperar
            deck_filter: Filtrar por deck específico
            include_sources: Si incluir fuentes en respuesta
            max_context_chars: Límite de caracteres de contexto
            claude_temperature: Override de temperatura para Claude

        Returns:
            RAGResult con respuesta y metadata

        Example:
            >>> result = rag.query(
            ...     "¿Qué es QuickSort?",
            ...     top_k=3,
            ...     deck_filter="Algoritmos"
            ... )
            >>> print(result.answer)
            >>> print(result.format_sources())
        """
        import time

        logger.info(f"❓ Query: '{question}'")

        # 1. Retrieval
        logger.info("🔍 Recuperando documentos relevantes...")
        retrieval_start = time.time()

        retrieved_docs = self.retriever.retrieve(
            query=question,
            top_k=top_k,
            deck_filter=deck_filter
        )

        retrieval_time = time.time() - retrieval_start
        logger.info(f"   {len(retrieved_docs)} documentos recuperados en {retrieval_time:.2f}s")

        if not retrieved_docs:
            logger.warning("⚠️ No se encontraron documentos relevantes")
            return RAGResult(
                query=question,
                answer="No encontré información relevante en tus notas para responder esta pregunta.",
                retrieved_docs=[],
                tokens_used=0,
                retrieval_time=retrieval_time,
                generation_time=0.0,
                metadata={'no_results': True}
            )

        # 2. Preparar contexto
        context = self.retriever.get_context_for_llm(
            query=question,
            top_k=top_k,
            max_chars=max_context_chars,
            deck_filter=deck_filter
        )

        # 3. Generar respuesta con Claude
        logger.info("🤖 Generando respuesta con Claude...")
        generation_start = time.time()

        claude_kwargs = {}
        if claude_temperature is not None:
            claude_kwargs['temperature'] = claude_temperature

        claude_response = self.claude_client.generate_rag_response(
            query=question,
            context=context,
            include_sources=include_sources,
            **claude_kwargs
        )

        generation_time = time.time() - generation_start
        logger.info(f"   Respuesta generada en {generation_time:.2f}s")

        # 4. Construir resultado
        result = RAGResult(
            query=question,
            answer=claude_response.content,
            retrieved_docs=retrieved_docs,
            tokens_used=claude_response.tokens_input + claude_response.tokens_output,
            retrieval_time=retrieval_time,
            generation_time=generation_time,
            metadata={
                'top_k': top_k,
                'deck_filter': deck_filter,
                'claude_model': claude_response.model,
                'stop_reason': claude_response.stop_reason,
                'timestamp': datetime.now().isoformat()
            }
        )

        logger.info(f"✅ Query completada (total: {retrieval_time + generation_time:.2f}s)")

        return result

    def chat(
        self,
        message: str,
        retrieve_context: bool = True,
        top_k: int = 3,
        **kwargs
    ) -> RAGResult:
        """
        Modo conversacional con recuperación opcional de contexto.

        Args:
            message: Mensaje del usuario
            retrieve_context: Si recuperar contexto para este mensaje
            top_k: Número de documentos a recuperar
            **kwargs: Argumentos adicionales

        Returns:
            RAGResult con respuesta
        """
        import time

        logger.info(f"💬 Chat: '{message[:50]}...'")

        retrieval_time = 0.0
        retrieved_docs = []
        context = None

        # Recuperar contexto si se solicita
        if retrieve_context:
            retrieval_start = time.time()
            retrieved_docs = self.retriever.retrieve(message, top_k=top_k)
            retrieval_time = time.time() - retrieval_start

            if retrieved_docs:
                context = self.retriever.get_context_for_llm(message, top_k=top_k)

        # Generar respuesta
        generation_start = time.time()
        claude_response = self.claude_client.chat(
            message=message,
            context=context,
            use_history=True
        )
        generation_time = time.time() - generation_start

        return RAGResult(
            query=message,
            answer=claude_response.content,
            retrieved_docs=retrieved_docs,
            tokens_used=claude_response.tokens_input + claude_response.tokens_output,
            retrieval_time=retrieval_time,
            generation_time=generation_time,
            metadata={
                'mode': 'chat',
                'context_retrieved': retrieve_context,
                'timestamp': datetime.now().isoformat()
            }
        )

    def find_related_notes(
        self,
        note_name: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Encuentra notas relacionadas a una nota específica.

        Args:
            note_name: Nombre de la nota base
            top_k: Número de notas relacionadas

        Returns:
            Lista de notas relacionadas
        """
        logger.info(f"🔗 Buscando notas relacionadas a '{note_name}'")

        # Buscar la nota por nombre en el vector store
        # (esto es una simplificación, idealmente buscaríamos por metadata)
        results = self.retriever.retrieve(
            query=note_name,
            top_k=1
        )

        if not results:
            logger.warning(f"⚠️ Nota '{note_name}' no encontrada")
            return []

        # Usar contenido de la nota para buscar relacionadas
        note_content = results[0].document

        related = self.retriever.get_related_notes(
            note_content=note_content,
            top_k=top_k + 1  # +1 porque incluirá la nota original
        )

        # Filtrar la nota original (primera)
        related = [r for r in related if r.metadata.get('file_name') != note_name]

        return related[:top_k]

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del sistema RAG.

        Returns:
            Diccionario con estadísticas
        """
        logger.info("📊 Obteniendo estadísticas del sistema...")

        collection_stats = self.vector_store.get_collection_stats(self.collection_name)
        retriever_stats = self.retriever.get_stats()
        claude_info = self.claude_client.get_info()

        return {
            'vault_path': str(self.vault_path),
            'collection_name': self.collection_name,
            'total_notes': collection_stats['total_documents'],
            'notes_by_deck': collection_stats['by_deck'],
            'notes_with_flashcards': collection_stats.get('with_flashcards', 0),
            'embedding_model': retriever_stats['embedding_model'],
            'embedding_dimension': retriever_stats['embedding_dimension'],
            'claude_model': claude_info['model'],
            'conversation_length': claude_info['conversation_length']
        }

    def export_stats(self, output_path: str) -> None:
        """
        Exporta estadísticas a un archivo JSON.

        Args:
            output_path: Path del archivo de salida
        """
        stats = self.get_stats()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 Estadísticas exportadas a {output_path}")

    def clear_conversation(self) -> None:
        """Limpia el historial de conversación de Claude."""
        self.claude_client.clear_history()
        logger.info("🗑️ Historial de conversación limpiado")


# ============================================
# Funciones de utilidad
# ============================================

def create_rag_from_config(config_path: str) -> ObsidianRAG:
    """
    Crea instancia de RAG desde archivo de configuración JSON.

    Args:
        config_path: Path al archivo de configuración

    Returns:
        Instancia de ObsidianRAG configurada

    Example:
        >>> rag = create_rag_from_config("config.json")
    """
    with open(config_path, 'r') as f:
        config = json.load(f)

    return ObsidianRAG(**config)


# ============================================
# Script de prueba
# ============================================

if __name__ == "__main__":
    """
    Script de prueba del sistema RAG completo.

    Ejecutar con:
        export ANTHROPIC_API_KEY=sk-...
        python src/rag_chain.py /path/to/vault
    """
    import sys

    print("🧪 Probando sistema RAG completo...\n")

    # Verificar argumentos
    if len(sys.argv) < 2:
        print("❌ Uso: python src/rag_chain.py /path/to/vault")
        sys.exit(1)

    vault_path = sys.argv[1]

    # Verificar API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY no configurada")
        print("   export ANTHROPIC_API_KEY=sk-...")
        sys.exit(1)

    try:
        # Crear sistema RAG
        print("🚀 Inicializando sistema RAG...")
        rag = ObsidianRAG(
            vault_path=vault_path,
            collection_name="test_rag",
            claude_model="haiku"  # Usar haiku para tests
        )

        # Indexar vault
        print("\n📚 Indexando vault...")
        stats = rag.index_vault()
        print(f"   Notas indexadas: {stats['notes_indexed']}")
        print(f"   Tiempo total: {stats['total_time']:.2f}s")

        # Query de prueba
        print("\n❓ Query de prueba:")
        query = "¿Cuáles son los conceptos principales en mis notas?"
        result = rag.query(query, top_k=3)

        print(f"\nPregunta: {result.query}")
        print(f"\nRespuesta:\n{result.answer}")
        print(f"\n{result.format_sources()}")
        print(f"\nTokens usados: {result.tokens_used}")
        print(f"Tiempo total: {result.retrieval_time + result.generation_time:.2f}s")

        # Estadísticas
        print("\n📊 Estadísticas del sistema:")
        system_stats = rag.get_stats()
        print(f"   Total notas: {system_stats['total_notes']}")
        print(f"   Por deck: {system_stats['notes_by_deck']}")
        print(f"   Modelo Claude: {system_stats['claude_model']}")

        # Limpiar
        print("\n🗑️ Limpiando...")
        rag.vector_store.delete_collection("test_rag")

        print("\n✅ Pruebas completadas!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
