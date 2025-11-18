# 🧠 Obsidian RAG System

> **Sistema RAG que convierte mi Zettelkasten en un asistente de estudio inteligente**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-en%20desarrollo-orange.svg)]()

## 🎯 ¿Qué es esto?

Un sistema de **Retrieval-Augmented Generation (RAG)** que permite consultar mi base de conocimiento personal (notas en Obsidian) usando inteligencia artificial. 

En lugar de que Claude responda con conocimiento general de internet, este sistema le permite acceder a **mis notas específicas**, mis ejemplos, y mis conexiones entre conceptos.

### Problema que resuelve

Como estudiante de Data Science, tomo muchas notas usando el método Zettelkasten en Obsidian. El problema es que:
- ❌ Buscar manualmente entre cientos de notas es lento
- ❌ Olvido conexiones entre conceptos de diferentes asignaturas
- ❌ No aprovecho todo el conocimiento que he documentado

**Con RAG:**
- ✅ Búsqueda semántica instantánea en todas mis notas
- ✅ Claude responde basándose en MI conocimiento
- ✅ Descubro conexiones automáticamente entre temas

---

## 🏗️ Arquitectura (Objetivo final)

# 🧠 Obsidian RAG System

> **Sistema RAG que convierte mi Zettelkasten en un asistente de estudio inteligente**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-en%20desarrollo-orange.svg)]()

## 🎯 ¿Qué es esto?

Un sistema de **Retrieval-Augmented Generation (RAG)** que permite consultar mi base de conocimiento personal (notas en Obsidian) usando inteligencia artificial. 

En lugar de que Claude responda con conocimiento general de internet, este sistema le permite acceder a **mis notas específicas**, mis ejemplos, y mis conexiones entre conceptos.

### Problema que resuelve

Como estudiante de Data Science, tomo muchas notas usando el método Zettelkasten en Obsidian. El problema es que:
- ❌ Buscar manualmente entre cientos de notas es lento
- ❌ Olvido conexiones entre conceptos de diferentes asignaturas
- ❌ No aprovecho todo el conocimiento que he documentado

**Con RAG:**
- ✅ Búsqueda semántica instantánea en todas mis notas
- ✅ Claude responde basándose en MI conocimiento
- ✅ Descubro conexiones automáticamente entre temas

---

## ✨ Features (Roadmap)

- [x] Documentación de fundamentos RAG
- [ ] Parser de notas Markdown de Obsidian
- [ ] Sistema de embeddings con Sentence Transformers
- [ ] Vector database con ChromaDB
- [ ] Integración con Claude API
- [ ] Extracción automática de flashcards
- [ ] Análisis de conexiones entre notas
- [ ] REST API con FastAPI
- [ ] Dockerización del sistema
- [ ] Web UI (Streamlit)

---

## 🏗️ Arquitectura (Objetivo final)
```
┌─────────────────────────────────────────────┐
│           OBSIDIAN RAG SYSTEM               │
├─────────────────────────────────────────────┤
│                                             │
│  📝 Obsidian Vault                          │
│      └─ Notas en Markdown                   │
│      └─ Flashcards                          │
│      └─ Wikilinks                           │
│           ↓                                 │
│  🔍 Document Loader                         │
│      └─ Parser de .md                       │
│      └─ Extracción de metadata             │
│           ↓                                 │
│  🧮 Embedding Generator                     │
│      └─ Sentence Transformers               │
│      └─ Vectores de 384 dimensiones        │
│           ↓                                 │
│  💾 ChromaDB (Vector Database)              │
│      └─ Almacenamiento de vectores         │
│      └─ Búsqueda por similitud             │
│           ↓                                 │
│  🔎 Retriever                               │
│      └─ Top-K documentos relevantes        │
│      └─ Cosine similarity                  │
│           ↓                                 │
│  🤖 Claude API                              │
│      └─ Generación de respuestas           │
│      └─ Context-aware                      │
│           ↓                                 │
│  💬 Usuario                                 │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clonar e Instalar

```bash
# Clonar repositorio
git clone https://github.com/GabrielFersPin/obsidian-rag-system.git
cd obsidian-rag-system

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python scripts/check_dependencies.py
```

### 2. Configurar API Key

```bash
# Obtén tu API key en: https://console.anthropic.com/
export ANTHROPIC_API_KEY=sk-ant-api03-...

# O crea un archivo .env
cp .env.example .env
# Edita .env y añade tu API key
```

### 3. Usar el Sistema

```bash
# Modo interactivo con vault de ejemplo incluido
python scripts/quick_start.py example_vault

# O con tu vault real de Obsidian
python scripts/quick_start.py /path/to/tu/obsidian/vault

# O indexar primero y luego usar
python scripts/index_vault.py example_vault
python scripts/example_rag_usage.py
```

> **Nota**: Incluimos un `example_vault/` con 5 notas de ejemplo (QuickSort, MergeSort, Docker, RAG, ChromaDB) para que puedas probar el sistema inmediatamente.

Ver [INSTALL.md](INSTALL.md) para instrucciones detalladas de instalación.

---

## 📚 Stack Tecnológico

| Componente | Tecnología | Por qué |
|------------|-----------|---------|
| **Embeddings** | Sentence Transformers | Modelos locales, rápidos, eficientes |
| **Vector DB** | ChromaDB | Simple, local, open-source |
| **LLM** | Claude Sonnet 4 | Context window grande, muy preciso |
| **API** | FastAPI | Rápido, async, auto-documentación |
| **Containerización** | Docker | Reproducibilidad, portabilidad |
| **Notes** | Obsidian Markdown | Mi sistema actual de Zettelkasten |

---

## 📖 Documentación

### Conceptos fundamentales
- [¿Qué es RAG?](docs/conceptos/RAG.md) - Fundamentos teóricos
- [Embeddings explicados](docs/conceptos/embeddings.md) - Cómo funciona la vectorización
- [Vector Databases](docs/conceptos/vector-db.md) - Almacenamiento y búsqueda

### Guías de implementación
- [Parser de Obsidian](docs/guias/obsidian-parser.md) - Leer archivos .md
- [Sistema de búsqueda](docs/guias/retrieval.md) - Búsqueda semántica
- [Integración con Claude](docs/guias/claude-integration.md) - API de Anthropic

### Casos de uso
- [Estudiar para exámenes](docs/casos-uso/estudiar.md)
- [Conectar conceptos](docs/casos-uso/conexiones.md)
- [Generar flashcards](docs/casos-uso/flashcards.md)

---

## 🧪 Testing
```bash
# Ejecutar tests
pytest tests/ -v

# Con coverage
pytest tests/ --cov=src --cov-report=html

# Solo tests específicos
pytest tests/test_embeddings.py
```

---

## 📁 Estructura del Proyecto
```
obsidian-rag-system/
├── .devcontainer/          # Configuración de Codespaces
│   ├── devcontainer.json
│   └── docker-compose.yml
│
├── docker/                 # Dockerfiles
│   ├── Dockerfile.rag-api
│   ├── Dockerfile.embeddings
│   └── Dockerfile.jupyter
│
├── src/                    # Código fuente
│   ├── __init__.py
│   ├── obsidian_loader.py  # Parser de notas
│   ├── embeddings.py       # Generación de vectores
│   ├── vectorstore.py      # ChromaDB wrapper
│   ├── retriever.py        # Búsqueda semántica
│   ├── claude_client.py    # Cliente de Anthropic
│   ├── rag_chain.py        # Pipeline completo
│   └── api.py              # FastAPI endpoints
│
├── tests/                  # Tests unitarios
│   ├── __init__.py
│   ├── test_loader.py
│   ├── test_embeddings.py
│   ├── test_vectorstore.py
│   └── test_rag.py
│
├── notebooks/              # Jupyter notebooks
│   ├── 01_exploracion.ipynb
│   ├── 02_embeddings_test.ipynb
│   ├── 03_rag_pipeline.ipynb
│   └── 04_analisis.ipynb
│
├── docs/                   # Documentación
│   ├── conceptos/
│   ├── guias/
│   └── casos-uso/
│
├── scripts/                # Scripts de utilidad
│   ├── index_vault.py      # Indexar vault
│   ├── update_embeddings.py
│   └── generate_flashcards.py
│
├── data/                   # Datos (gitignored)
│   └── vault/              # Symlink a Obsidian
│
├── chroma_db/              # Vector database (gitignored)
├── models/                 # Cache de modelos (gitignored)
│
├── .env.example            # Template de variables
├── .gitignore
├── docker-compose.yml
├── requirements.txt
├── README.md
└── LICENSE
```

---

## 🎓 Aprendizajes

Este proyecto es también una experiencia de aprendizaje. Algunos conceptos clave:

- **RAG Architecture**: Cómo combinar retrieval + generation
- **Embeddings**: Representación vectorial de texto
- **Similarity Search**: Búsqueda por similitud semántica
- **Vector Databases**: ChromaDB y operaciones vectoriales
- **LLM Integration**: API de Claude y prompt engineering
- **Docker Compose**: Arquitectura multi-container
- **FastAPI**: APIs REST asíncronas

Cada componente está documentado con explicaciones detalladas para poder explicarlo en entrevistas técnicas.

---

## 🗓️ Desarrollo

### Fase actual: **Fundamentos** 🌱

**En progreso:**
- [x] Investigación y documentación de RAG
- [x] Estructura del repositorio
- [ ] Sistema de embeddings
- [ ] Parser de Obsidian

**Siguiente:**
- [ ] Vector database setup
- [ ] Primera consulta RAG funcional
- [ ] Integración con Claude

---

## 🤝 Contribuir

Este es un proyecto personal de aprendizaje, pero sugerencias son bienvenidas:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -m 'Añade X'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

---

## 📊 Casos de uso reales

### 1. Preparar examen de Algoritmos
```bash
curl -X POST http://localhost:8001/query \
  -d '{
    "question": "Resume los conceptos clave de ordenamiento",
    "deck_filter": "Algoritmos",
    "n_results": 5
  }'
```

### 2. Conectar conceptos entre asignaturas
```bash
curl -X POST http://localhost:8001/query \
  -d '{
    "question": "¿Cómo se relaciona Docker con arquitectura de computadores?",
    "n_results": 10
  }'
```

### 3. Generar flashcards automáticamente
```bash
curl -X POST http://localhost:8001/flashcards/generate \
  -d '{"note_path": "data/vault/Algoritmos/QuickSort.md"}'
```

---

## 🙏 Inspiración & Referencias

- [LangChain Documentation](https://python.langchain.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- Método Zettelkasten de Niklas Luhmann
- Mi propia frustración buscando en 200+ notas manualmente

---

## 📄 License

MIT License - Siéntete libre de usar, modificar y aprender de este código.

---

## 📧 Contacto

**Gabriel** 
- Portfolio: [tu-portfolio]
- LinkedIn: [tu-linkedin]
- GitHub: [@tu-usuario](https://github.com/tu-usuario)

---

## ⭐ Progreso
```
███████░░░░░░░░░░░░░░░░░░░ 25% - Fundamentos completados
```

**Última actualización**: Enero 2025

---

> *"El conocimiento que no se puede explicar es conocimiento que no se comprende"*
> 
> Este proyecto no solo automatiza mi segundo cerebro, sino que me obliga a entender profundamente cada componente para poder explicarlo.
