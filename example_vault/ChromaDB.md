---
cards-deck: Data Science
status: completo
tipo_nota: herramienta
created: 2025-01-15
---

# ChromaDB

ChromaDB es una **base de datos vectorial** open-source diseñada para aplicaciones de IA y embeddings.

## Qué es

ChromaDB almacena embeddings (vectores) y permite búsqueda por similitud semántica.

## Características

- **Open Source**: Completamente gratis
- **Local-First**: Puede ejecutarse completamente local
- **Simple**: API muy fácil de usar
- **Rápido**: Optimizado para búsqueda de similaridad
- **Persistencia**: Guarda datos en disco

## Instalación

```bash
pip install chromadb
```

## Uso Básico

```python
import chromadb

# Cliente
client = chromadb.Client()

# Crear colección
collection = client.create_collection("mi_coleccion")

# Añadir documentos
collection.add(
    embeddings=[[1.1, 2.3, 3.2], [4.5, 6.9, 4.4]],
    documents=["Documento 1", "Documento 2"],
    ids=["id1", "id2"]
)

# Buscar
results = collection.query(
    query_embeddings=[[1.0, 2.0, 3.0]],
    n_results=2
)
```

## Conceptos

### Collection
Grupo de documentos con sus embeddings. Cada collection es independiente.

### Embedding
Vector numérico que representa el significado semántico de un documento.

### Metadata
Información adicional asociada a cada documento (ej: fecha, autor, categoría).

### Query
Búsqueda por similitud usando un embedding de consulta.

## Ventajas

- Muy fácil de usar vs otras vector DBs
- No requiere servidor (en modo local)
- Perfecto para prototipado
- Filtra por metadata

## Comparación con Alternativas

| DB | Complejidad | Costo | Escalabilidad |
|----|-------------|-------|---------------|
| **ChromaDB** | Baja | Gratis | Mediana |
| Pinecone | Media | Pago | Alta |
| Weaviate | Alta | Gratis/Pago | Alta |
| FAISS | Media | Gratis | Alta |

## Casos de Uso

- Sistemas [[RAG]] (Retrieval-Augmented Generation)
- Búsqueda semántica
- Recomendaciones
- Clasificación por similitud

## Uso en Este Proyecto

Este sistema RAG usa ChromaDB para:
1. Almacenar embeddings de notas de Obsidian
2. Buscar notas relevantes para una query
3. Filtrar por deck/metadata
4. Encontrar notas relacionadas

```python
from src.vectorstore import ObsidianVectorStore

store = ObsidianVectorStore(persist_directory="./chroma_db")
store.create_collection("mis_notas")
```

## Relaciones

- Usado en sistemas [[RAG]]
- Almacena salidas de [[Sentence Transformers]]
- Alternativa local a Pinecone
