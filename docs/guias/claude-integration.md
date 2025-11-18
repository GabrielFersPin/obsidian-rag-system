# Guía de Integración con Claude

Esta guía explica cómo usar el pipeline completo de integración con Claude para el sistema RAG de Obsidian.

## 📋 Requisitos Previos

1. **API Key de Anthropic**: Obtén tu API key en [console.anthropic.com](https://console.anthropic.com/)
2. **Python 3.10+**: Verifica con `python --version`
3. **Dependencias instaladas**: `pip install -r requirements.txt`
4. **Vault de Obsidian**: Path a tu vault con notas en formato Markdown

## 🚀 Configuración Inicial

### 1. Configurar Variables de Entorno

Copia el archivo de ejemplo y configura tus variables:

```bash
cp .env.example .env
```

Edita `.env` y configura:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
VAULT_PATH=/path/to/your/obsidian/vault
```

### 2. Indexar tu Vault

Antes de hacer queries, debes indexar tus notas:

```bash
python scripts/index_vault.py /path/to/vault
```

Opciones disponibles:
- `--force`: Reindexar desde cero
- `--collection`: Nombre de la collection (default: obsidian_notes)
- `--batch-size`: Tamaño de batch para embeddings (default: 32)

Ejemplo:
```bash
python scripts/index_vault.py ~/Documents/ObsidianVault --force --batch-size 64
```

## 💬 Uso del Sistema RAG

### Quick Start Interactivo

La forma más simple de empezar:

```bash
python scripts/quick_start.py /path/to/vault
```

Esto inicia un modo interactivo donde puedes hacer preguntas directamente.

### Uso Programático

#### Ejemplo Básico

```python
from src.rag_chain import ObsidianRAG

# Inicializar sistema
rag = ObsidianRAG(
    vault_path="/path/to/vault",
    collection_name="mis_notas",
    claude_model="sonnet"
)

# Indexar vault (solo la primera vez)
rag.index_vault()

# Hacer una query
result = rag.query(
    question="¿Qué es QuickSort?",
    top_k=5
)

print(result.answer)
print(result.format_sources())
```

#### Query con Filtros

```python
# Filtrar por deck específico
result = rag.query(
    question="Explícame algoritmos de ordenamiento",
    top_k=3,
    deck_filter="Algoritmos"
)

# Limitar contexto
result = rag.query(
    question="¿Qué es Docker?",
    top_k=5,
    max_context_chars=2000
)

# Ajustar temperatura de Claude
result = rag.query(
    question="Dame ejemplos creativos de uso de QuickSort",
    claude_temperature=0.9  # Más creativo
)
```

#### Modo Conversacional

```python
# Primera pregunta (recupera contexto)
response1 = rag.chat(
    "¿Qué algoritmos de ordenamiento tengo documentados?",
    top_k=3
)
print(response1.answer)

# Pregunta de seguimiento (usa historial)
response2 = rag.chat(
    "¿Cuál es el más eficiente?",
    retrieve_context=False  # No necesita nuevo contexto
)
print(response2.answer)

# Limpiar historial cuando cambies de tema
rag.clear_conversation()
```

#### Encontrar Notas Relacionadas

```python
# Encontrar notas relacionadas a una nota específica
related = rag.find_related_notes(
    note_name="QuickSort",
    top_k=5
)

for note in related:
    file_name = note.metadata['file_name']
    deck = note.metadata['deck']
    score = note.score
    print(f"{file_name} (Deck: {deck}, Relevancia: {score:.3f})")
```

## 🔧 Componentes del Pipeline

### 1. ObsidianLoader

Carga y parsea notas de Obsidian:

```python
from src.obsidian_loader import ObsidianLoader

loader = ObsidianLoader(vault_path="/path/to/vault")
notes = loader.load_notes()

# Estadísticas del vault
stats = loader.get_vault_stats()
print(f"Total notas: {stats['total_notes']}")
print(f"Por deck: {stats['by_deck']}")
```

### 2. EmbeddingGenerator

Genera embeddings semánticos:

```python
from src.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Embedding único
embedding = generator.embed_text("QuickSort es eficiente")

# Batch de embeddings
embeddings = generator.embed_batch(
    ["QuickSort", "MergeSort", "BubbleSort"],
    batch_size=32
)
```

### 3. ObsidianVectorStore

Gestiona el almacenamiento vectorial con ChromaDB:

```python
from src.vectorstore import ObsidianVectorStore

store = ObsidianVectorStore(persist_directory="./chroma_db")

# Crear collection
store.create_collection("mis_notas")

# Añadir notas
store.add_notes(
    collection_name="mis_notas",
    notes=notes,
    embeddings=embeddings
)

# Buscar
results = store.search(
    collection_name="mis_notas",
    query_embedding=query_vector,
    n_results=5,
    where={"deck": "Algoritmos"}
)
```

### 4. ObsidianRetriever

Recuperación semántica:

```python
from src.retriever import ObsidianRetriever

retriever = ObsidianRetriever(
    embedding_generator=generator,
    vector_store=store,
    collection_name="mis_notas"
)

# Recuperar documentos
results = retriever.retrieve(
    query="algoritmo de ordenamiento",
    top_k=5,
    deck_filter="Algoritmos"
)

# Contexto para LLM
context = retriever.get_context_for_llm(
    query="¿Qué es QuickSort?",
    top_k=3,
    max_chars=2000
)
```

### 5. ClaudeClient

Cliente para la API de Anthropic:

```python
from src.claude_client import ClaudeClient

client = ClaudeClient(
    api_key="sk-ant-...",
    model="sonnet",  # haiku, sonnet, opus
    max_tokens=2048,
    temperature=0.7
)

# Respuesta RAG
response = client.generate_rag_response(
    query="¿Qué es QuickSort?",
    context="QuickSort es un algoritmo..."
)

print(response.content)
print(f"Tokens: {response.tokens_input + response.tokens_output}")

# Resumir notas
summary = client.summarize_notes(
    notes_content="...",
    style="bullet_points"
)

# Explicar concepto
explanation = client.explain_concept(
    concept="QuickSort",
    context="...",
    depth="deep"
)
```

## 📊 Estadísticas y Monitoring

### Obtener Estadísticas del Sistema

```python
stats = rag.get_stats()

print(f"Total notas: {stats['total_notes']}")
print(f"Por deck: {stats['notes_by_deck']}")
print(f"Modelo embeddings: {stats['embedding_model']}")
print(f"Dimensión: {stats['embedding_dimension']}")
print(f"Modelo Claude: {stats['claude_model']}")
```

### Exportar Estadísticas

```python
rag.export_stats("rag_stats.json")
```

### Analizar Resultados de Query

```python
result = rag.query("¿Qué es QuickSort?")

print(f"Query: {result.query}")
print(f"Tokens usados: {result.tokens_used}")
print(f"Tiempo retrieval: {result.retrieval_time:.2f}s")
print(f"Tiempo generación: {result.generation_time:.2f}s")
print(f"Documentos recuperados: {len(result.retrieved_docs)}")

# Ver fuentes
for doc in result.retrieved_docs:
    print(f"  - {doc.metadata['file_name']} (Score: {doc.score:.3f})")
```

## 🎯 Casos de Uso

### Estudiar para Examen

```python
# Obtener resumen de un tema
result = rag.query(
    "Resume los conceptos clave de algoritmos de ordenamiento",
    deck_filter="Algoritmos",
    top_k=10
)

print(result.answer)
```

### Conectar Conceptos

```python
# Encontrar conexiones entre temas
result = rag.query(
    "¿Cómo se relaciona Docker con arquitectura de computadores?",
    top_k=10
)

print(result.answer)
```

### Generar Explicaciones

```python
# Explicación profunda de un concepto
result = rag.query(
    "Explica QuickSort con ejemplos y casos de uso",
    deck_filter="Algoritmos",
    top_k=5,
    claude_temperature=0.5  # Más determinista
)

print(result.answer)
```

## ⚙️ Configuración Avanzada

### Modelos de Embeddings

Opciones recomendadas:

1. **all-MiniLM-L6-v2** (default)
   - Rápido
   - 384 dimensiones
   - Bueno para español e inglés

2. **all-mpnet-base-v2**
   - Mejor calidad
   - 768 dimensiones
   - Más lento

3. **paraphrase-multilingual-MiniLM-L12-v2**
   - Optimizado para multilingüe
   - 384 dimensiones
   - Excelente para español

```python
rag = ObsidianRAG(
    vault_path="/path/to/vault",
    embedding_model="sentence-transformers/all-mpnet-base-v2"
)
```

### Modelos de Claude

- **haiku**: Más rápido y económico (ideal para desarrollo)
- **sonnet**: Balance entre velocidad y calidad (recomendado)
- **opus**: Mejor calidad pero más lento y costoso

```python
rag = ObsidianRAG(
    vault_path="/path/to/vault",
    claude_model="opus"  # Para máxima calidad
)
```

## 🐛 Troubleshooting

### Error: "ANTHROPIC_API_KEY no configurada"

Asegúrate de tener tu API key configurada:

```bash
export ANTHROPIC_API_KEY=sk-ant-api03-...
```

O en `.env`:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Error: "Collection no existe"

Indexa tu vault primero:

```bash
python scripts/index_vault.py /path/to/vault
```

### Respuestas de baja calidad

1. Aumenta `top_k` para incluir más contexto
2. Ajusta `max_context_chars` para dar más información
3. Prueba con modelo Claude superior (sonnet/opus)
4. Verifica que tus notas están bien escritas y estructuradas

### Lentitud en queries

1. Usa `haiku` para desarrollo
2. Reduce `top_k`
3. Limita `max_context_chars`
4. Considera usar un modelo de embeddings más rápido

## 📚 Ejemplos Completos

Ver `scripts/example_rag_usage.py` para un ejemplo completo con todos los casos de uso.

## 🔗 Referencias

- [Documentación de Anthropic](https://docs.anthropic.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Obsidian](https://obsidian.md/)

## 💡 Tips y Mejores Prácticas

1. **Indexación**: Reindexa periódicamente cuando agregues muchas notas nuevas
2. **Decks**: Usa decks organizados para filtrado eficiente
3. **Temperatura**: Usa 0.5-0.7 para respuestas académicas, 0.8-1.0 para creatividad
4. **Contexto**: Más contexto = mejores respuestas pero más tokens
5. **Historial**: Limpia el historial cuando cambies de tema completamente
