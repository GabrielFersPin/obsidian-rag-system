---
cards-deck: Data Science
status: completo
tipo_nota: concepto
created: 2025-01-15
---

# RAG (Retrieval-Augmented Generation)

RAG es una técnica que combina **recuperación de información** con **generación de lenguaje** para crear sistemas de IA más precisos y actualizados.

## Concepto

En lugar de depender solo del conocimiento "memorizado" durante el entrenamiento, RAG:

1. **Recupera** información relevante de una base de datos externa
2. **Aumenta** el prompt con esa información
3. **Genera** una respuesta basada en el contexto recuperado

## Arquitectura

```
Query → Embeddings → Vector Search → Top-K Docs → LLM → Response
```

### Componentes

1. **Vector Database**: Almacena embeddings de documentos
2. **Embedding Model**: Convierte texto en vectores (ej: Sentence Transformers)
3. **Retriever**: Busca documentos similares usando cosine similarity
4. **LLM**: Genera respuesta usando contexto recuperado (ej: Claude, GPT-4)

## Ventajas

- ✅ Respuestas basadas en información actual y específica
- ✅ Reduce alucinaciones del LLM
- ✅ Permite actualizar conocimiento sin reentrenar
- ✅ Cita fuentes específicas
- ✅ Funciona con conocimiento privado/propietario

## Desventajas

- ❌ Latencia adicional por la búsqueda
- ❌ Dependiente de la calidad del retrieval
- ❌ Costo de mantener vector database

## Implementación Típica

```python
# 1. Indexar documentos
embeddings = embedding_model.encode(documents)
vector_store.add(embeddings)

# 2. Query
query_embedding = embedding_model.encode(query)
relevant_docs = vector_store.search(query_embedding, top_k=5)

# 3. Generar respuesta
context = "\n".join(relevant_docs)
prompt = f"Context: {context}\n\nQuestion: {query}"
response = llm.generate(prompt)
```

## Casos de Uso

- Sistemas de Q&A sobre documentación
- Chatbots con conocimiento específico de empresa
- Asistentes de investigación
- Segunda cerebros digitales (como este proyecto!)

## Stack Tecnológico Común

- **Embeddings**: Sentence Transformers, OpenAI embeddings
- **Vector DB**: [[ChromaDB]], Pinecone, Weaviate, FAISS
- **LLMs**: Claude, GPT-4, Llama
- **Frameworks**: LangChain, LlamaIndex

## Relaciones

- Usa [[Vector Databases]] para almacenar embeddings
- Complementa [[LLMs]] con información actualizada
- Base de muchos [[Chatbots]] modernos
