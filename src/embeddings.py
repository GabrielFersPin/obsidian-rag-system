"""
Módulo de Embeddings para Obsidian RAG System

Este módulo se encarga de convertir texto en representaciones vectoriales
usando Sentence Transformers.

Componentes principales:
1. EmbeddingGenerator: Clase para generar embeddings
2. Funciones de similitud: Calcular distancias entre vectores
3. Batch processing: Procesar múltiples textos eficientemente

Autor: Gabriel
Fecha: 2025-01
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union, Optional
import numpy as np
from tqdm import tqdm
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generador de embeddings usando Sentence Transformers.
    
    Esta clase encapsula la funcionalidad de convertir texto en vectores
    numéricos que capturan el significado semántico.
    
    Attributes:
        model_name: Nombre del modelo de Sentence Transformers
        model: Instancia del modelo cargado
        dimension: Dimensionalidad de los embeddings generados
        device: Dispositivo para computación (cpu/cuda)
    
    Example:
        >>> generator = EmbeddingGenerator()
        >>> embedding = generator.embed_text("QuickSort es eficiente")
        >>> print(embedding.shape)
        (384,)
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_folder: Optional[str] = None,
        device: Optional[str] = None
    ):
        """
        Inicializa el generador de embeddings.
        
        Args:
            model_name: Nombre del modelo a usar. Opciones populares:
                - all-MiniLM-L6-v2: Rápido, 384 dim (recomendado)
                - all-mpnet-base-v2: Mejor calidad, 768 dim
                - paraphrase-multilingual: Soporte español
            cache_folder: Carpeta para cachear modelos descargados
            device: 'cpu', 'cuda', o None (auto-detect)
        
        Raises:
            RuntimeError: Si el modelo no se puede cargar
        """
        self.model_name = model_name
        
        # Configurar cache folder
        if cache_folder is None:
            cache_folder = os.getenv('MODELS_CACHE_DIR', './models')
        
        logger.info(f"🚀 Cargando modelo de embeddings: {model_name}")
        logger.info(f"📁 Cache folder: {cache_folder}")
        
        try:
            self.model = SentenceTransformer(
                model_name,
                cache_folder=cache_folder,
                device=device
            )
            
            self.dimension = self.model.get_sentence_embedding_dimension()
            self.device = self.model.device
            
            logger.info(f"✅ Modelo cargado exitosamente")
            logger.info(f"   - Dimensiones: {self.dimension}")
            logger.info(f"   - Device: {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelo: {e}")
            raise RuntimeError(f"No se pudo cargar el modelo {model_name}") from e
    
    def embed_text(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Genera embedding para un texto único.
        
        Args:
            text: Texto a convertir en embedding
            normalize: Si True, normaliza el vector (recomendado para cosine similarity)
        
        Returns:
            Vector numpy de dimensión (self.dimension,)
        
        Example:
            >>> embedding = generator.embed_text("Algoritmo QuickSort")
            >>> print(embedding.shape)
            (384,)
        """
        if not text or not text.strip():
            logger.warning("⚠️ Texto vacío proporcionado, retornando vector de ceros")
            return np.zeros(self.dimension)
        
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
            show_progress_bar=False
        )
        
        return embedding
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        normalize: bool = True,
        show_progress: bool = True
    ) -> List[np.ndarray]:
        """
        Genera embeddings para múltiples textos eficientemente.
        
        Args:
            texts: Lista de textos a procesar
            batch_size: Tamaño del batch para procesamiento paralelo
            normalize: Si True, normaliza vectores
            show_progress: Mostrar barra de progreso
        
        Returns:
            Lista de embeddings (arrays numpy)
        
        Example:
            >>> texts = ["QuickSort", "MergeSort", "BubbleSort"]
            >>> embeddings = generator.embed_batch(texts)
            >>> print(len(embeddings))
            3
        """
        if not texts:
            logger.warning("⚠️ Lista vacía proporcionada")
            return []
        
        # Filtrar textos vacíos
        textos_validos = [t for t in texts if t and t.strip()]
        
        if len(textos_validos) < len(texts):
            logger.warning(
                f"⚠️ {len(texts) - len(textos_validos)} textos vacíos ignorados"
            )
        
        if not textos_validos:
            return [np.zeros(self.dimension) for _ in texts]
        
        logger.info(f"🧮 Generando embeddings para {len(textos_validos)} textos...")
        
        embeddings = []
        
        # Procesar en batches
        for i in tqdm(
            range(0, len(textos_validos), batch_size),
            desc="Generando embeddings",
            disable=not show_progress
        ):
            batch = textos_validos[i:i + batch_size]
            
            batch_embeddings = self.model.encode(
                batch,
                convert_to_numpy=True,
                normalize_embeddings=normalize,
                show_progress_bar=False,
                batch_size=batch_size
            )
            
            embeddings.extend(batch_embeddings)
        
        logger.info(f"✅ {len(embeddings)} embeddings generados")
        
        return embeddings
    
    def cosine_similarity(
        self,
        vec1: np.ndarray,
        vec2: np.ndarray
    ) -> float:
        """
        Calcula similitud coseno entre dos vectores.
        
        Formula: cos(θ) = (A · B) / (||A|| × ||B||)
        
        Args:
            vec1: Primer vector
            vec2: Segundo vector
        
        Returns:
            Similitud coseno (rango: -1 a 1)
            - 1.0: Vectores idénticos
            - 0.0: Vectores perpendiculares (no relacionados)
            - -1.0: Vectores opuestos
        
        Example:
            >>> emb1 = generator.embed_text("QuickSort")
            >>> emb2 = generator.embed_text("MergeSort")
            >>> sim = generator.cosine_similarity(emb1, emb2)
            >>> print(f"Similitud: {sim:.3f}")
        """
        # Si ya están normalizados, el producto punto es la similitud
        if np.allclose(np.linalg.norm(vec1), 1.0) and \
           np.allclose(np.linalg.norm(vec2), 1.0):
            return float(np.dot(vec1, vec2))
        
        # Si no, calcular explícitamente
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def most_similar(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: List[np.ndarray],
        top_k: int = 5
    ) -> List[tuple]:
        """
        Encuentra los embeddings más similares a una query.
        
        Args:
            query_embedding: Embedding de la query
            candidate_embeddings: Lista de embeddings candidatos
            top_k: Número de resultados a retornar
        
        Returns:
            Lista de tuplas (índice, similitud) ordenadas por similitud
        
        Example:
            >>> query = generator.embed_text("algoritmo rápido")
            >>> docs = generator.embed_batch(["QuickSort", "BubbleSort"])
            >>> results = generator.most_similar(query, docs, top_k=1)
            >>> print(results)
            [(0, 0.85)]  # QuickSort es más similar
        """
        similitudes = []
        
        for idx, candidate in enumerate(candidate_embeddings):
            sim = self.cosine_similarity(query_embedding, candidate)
            similitudes.append((idx, sim))
        
        # Ordenar por similitud (descendente)
        similitudes.sort(key=lambda x: x[1], reverse=True)
        
        return similitudes[:top_k]
    
    def get_info(self) -> dict:
        """
        Retorna información sobre el modelo cargado.
        
        Returns:
            Diccionario con metadata del modelo
        """
        return {
            'model_name': self.model_name,
            'dimension': self.dimension,
            'device': str(self.device),
            'max_seq_length': self.model.max_seq_length,
        }


# ============================================
# Funciones de utilidad
# ============================================

def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calcula distancia euclidiana entre dos vectores.
    
    Menos usado que cosine similarity en NLP, pero útil para algunos casos.
    
    Args:
        vec1: Primer vector
        vec2: Segundo vector
    
    Returns:
        Distancia euclidiana (0 = idénticos, mayor = más diferentes)
    """
    return float(np.linalg.norm(vec1 - vec2))


def manhattan_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calcula distancia Manhattan (L1) entre dos vectores.
    
    Args:
        vec1: Primer vector
        vec2: Segundo vector
    
    Returns:
        Distancia Manhattan
    """
    return float(np.sum(np.abs(vec1 - vec2)))


# ============================================
# Script de prueba
# ============================================

if __name__ == "__main__":
    """
    Script de prueba del módulo de embeddings.
    
    Ejecutar con:
        python src/embeddings.py
    """
    
    print("🧪 Probando módulo de embeddings...\n")
    
    # Crear generador
    generator = EmbeddingGenerator()
    
    # Probar con textos simples
    textos = [
        "QuickSort es un algoritmo eficiente",
        "MergeSort también es rápido",
        "BubbleSort es lento",
        "Me gusta el surf"
    ]
    
    print(f"📝 Textos de prueba: {len(textos)}")
    for i, t in enumerate(textos):
        print(f"   {i+1}. {t}")
    
    # Generar embeddings
    print("\n🧮 Generando embeddings...")
    embeddings = generator.embed_batch(textos)
    
    # Mostrar dimensiones
    print(f"✅ Embeddings generados: {len(embeddings)}")
    print(f"   Dimensión: {embeddings[0].shape}")
    
    # Calcular similitudes
    print("\n📊 Matriz de similitudes:")
    print("     ", " ".join([f"T{i+1}" for i in range(len(textos))]))
    
    for i, emb_i in enumerate(embeddings):
        similitudes = []
        for emb_j in embeddings:
            sim = generator.cosine_similarity(emb_i, emb_j)
            similitudes.append(f"{sim:.2f}")
        
        print(f"  T{i+1}: {' '.join(similitudes)}")
    
    # Búsqueda
    print("\n🔍 Probando búsqueda semántica:")
    query = "algoritmo de ordenamiento rápido"
    query_emb = generator.embed_text(query)
    
    resultados = generator.most_similar(query_emb, embeddings, top_k=3)
    
    print(f"   Query: '{query}'")
    print(f"   Top 3 resultados:")
    for idx, sim in resultados:
        print(f"     {sim:.3f} - {textos[idx]}")
    
    # Info del modelo
    print("\n📋 Información del modelo:")
    info = generator.get_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Pruebas completadas!")