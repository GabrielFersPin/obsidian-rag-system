"""
Módulo de Vector Store para Obsidian RAG System

Este módulo gestiona el almacenamiento y búsqueda de embeddings usando ChromaDB.
Proporciona una interfaz de alto nivel para operaciones CRUD y búsqueda semántica.

Componentes principales:
1. ObsidianVectorStore: Clase principal para gestionar collections
2. Métodos CRUD: add, query, update, delete
3. Utilities: estadísticas, backup, restore

Autor: Gabriel
Fecha: 2025-01
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any, Union
import uuid
import logging
from datetime import datetime
import json
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ObsidianVectorStore:
    """
    Gestor de base de datos vectorial para notas de Obsidian.
    
    Encapsula ChromaDB y proporciona métodos específicos para trabajar
    con notas de Obsidian, incluyendo metadata filtering, búsqueda semántica,
    y gestión de múltiples collections.
    
    Attributes:
        client: Cliente de ChromaDB
        persist_directory: Directorio de persistencia
        collections: Dict de collections activas
    
    Example:
        >>> store = ObsidianVectorStore()
        >>> store.create_collection("mis_notas")
        >>> store.add_notes(collection_name="mis_notas", notes=notes_data)
        >>> results = store.search(collection_name="mis_notas", query_embedding=vec)
    """
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        client_settings: Optional[Dict] = None
    ):
        """
        Inicializa el vector store.
        
        Args:
            persist_directory: Directorio donde persistir la base de datos
            client_settings: Configuración adicional para ChromaDB client
        
        Raises:
            RuntimeError: Si no se puede crear el cliente
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🚀 Inicializando Vector Store")
        logger.info(f"📁 Persist directory: {self.persist_directory}")
        
        # Configuración por defecto
        default_settings = Settings(
            persist_directory=str(self.persist_directory),
            anonymized_telemetry=False
        )
        
        # Mergear con settings custom si se proporcionan
        if client_settings:
            for key, value in client_settings.items():
                setattr(default_settings, key, value)
        
        try:
            self.client = chromadb.Client(default_settings)
            logger.info("✅ Cliente ChromaDB creado")
            
            # Cargar collections existentes
            self.collections = {}
            existing = self.client.list_collections()
            logger.info(f"📚 Collections existentes: {len(existing)}")
            for col in existing:
                logger.info(f"   - {col.name}")
                
        except Exception as e:
            logger.error(f"❌ Error creando cliente ChromaDB: {e}")
            raise RuntimeError("No se pudo inicializar ChromaDB") from e
    
    def create_collection(
        self,
        name: str,
        metadata: Optional[Dict] = None,
        get_or_create: bool = True
    ) -> chromadb.Collection:
        """
        Crea una nueva collection o recupera una existente.
        
        Args:
            name: Nombre de la collection
            metadata: Metadata de la collection (opcional)
            get_or_create: Si True, obtiene si existe, si False lanza error
        
        Returns:
            Collection de ChromaDB
        
        Example:
            >>> collection = store.create_collection(
            ...     name="algoritmos",
            ...     metadata={"description": "Notas de algoritmos"}
            ... )
        """
        logger.info(f"📝 Creando/obteniendo collection: {name}")
        
        try:
            if get_or_create:
                collection = self.client.get_or_create_collection(
                    name=name,
                    metadata=metadata or {}
                )
                logger.info(f"   Collection obtenida/creada: {name}")
            else:
                collection = self.client.create_collection(
                    name=name,
                    metadata=metadata or {}
                )
                logger.info(f"   Nueva collection creada: {name}")
            
            # Guardar referencia
            self.collections[name] = collection
            
            return collection
            
        except Exception as e:
            logger.error(f"❌ Error con collection {name}: {e}")
            raise
    
    def get_collection(self, name: str) -> chromadb.Collection:
        """
        Obtiene una collection existente.
        
        Args:
            name: Nombre de la collection
        
        Returns:
            Collection de ChromaDB
        
        Raises:
            ValueError: Si la collection no existe
        """
        if name in self.collections:
            return self.collections[name]
        
        try:
            collection = self.client.get_collection(name)
            self.collections[name] = collection
            return collection
        except Exception as e:
            raise ValueError(f"Collection '{name}' no existe") from e
    
    def delete_collection(self, name: str) -> None:
        """
        Elimina una collection completa.
        
        Args:
            name: Nombre de la collection a eliminar
        
        Warning:
            Esta operación es irreversible. Todos los documentos se perderán.
        """
        logger.warning(f"🗑️ Eliminando collection: {name}")
        
        try:
            self.client.delete_collection(name)
            
            # Remover de cache
            if name in self.collections:
                del self.collections[name]
            
            logger.info(f"   ✅ Collection {name} eliminada")
            
        except Exception as e:
            logger.error(f"❌ Error eliminando collection {name}: {e}")
            raise
    
    def add_notes(
        self,
        collection_name: str,
        notes: List[Dict],
        embeddings: List[Any]
    ) -> None:
        """
        Añade notas a una collection.
        
        Args:
            collection_name: Nombre de la collection
            notes: Lista de diccionarios con datos de notas
            embeddings: Lista de vectores (numpy arrays o listas)
        
        Expected note format:
            {
                'file_name': str,
                'file_path': str,
                'content': str,
                'deck': str,
                'last_modified': datetime,
                'flashcards': List,
                'links': List,
                ... (metadata adicional)
            }
        
        Example:
            >>> notes = [
            ...     {
            ...         'file_name': 'QuickSort',
            ...         'content': 'QuickSort es...',
            ...         'deck': 'Algoritmos',
            ...         ...
            ...     }
            ... ]
            >>> embeddings = [[0.1, 0.2, ...], ...]
            >>> store.add_notes("mis_notas", notes, embeddings)
        """
        collection = self.get_collection(collection_name)
        
        if len(notes) != len(embeddings):
            raise ValueError(
                f"Cantidad de notas ({len(notes)}) no coincide con "
                f"cantidad de embeddings ({len(embeddings)})"
            )
        
        logger.info(f"📝 Añadiendo {len(notes)} notas a '{collection_name}'")
        
        # Preparar datos
        ids = []
        documents = []
        metadatas = []
        embeddings_list = []
        
        for note, embedding in zip(notes, embeddings):
            # Generar ID único (puedes usar file_path hash si prefieres)
            note_id = str(uuid.uuid4())
            ids.append(note_id)
            
            # Documento (contenido de la nota)
            documents.append(note.get('content', ''))
            
            # Metadata (todo excepto content)
            metadata = {
                'file_name': note.get('file_name', 'unknown'),
                'file_path': note.get('file_path', ''),
                'deck': note.get('deck', 'general'),
                'has_flashcards': len(note.get('flashcards', [])) > 0,
                'num_flashcards': len(note.get('flashcards', [])),
                'num_links': len(note.get('links', [])),
                'last_modified': note.get('last_modified', datetime.now()).isoformat(),
                'indexed_at': datetime.now().isoformat()
            }
            
            # Añadir metadata adicional si existe
            for key in ['status', 'tipo_nota', 'created']:
                if key in note:
                    metadata[key] = str(note[key])
            
            metadatas.append(metadata)
            
            # Embedding (convertir a lista si es numpy)
            if hasattr(embedding, 'tolist'):
                embeddings_list.append(embedding.tolist())
            else:
                embeddings_list.append(embedding)
        
        # Añadir a collection
        try:
            collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents
            )
            
            logger.info(f"✅ {len(notes)} notas añadidas exitosamente")
            logger.info(f"   Total en collection: {collection.count()}")
            
        except Exception as e:
            logger.error(f"❌ Error añadiendo notas: {e}")
            raise
    
    def search(
        self,
        collection_name: str,
        query_embedding: Union[List[float], Any],
        n_results: int = 5,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ) -> Dict:
        """
        Busca documentos similares en una collection.
        
        Args:
            collection_name: Nombre de la collection
            query_embedding: Vector de búsqueda
            n_results: Número de resultados a retornar
            where: Filtro de metadata (ej: {"deck": "Algoritmos"})
            where_document: Filtro de contenido de documento
        
        Returns:
            Diccionario con resultados:
            {
                'ids': List[List[str]],
                'distances': List[List[float]],
                'documents': List[List[str]],
                'metadatas': List[List[Dict]]
            }
        
        Example:
            >>> results = store.search(
            ...     collection_name="mis_notas",
            ...     query_embedding=[0.1, 0.2, ...],
            ...     n_results=3,
            ...     where={"deck": "Algoritmos"}
            ... )
            >>> for doc in results['documents'][0]:
            ...     print(doc)
        """
        collection = self.get_collection(collection_name)
        
        # Convertir embedding si es necesario
        if hasattr(query_embedding, 'tolist'):
            query_embedding = query_embedding.tolist()
        
        logger.info(f"🔍 Buscando en '{collection_name}'")
        logger.info(f"   n_results: {n_results}")
        if where:
            logger.info(f"   Filtro metadata: {where}")
        
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            
            num_found = len(results['ids'][0]) if results['ids'] else 0
            logger.info(f"✅ {num_found} resultados encontrados")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda: {e}")
            raise
    
    def update_note(
        self,
        collection_name: str,
        note_id: str,
        embedding: Optional[Any] = None,
        metadata: Optional[Dict] = None,
        document: Optional[str] = None
    ) -> None:
        """
        Actualiza una nota existente.
        
        Args:
            collection_name: Nombre de la collection
            note_id: ID del documento a actualizar
            embedding: Nuevo embedding (opcional)
            metadata: Nueva metadata (opcional)
            document: Nuevo contenido (opcional)
        
        Example:
            >>> store.update_note(
            ...     collection_name="mis_notas",
            ...     note_id="abc-123",
            ...     metadata={"reviewed": True}
            ... )
        """
        collection = self.get_collection(collection_name)
        
        logger.info(f"🔄 Actualizando nota {note_id} en '{collection_name}'")
        
        # Preparar datos de actualización
        update_data = {'ids': [note_id]}
        
        if embedding is not None:
            if hasattr(embedding, 'tolist'):
                embedding = embedding.tolist()
            update_data['embeddings'] = [embedding]
        
        if metadata is not None:
            # Añadir timestamp de actualización
            metadata['updated_at'] = datetime.now().isoformat()
            update_data['metadatas'] = [metadata]
        
        if document is not None:
            update_data['documents'] = [document]
        
        try:
            collection.update(**update_data)
            logger.info(f"✅ Nota actualizada")
            
        except Exception as e:
            logger.error(f"❌ Error actualizando nota: {e}")
            raise
    
    def delete_note(
        self,
        collection_name: str,
        note_id: str
    ) -> None:
        """
        Elimina una nota por su ID.
        
        Args:
            collection_name: Nombre de la collection
            note_id: ID del documento a eliminar
        """
        collection = self.get_collection(collection_name)
        
        logger.info(f"🗑️ Eliminando nota {note_id} de '{collection_name}'")
        
        try:
            collection.delete(ids=[note_id])
            logger.info(f"✅ Nota eliminada")
            
        except Exception as e:
            logger.error(f"❌ Error eliminando nota: {e}")
            raise
    
    def delete_by_filter(
        self,
        collection_name: str,
        where: Dict
    ) -> int:
        """
        Elimina notas que coincidan con un filtro.
        
        Args:
            collection_name: Nombre de la collection
            where: Filtro de metadata
        
        Returns:
            Número de documentos eliminados
        
        Example:
            >>> # Eliminar todas las notas del deck "Temporal"
            >>> deleted = store.delete_by_filter(
            ...     "mis_notas",
            ...     where={"deck": "Temporal"}
            ... )
            >>> print(f"Eliminadas {deleted} notas")
        """
        collection = self.get_collection(collection_name)
        
        logger.info(f"🗑️ Eliminando notas con filtro: {where}")
        
        # Primero obtener las notas que coinciden
        before_count = collection.count()
        
        try:
            collection.delete(where=where)
            
            after_count = collection.count()
            deleted = before_count - after_count
            
            logger.info(f"✅ {deleted} notas eliminadas")
            
            return deleted
            
        except Exception as e:
            logger.error(f"❌ Error eliminando con filtro: {e}")
            raise
    
    def get_collection_stats(self, collection_name: str) -> Dict:
        """
        Obtiene estadísticas de una collection.
        
        Args:
            collection_name: Nombre de la collection
        
        Returns:
            Diccionario con estadísticas
        
        Example:
            >>> stats = store.get_collection_stats("mis_notas")
            >>> print(f"Total: {stats['total_documents']}")
            >>> print(f"Por deck: {stats['by_deck']}")
        """
        collection = self.get_collection(collection_name)
        
        logger.info(f"📊 Obteniendo estadísticas de '{collection_name}'")
        
        try:
            # Total de documentos
            total = collection.count()
            
            # Obtener todos para análisis
            all_data = collection.get()
            
            # Estadísticas por deck
            by_deck = {}
            by_status = {}
            has_flashcards_count = 0
            
            for metadata in all_data['metadatas']:
                # Por deck
                deck = metadata.get('deck', 'unknown')
                by_deck[deck] = by_deck.get(deck, 0) + 1
                
                # Por status
                status = metadata.get('status', 'unknown')
                by_status[status] = by_status.get(status, 0) + 1
                
                # Con flashcards
                if metadata.get('has_flashcards', False):
                    has_flashcards_count += 1
            
            stats = {
                'total_documents': total,
                'by_deck': by_deck,
                'by_status': by_status,
                'with_flashcards': has_flashcards_count,
                'collection_metadata': collection.metadata
            }
            
            logger.info(f"✅ Estadísticas obtenidas")
            logger.info(f"   Total documentos: {total}")
            logger.info(f"   Decks: {len(by_deck)}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            raise
    
    def list_collections(self) -> List[str]:
        """
        Lista todas las collections disponibles.
        
        Returns:
            Lista de nombres de collections
        """
        collections = self.client.list_collections()
        names = [col.name for col in collections]
        
        logger.info(f"📚 Collections disponibles: {len(names)}")
        for name in names:
            logger.info(f"   - {name}")
        
        return names
    
    def export_collection(
        self,
        collection_name: str,
        output_path: str
    ) -> None:
        """
        Exporta una collection a JSON (backup).
        
        Args:
            collection_name: Nombre de la collection
            output_path: Ruta del archivo de salida
        
        Example:
            >>> store.export_collection(
            ...     "mis_notas",
            ...     "backup_mis_notas.json"
            ... )
        """
        collection = self.get_collection(collection_name)
        
        logger.info(f"💾 Exportando '{collection_name}' a {output_path}")
        
        try:
            # Obtener todos los datos
            data = collection.get()
            
            # Preparar para JSON
            export_data = {
                'collection_name': collection_name,
                'collection_metadata': collection.metadata,
                'exported_at': datetime.now().isoformat(),
                'total_documents': collection.count(),
                'data': {
                    'ids': data['ids'],
                    'documents': data['documents'],
                    'metadatas': data['metadatas'],
                    'embeddings': data['embeddings']
                }
            }
            
            # Guardar
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Collection exportada exitosamente")
            logger.info(f"   Tamaño: {Path(output_path).stat().st_size / 1024:.2f} KB")
            
        except Exception as e:
            logger.error(f"❌ Error exportando collection: {e}")
            raise
    
    def get_info(self) -> Dict:
        """
        Información general del vector store.
        
        Returns:
            Diccionario con información del sistema
        """
        collections = self.client.list_collections()
        
        info = {
            'persist_directory': str(self.persist_directory),
            'total_collections': len(collections),
            'collections': [
                {
                    'name': col.name,
                    'count': col.count(),
                    'metadata': col.metadata
                }
                for col in collections
            ]
        }
        
        return info


# ============================================
# Funciones de utilidad
# ============================================

def format_search_results(results: Dict) -> List[Dict]:
    """
    Formatea resultados de búsqueda para mostrar fácilmente.
    
    Args:
        results: Resultados crudos de ChromaDB
    
    Returns:
        Lista de dicts con resultados formateados
    
    Example:
        >>> results = collection.query(...)
        >>> formatted = format_search_results(results)
        >>> for res in formatted:
        ...     print(f"{res['distance']:.3f} - {res['document'][:50]}")
    """
    formatted = []
    
    if not results['ids'] or not results['ids'][0]:
        return formatted
    
    for i in range(len(results['ids'][0])):
        formatted.append({
            'id': results['ids'][0][i],
            'distance': results['distances'][0][i],
            'document': results['documents'][0][i],
            'metadata': results['metadatas'][0][i]
        })
    
    return formatted


# ============================================
# Script de prueba
# ============================================

if __name__ == "__main__":
    """
    Script de prueba del módulo vectorstore.
    
    Ejecutar con:
        python src/vectorstore.py
    """
    import numpy as np
    
    print("🧪 Probando módulo de vectorstore...\n")
    
    # Crear vector store
    store = ObsidianVectorStore(persist_directory="./test_chroma_db")
    
    # Crear collection de prueba
    collection_name = "test_collection"
    store.create_collection(
        collection_name,
        metadata={"description": "Collection de prueba"}
    )
    
    # Datos de prueba
    test_notes = [
        {
            'file_name': 'QuickSort',
            'file_path': '/test/QuickSort.md',
            'content': 'QuickSort es un algoritmo eficiente',
            'deck': 'Algoritmos',
            'last_modified': datetime.now(),
            'flashcards': ['Q1', 'Q2'],
            'links': ['MergeSort']
        },
        {
            'file_name': 'Docker',
            'file_path': '/test/Docker.md',
            'content': 'Docker permite containerización',
            'deck': 'Nube',
            'last_modified': datetime.now(),
            'flashcards': [],
            'links': []
        }
    ]
    
    # Embeddings de prueba (random)
    test_embeddings = [np.random.rand(384) for _ in test_notes]
    
    # Añadir notas
    print("📝 Añadiendo notas...")
    store.add_notes(collection_name, test_notes, test_embeddings)
    
    # Buscar
    print("\n🔍 Buscando...")
    query_emb = np.random.rand(384)
    results = store.search(
        collection_name,
        query_emb,
        n_results=2
    )
    
    formatted = format_search_results(results)
    for i, res in enumerate(formatted, 1):
        print(f"{i}. [{res['distance']:.3f}] {res['metadata']['file_name']}")
    
    # Estadísticas
    print("\n📊 Estadísticas:")
    stats = store.get_collection_stats(collection_name)
    print(f"   Total: {stats['total_documents']}")
    print(f"   Por deck: {stats['by_deck']}")
    
    # Info general
    print("\n📋 Info del sistema:")
    info = store.get_info()
    print(f"   Collections: {info['total_collections']}")
    
    # Limpiar
    print("\n🗑️ Limpiando...")
    store.delete_collection(collection_name)
    
    print("\n✅ Pruebas completadas!")