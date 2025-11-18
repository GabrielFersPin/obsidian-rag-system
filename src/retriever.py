"""
Módulo de Retrieval para Obsidian RAG System

Este módulo implementa la búsqueda semántica sobre el vector store.
Proporciona funcionalidad para encontrar documentos relevantes basándose
en queries del usuario.

Componentes principales:
1. ObsidianRetriever: Clase principal para búsqueda semántica
2. Ranking y re-ranking de resultados
3. Filtrado por metadata

Autor: Gabriel
Fecha: 2025-01
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging

try:
    from .embeddings import EmbeddingGenerator
    from .vectorstore import ObsidianVectorStore, format_search_results
except ImportError:
    from embeddings import EmbeddingGenerator
    from vectorstore import ObsidianVectorStore, format_search_results

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """
    Resultado de una búsqueda.

    Attributes:
        document: Contenido del documento
        metadata: Metadata asociada
        score: Score de relevancia (distancia o similitud)
        rank: Posición en el ranking
    """
    document: str
    metadata: Dict[str, Any]
    score: float
    rank: int

    def __repr__(self) -> str:
        file_name = self.metadata.get('file_name', 'unknown')
        return f"RetrievalResult(rank={self.rank}, score={self.score:.3f}, file={file_name})"


class ObsidianRetriever:
    """
    Sistema de recuperación semántica para notas de Obsidian.

    Combina embeddings y vector store para encontrar documentos relevantes
    basándose en queries en lenguaje natural.

    Attributes:
        embedding_generator: Generador de embeddings
        vector_store: Store vectorial
        collection_name: Nombre de la collection a buscar

    Example:
        >>> retriever = ObsidianRetriever(
        ...     embedding_generator=generator,
        ...     vector_store=store,
        ...     collection_name="mis_notas"
        ... )
        >>> results = retriever.retrieve(
        ...     "¿Qué es QuickSort?",
        ...     top_k=3
        ... )
        >>> for res in results:
        ...     print(f"{res.rank}. {res.metadata['file_name']}")
    """

    def __init__(
        self,
        embedding_generator: EmbeddingGenerator,
        vector_store: ObsidianVectorStore,
        collection_name: str,
        default_top_k: int = 5
    ):
        """
        Inicializa el retriever.

        Args:
            embedding_generator: Instancia de EmbeddingGenerator
            vector_store: Instancia de ObsidianVectorStore
            collection_name: Nombre de la collection donde buscar
            default_top_k: Número por defecto de resultados a retornar

        Raises:
            ValueError: Si la collection no existe
        """
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self.collection_name = collection_name
        self.default_top_k = default_top_k

        # Verificar que la collection existe
        try:
            self.vector_store.get_collection(collection_name)
            logger.info(f"🔍 Retriever inicializado para collection: {collection_name}")
        except Exception as e:
            raise ValueError(
                f"Collection '{collection_name}' no existe. "
                f"Crea la collection primero."
            ) from e

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        deck_filter: Optional[str] = None,
        metadata_filter: Optional[Dict] = None,
        min_score: Optional[float] = None
    ) -> List[RetrievalResult]:
        """
        Recupera documentos relevantes para una query.

        Args:
            query: Query en lenguaje natural
            top_k: Número de resultados (usa default si es None)
            deck_filter: Filtrar por deck específico (ej: "Algoritmos")
            metadata_filter: Filtro adicional de metadata
            min_score: Score mínimo para incluir resultado

        Returns:
            Lista de RetrievalResult ordenados por relevancia

        Example:
            >>> results = retriever.retrieve(
            ...     "algoritmos de ordenamiento",
            ...     top_k=3,
            ...     deck_filter="Algoritmos"
            ... )
        """
        if not query or not query.strip():
            logger.warning("⚠️ Query vacía proporcionada")
            return []

        top_k = top_k or self.default_top_k

        logger.info(f"🔍 Recuperando documentos para query: '{query[:50]}...'")
        logger.info(f"   top_k: {top_k}")

        # 1. Generar embedding de la query
        query_embedding = self.embedding_generator.embed_text(query)

        # 2. Construir filtro de metadata
        where_filter = metadata_filter or {}

        if deck_filter:
            where_filter['deck'] = deck_filter
            logger.info(f"   Filtrando por deck: {deck_filter}")

        # 3. Buscar en vector store
        search_results = self.vector_store.search(
            collection_name=self.collection_name,
            query_embedding=query_embedding,
            n_results=top_k,
            where=where_filter if where_filter else None
        )

        # 4. Formatear resultados
        formatted = format_search_results(search_results)

        # 5. Convertir a RetrievalResult
        results = []
        for rank, result in enumerate(formatted, start=1):
            # ChromaDB retorna distancias (menor = más similar)
            # Convertir a score (mayor = más similar)
            score = 1 / (1 + result['distance'])

            # Filtrar por score mínimo si se especifica
            if min_score is not None and score < min_score:
                continue

            results.append(
                RetrievalResult(
                    document=result['document'],
                    metadata=result['metadata'],
                    score=score,
                    rank=rank
                )
            )

        logger.info(f"✅ {len(results)} documentos recuperados")

        return results

    def retrieve_batch(
        self,
        queries: List[str],
        top_k: Optional[int] = None,
        **kwargs
    ) -> List[List[RetrievalResult]]:
        """
        Recupera documentos para múltiples queries.

        Args:
            queries: Lista de queries
            top_k: Número de resultados por query
            **kwargs: Argumentos adicionales para retrieve()

        Returns:
            Lista de listas de RetrievalResult

        Example:
            >>> queries = [
            ...     "¿Qué es QuickSort?",
            ...     "Explicar Docker"
            ... ]
            >>> results = retriever.retrieve_batch(queries, top_k=3)
            >>> for i, query_results in enumerate(results):
            ...     print(f"Query {i}: {len(query_results)} resultados")
        """
        logger.info(f"🔍 Recuperando documentos para {len(queries)} queries")

        results = []
        for query in queries:
            query_results = self.retrieve(query, top_k=top_k, **kwargs)
            results.append(query_results)

        return results

    def get_context_for_llm(
        self,
        query: str,
        top_k: Optional[int] = None,
        max_chars: Optional[int] = None,
        include_metadata: bool = True,
        **kwargs
    ) -> str:
        """
        Prepara contexto formateado para enviar a un LLM.

        Este método recupera documentos y los formatea en un string
        optimizado para usar como contexto en prompts a LLMs.

        Args:
            query: Query del usuario
            top_k: Número de documentos a incluir
            max_chars: Límite de caracteres total (trunca si excede)
            include_metadata: Si incluir metadata en el contexto
            **kwargs: Argumentos adicionales para retrieve()

        Returns:
            String con contexto formateado para LLM

        Example:
            >>> context = retriever.get_context_for_llm(
            ...     "¿Qué es QuickSort?",
            ...     top_k=3,
            ...     max_chars=2000
            ... )
            >>> prompt = f"Contexto:\\n{context}\\n\\nPregunta: ¿Qué es QuickSort?"
        """
        results = self.retrieve(query, top_k=top_k, **kwargs)

        if not results:
            return "No se encontraron documentos relevantes."

        # Formatear contexto
        context_parts = []

        for result in results:
            # Header del documento
            file_name = result.metadata.get('file_name', 'unknown')
            deck = result.metadata.get('deck', 'general')

            doc_header = f"--- Documento {result.rank}: {file_name}"
            if include_metadata:
                doc_header += f" (Deck: {deck}, Relevancia: {result.score:.2f})"
            doc_header += " ---"

            # Contenido
            doc_content = result.document.strip()

            context_parts.append(f"{doc_header}\n{doc_content}")

        # Unir todo
        context = "\n\n".join(context_parts)

        # Truncar si excede max_chars
        if max_chars and len(context) > max_chars:
            context = context[:max_chars]
            context += "\n\n[... contexto truncado ...]"
            logger.warning(f"⚠️ Contexto truncado a {max_chars} caracteres")

        logger.info(f"📝 Contexto generado: {len(context)} caracteres")

        return context

    def get_related_notes(
        self,
        note_content: str,
        top_k: int = 5,
        exclude_metadata: Optional[Dict] = None
    ) -> List[RetrievalResult]:
        """
        Encuentra notas relacionadas a un contenido dado.

        Útil para descubrir conexiones entre notas.

        Args:
            note_content: Contenido de la nota base
            top_k: Número de notas relacionadas a encontrar
            exclude_metadata: Metadata para excluir (ej: la nota original)

        Returns:
            Lista de notas relacionadas

        Example:
            >>> # Encontrar notas relacionadas a QuickSort
            >>> related = retriever.get_related_notes(
            ...     note_content="QuickSort usa divide y conquista...",
            ...     top_k=5
            ... )
        """
        logger.info("🔗 Buscando notas relacionadas")

        # Usar el contenido como query
        return self.retrieve(
            query=note_content,
            top_k=top_k
        )

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas del retriever.

        Returns:
            Diccionario con estadísticas
        """
        collection_stats = self.vector_store.get_collection_stats(self.collection_name)

        return {
            'collection_name': self.collection_name,
            'total_documents': collection_stats['total_documents'],
            'by_deck': collection_stats['by_deck'],
            'default_top_k': self.default_top_k,
            'embedding_model': self.embedding_generator.model_name,
            'embedding_dimension': self.embedding_generator.dimension
        }


# ============================================
# Funciones de utilidad
# ============================================

def merge_results(
    results_list: List[List[RetrievalResult]],
    strategy: str = 'round_robin',
    max_results: int = 10
) -> List[RetrievalResult]:
    """
    Combina múltiples listas de resultados.

    Útil cuando se hacen múltiples queries y se quiere combinar resultados.

    Args:
        results_list: Lista de listas de resultados
        strategy: Estrategia de merge:
            - 'round_robin': Alternar entre listas
            - 'score': Ordenar por score global
        max_results: Número máximo de resultados finales

    Returns:
        Lista combinada de resultados
    """
    if not results_list:
        return []

    if strategy == 'round_robin':
        merged = []
        max_len = max(len(r) for r in results_list)

        for i in range(max_len):
            for results in results_list:
                if i < len(results) and len(merged) < max_results:
                    merged.append(results[i])

        # Re-asignar ranks
        for rank, result in enumerate(merged, start=1):
            result.rank = rank

        return merged

    elif strategy == 'score':
        # Combinar todas y ordenar por score
        all_results = []
        for results in results_list:
            all_results.extend(results)

        # Ordenar por score descendente
        all_results.sort(key=lambda x: x.score, reverse=True)

        # Limitar y re-asignar ranks
        merged = all_results[:max_results]
        for rank, result in enumerate(merged, start=1):
            result.rank = rank

        return merged

    else:
        raise ValueError(f"Estrategia '{strategy}' no soportada")


# ============================================
# Script de prueba
# ============================================

if __name__ == "__main__":
    """
    Script de prueba del retriever.

    Ejecutar con:
        python src/retriever.py
    """
    import numpy as np
    from datetime import datetime

    print("🧪 Probando módulo de retriever...\n")

    # Crear componentes
    from embeddings import EmbeddingGenerator
    from vectorstore import ObsidianVectorStore

    generator = EmbeddingGenerator()
    store = ObsidianVectorStore(persist_directory="./test_chroma_db")

    # Crear collection de prueba
    collection_name = "test_retrieval"
    store.create_collection(collection_name)

    # Datos de prueba
    test_notes = [
        {
            'file_name': 'QuickSort',
            'file_path': '/test/QuickSort.md',
            'content': 'QuickSort es un algoritmo de ordenamiento eficiente que usa divide y conquista',
            'deck': 'Algoritmos',
            'last_modified': datetime.now(),
            'flashcards': [],
            'links': []
        },
        {
            'file_name': 'MergeSort',
            'file_path': '/test/MergeSort.md',
            'content': 'MergeSort también usa divide y conquista y es estable',
            'deck': 'Algoritmos',
            'last_modified': datetime.now(),
            'flashcards': [],
            'links': []
        },
        {
            'file_name': 'Docker',
            'file_path': '/test/Docker.md',
            'content': 'Docker permite crear contenedores para aplicaciones',
            'deck': 'DevOps',
            'last_modified': datetime.now(),
            'flashcards': [],
            'links': []
        }
    ]

    # Generar embeddings
    print("🧮 Generando embeddings...")
    embeddings = generator.embed_batch([n['content'] for n in test_notes])

    # Añadir al store
    print("📝 Añadiendo notas...")
    store.add_notes(collection_name, test_notes, embeddings)

    # Crear retriever
    print("\n🔍 Creando retriever...")
    retriever = ObsidianRetriever(
        embedding_generator=generator,
        vector_store=store,
        collection_name=collection_name
    )

    # Probar búsqueda
    print("\n🔍 Probando búsqueda:")
    query = "algoritmo rápido de ordenamiento"
    results = retriever.retrieve(query, top_k=2)

    print(f"\nQuery: '{query}'")
    print(f"Resultados:")
    for res in results:
        print(f"  {res.rank}. [{res.score:.3f}] {res.metadata['file_name']}")
        print(f"     {res.document[:60]}...")

    # Probar filtro por deck
    print("\n🔍 Probando filtro por deck:")
    results_filtered = retriever.retrieve(
        "algoritmo",
        top_k=5,
        deck_filter="Algoritmos"
    )
    print(f"Resultados con deck='Algoritmos': {len(results_filtered)}")

    # Probar contexto para LLM
    print("\n📝 Generando contexto para LLM:")
    context = retriever.get_context_for_llm(
        query,
        top_k=2,
        max_chars=500
    )
    print(f"Contexto ({len(context)} chars):")
    print(context[:200] + "...")

    # Estadísticas
    print("\n📊 Estadísticas del retriever:")
    stats = retriever.get_stats()
    print(f"  Collection: {stats['collection_name']}")
    print(f"  Total documentos: {stats['total_documents']}")
    print(f"  Por deck: {stats['by_deck']}")

    # Limpiar
    print("\n🗑️ Limpiando...")
    store.delete_collection(collection_name)

    print("\n✅ Pruebas completadas!")
