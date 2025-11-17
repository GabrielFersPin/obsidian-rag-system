# CLAUDE.md - AI Assistant Guide for Obsidian RAG System

> **Last Updated**: 2025-01-17
> **Project Status**: Early Development (Foundational Phase)

This document provides comprehensive guidance for AI assistants (like Claude Code) working on the Obsidian RAG System. It covers codebase structure, development workflows, conventions, and best practices.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Core Modules](#core-modules)
4. [Development Workflow](#development-workflow)
5. [Code Conventions](#code-conventions)
6. [Testing Strategy](#testing-strategy)
7. [Dependencies & Environment](#dependencies--environment)
8. [Key Patterns & Architecture](#key-patterns--architecture)
9. [Common Tasks](#common-tasks)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

### What is this?
A **Retrieval-Augmented Generation (RAG)** system that converts an Obsidian vault (Zettelkasten notes) into an intelligent study assistant. The system enables semantic search across personal notes and allows Claude to answer questions based on the user's specific knowledge base.

### Tech Stack
- **Language**: Python 3.10+
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Vector Database**: ChromaDB
- **LLM**: Claude Sonnet 4 (via Anthropic API)
- **Testing**: pytest + pytest-cov

### Current Development Phase
- ✅ **Complete**: Repository structure, ObsidianLoader, VectorStore, Embeddings modules
- 🚧 **In Progress**: Testing framework, integration pipeline
- 📋 **Planned**: Retriever, Claude client, RAG chain, FastAPI, Docker, Web UI

### Primary User
- Spanish-speaking Data Science student
- Uses Zettelkasten method in Obsidian
- Focuses on learning and explaining concepts for technical interviews

---

## 📁 Codebase Structure

```
obsidian-rag-system/
├── src/                           # Source code modules
│   ├── __init__.py               # Package initialization (minimal)
│   ├── obsidian_loader.py        # Parse and load Obsidian notes
│   ├── embeddings.py             # Generate text embeddings
│   ├── vectorstore.py            # ChromaDB vector database wrapper
│   ├── retriever.py              # (Planned) Semantic search & retrieval
│   ├── claude_client.py          # (Planned) Anthropic API client
│   ├── rag_chain.py              # (Planned) Full RAG pipeline
│   └── api.py                    # (Planned) FastAPI endpoints
│
├── tests/                        # Test suite
│   ├── __init__.py              # Empty test package init
│   ├── test_loader.py           # (Planned) Tests for ObsidianLoader
│   ├── test_embeddings.py       # (Planned) Tests for embeddings
│   ├── test_vectorstore.py      # (Planned) Tests for vector store
│   └── test_rag.py              # (Planned) Integration tests
│
├── notebooks/                    # (Planned) Jupyter notebooks for exploration
├── docs/                         # (Planned) Detailed documentation
├── scripts/                      # (Planned) Utility scripts
├── data/vault/                   # (gitignored) Obsidian vault symlink
├── chroma_db/                    # (gitignored) Persisted vector database
├── models/                       # (gitignored) Cached ML models
│
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── README.md                     # User-facing documentation (Spanish)
├── LICENSE                       # MIT License
└── CLAUDE.md                     # This file
```

### File Purpose Reference

| File | Purpose | Status |
|------|---------|--------|
| `src/obsidian_loader.py` | Parse .md files, extract frontmatter, wikilinks, clean content | ✅ Complete |
| `src/embeddings.py` | Generate vector embeddings using Sentence Transformers | ✅ Complete |
| `src/vectorstore.py` | CRUD operations for ChromaDB vector database | ✅ Complete |
| `src/retriever.py` | Semantic search and document retrieval | 📋 Planned |
| `src/claude_client.py` | Interact with Anthropic Claude API | 📋 Planned |
| `src/rag_chain.py` | Orchestrate full RAG pipeline (retrieve + generate) | 📋 Planned |
| `src/api.py` | FastAPI REST endpoints | 📋 Planned |

---

## 🔧 Core Modules

### 1. ObsidianLoader (`src/obsidian_loader.py`)

**Purpose**: Load and parse Obsidian Markdown notes.

**Key Classes**:
- `ObsidianLoader`: Main loader class

**Key Methods**:
- `__init__(vault_path, ignore_patterns)`: Initialize with vault path
- `load_notes(file_extensions)`: Load all notes from vault
- `_parse_note(file_path)`: Parse individual note
- `_extract_frontmatter(content)`: Extract YAML frontmatter
- `_extract_wikilinks(content)`: Extract `[[wikilinks]]`
- `_extract_title(content)`: Get first H1 heading
- `_clean_content(content)`: Remove markdown syntax for embeddings
- `get_vault_stats()`: Get statistics about the vault

**Utility Functions**:
- `find_orphan_notes(notes)`: Find notes with no links
- `build_link_graph(notes)`: Build graph of note connections

**Note Format Returned**:
```python
{
    'file_name': str,          # Filename without extension
    'file_path': str,          # Full path to file
    'title': str,              # First H1 or filename
    'content': str,            # Cleaned content for embeddings
    'content_raw': str,        # Original markdown content
    'deck': str,               # From frontmatter cards-deck
    'status': str,             # From frontmatter
    'tipo_nota': str,          # From frontmatter (note type)
    'created': str,            # From frontmatter
    'modified': str,           # From frontmatter
    'frontmatter': dict,       # Full frontmatter data
    'wikilinks': List[str],    # List of linked notes
    'num_links': int,          # Count of wikilinks
    'file_size': int,          # File size in bytes
    'last_modified': datetime, # File system modified time
    'last_accessed': datetime  # File system access time
}
```

**Important Patterns**:
- Ignores hidden files, `.obsidian/`, `.trash/`, `template/` folders
- Frontmatter parsing is simple (no YAML library dependency)
- Wikilinks support both `[[Note]]` and `[[Note|Alias]]` syntax
- Content cleaning removes code blocks, comments, callouts, but preserves text

### 2. EmbeddingGenerator (`src/embeddings.py`)

**Purpose**: Convert text to vector embeddings using Sentence Transformers.

**Key Classes**:
- `EmbeddingGenerator`: Main embedding generator

**Key Methods**:
- `__init__(model_name, cache_folder, device)`: Initialize model
- `embed_text(text, normalize)`: Generate embedding for single text
- `embed_batch(texts, batch_size, normalize, show_progress)`: Batch process texts
- `cosine_similarity(vec1, vec2)`: Calculate cosine similarity
- `most_similar(query_embedding, candidate_embeddings, top_k)`: Find most similar vectors
- `get_info()`: Get model metadata

**Utility Functions**:
- `euclidean_distance(vec1, vec2)`: Euclidean distance metric
- `manhattan_distance(vec1, vec2)`: Manhattan (L1) distance metric

**Default Model**: `sentence-transformers/all-MiniLM-L6-v2`
- Dimension: 384
- Fast and efficient
- Good for English and some multilingual support

**Important Patterns**:
- Always normalizes embeddings by default (for cosine similarity)
- Handles empty text gracefully (returns zero vector)
- Batch processing with progress bars using tqdm
- Uses numpy arrays for vector operations
- Auto-detects CUDA/CPU device

### 3. ObsidianVectorStore (`src/vectorstore.py`)

**Purpose**: Manage ChromaDB vector database for note storage and retrieval.

**Key Classes**:
- `ObsidianVectorStore`: ChromaDB wrapper with domain-specific methods

**Key Methods**:
- `__init__(persist_directory, client_settings)`: Initialize ChromaDB client
- `create_collection(name, metadata, get_or_create)`: Create/get collection
- `get_collection(name)`: Retrieve existing collection
- `delete_collection(name)`: Remove collection
- `add_notes(collection_name, notes, embeddings)`: Add notes with embeddings
- `search(collection_name, query_embedding, n_results, where, where_document)`: Semantic search
- `update_note(collection_name, note_id, embedding, metadata, document)`: Update existing note
- `delete_note(collection_name, note_id)`: Delete single note
- `delete_by_filter(collection_name, where)`: Delete notes matching filter
- `get_collection_stats(collection_name)`: Get statistics
- `list_collections()`: List all collections
- `export_collection(collection_name, output_path)`: Backup to JSON
- `get_info()`: Get vector store info

**Utility Functions**:
- `format_search_results(results)`: Format ChromaDB results for display

**Metadata Stored**:
```python
{
    'file_name': str,
    'file_path': str,
    'deck': str,               # Subject/topic
    'has_flashcards': bool,
    'num_flashcards': int,
    'num_links': int,
    'last_modified': str,      # ISO format datetime
    'indexed_at': str,         # ISO format datetime
    'status': str,             # Optional
    'tipo_nota': str,          # Optional
    'created': str             # Optional
}
```

**Important Patterns**:
- Persists to disk automatically (`./chroma_db/` by default)
- Generates UUID for each document
- Supports metadata filtering in searches (e.g., filter by deck)
- Collection caching for performance
- Extensive logging for debugging

---

## 🛠️ Development Workflow

### Git Branch Strategy

**Current Branch**: `claude/claude-md-mi3suu1ityxbawhr-01BiiatXkPcPMahdpRwcTDyR`

**Important Git Rules**:
1. **ALWAYS** develop on branches starting with `claude/` and ending with session ID
2. **NEVER** push to main directly
3. Use descriptive commit messages in English
4. Push with: `git push -u origin <branch-name>`
5. Retry network failures up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

### Commit Message Format

Follow conventional commits:
```
feat: Add semantic search to retriever module
fix: Handle empty text in embedding generator
docs: Update CLAUDE.md with testing guidelines
refactor: Simplify frontmatter parsing logic
test: Add unit tests for ObsidianLoader
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `style`

### Development Process

1. **Before Coding**:
   - Read relevant module(s) to understand current implementation
   - Check existing tests (when available)
   - Review this CLAUDE.md for conventions

2. **While Coding**:
   - Follow existing code style (see Code Conventions)
   - Add docstrings to all functions/classes
   - Include type hints
   - Add logging statements (use `logging` module)
   - Write examples in docstrings

3. **After Coding**:
   - Run tests: `pytest tests/ -v`
   - Check coverage: `pytest tests/ --cov=src --cov-report=html`
   - Update documentation if needed
   - Commit with descriptive message
   - Push to feature branch

---

## 📝 Code Conventions

### Language & Documentation

**Code**: English
**Comments**: Spanish (developer preference) or English
**Docstrings**: Spanish (for consistency with existing code)
**README**: Spanish
**This file (CLAUDE.md)**: English

### Python Style

**Follow PEP 8** with these specifics:

1. **Imports**:
```python
# Standard library
import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Third-party
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb

# Local
from obsidian_loader import ObsidianLoader
```

2. **Type Hints**:
- Always use type hints for function parameters and return values
- Use `Optional[Type]` for nullable values
- Use `List[Type]`, `Dict[str, Type]` instead of `list`, `dict`

3. **Docstrings**:
```python
def example_function(param1: str, param2: int = 5) -> Dict:
    """
    Brief description in Spanish or English.

    Longer explanation if needed...

    Args:
        param1: Description
        param2: Description (default: 5)

    Returns:
        Description of return value

    Raises:
        ValueError: When this happens
        RuntimeError: When that happens

    Example:
        >>> result = example_function("test", 10)
        >>> print(result)
        {'key': 'value'}
    """
    pass
```

4. **Logging**:
```python
import logging

logger = logging.getLogger(__name__)

# Use emojis for visual clarity (existing pattern)
logger.info("✅ Operation successful")
logger.warning("⚠️ Potential issue")
logger.error("❌ Error occurred")
logger.info("📁 Loading file...")
logger.info("🔍 Searching...")
logger.info("🧮 Computing...")
```

Common emojis:
- ✅ Success
- ❌ Error
- ⚠️ Warning
- 📁 File operations
- 🔍 Search
- 🧮 Computation
- 📝 Writing
- 🗑️ Deletion
- 🚀 Initialization
- 📊 Statistics
- 💾 Saving/Export

5. **Constants**:
```python
DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_EMBEDDING_DIM = 384
MAX_RETRY_ATTEMPTS = 4
```

6. **Class Structure**:
```python
class ClassName:
    """Docstring."""

    def __init__(self, param: str):
        """Docstring."""
        self.param = param

    def public_method(self) -> str:
        """Docstring."""
        pass

    def _private_method(self) -> None:
        """Docstring (can be shorter for private methods)."""
        pass
```

7. **Error Handling**:
```python
try:
    # Operation
    result = risky_operation()
except SpecificError as e:
    logger.error(f"❌ Error: {e}")
    raise RuntimeError("Descriptive message") from e
```

### File Organization

Each module should have:
1. Module docstring at top
2. Imports
3. Logger configuration
4. Main classes
5. Utility functions
6. `if __name__ == "__main__":` test script

---

## 🧪 Testing Strategy

### Test Structure

**Location**: `tests/` directory
**Framework**: pytest
**Coverage**: pytest-cov

### Test File Naming

- `test_loader.py` - Tests for `obsidian_loader.py`
- `test_embeddings.py` - Tests for `embeddings.py`
- `test_vectorstore.py` - Tests for `vectorstore.py`
- `test_rag.py` - Integration tests

### Test Organization

```python
"""Tests for obsidian_loader module."""

import pytest
from pathlib import Path
from src.obsidian_loader import ObsidianLoader

class TestObsidianLoader:
    """Test suite for ObsidianLoader class."""

    def test_initialization_valid_path(self):
        """Test loader initializes with valid vault path."""
        # Test implementation
        pass

    def test_initialization_invalid_path(self):
        """Test loader raises error with invalid path."""
        with pytest.raises(ValueError):
            # Test implementation
            pass

def test_utility_function():
    """Test standalone utility function."""
    pass
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_loader.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_loader.py::TestObsidianLoader::test_initialization_valid_path -v
```

### Test Data

- Create test fixtures in `tests/fixtures/` (when needed)
- Use small, focused test cases
- Mock external dependencies (file system, API calls)

### What to Test

1. **Unit Tests**:
   - Class initialization
   - Method return values
   - Error handling
   - Edge cases (empty input, None, invalid data)
   - Data transformations

2. **Integration Tests**:
   - Full RAG pipeline
   - Database persistence
   - End-to-end workflows

3. **Coverage Goals**:
   - Aim for 80%+ coverage on core modules
   - 100% on critical paths (data processing, search)

---

## 🔌 Dependencies & Environment

### Python Version
- **Minimum**: Python 3.10
- **Recommended**: Python 3.11

### Core Dependencies

```python
# LLM & API
anthropic>=0.34.0

# Embeddings & ML
sentence-transformers>=2.2.0
torch>=2.0.0

# Vector Database
chromadb>=0.4.22

# Text Processing
markdown>=3.5.0
tiktoken>=0.5.0

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0
tqdm>=4.66.0
numpy>=1.24.0
pandas>=2.0.0

# Development
jupyter>=1.0.0
ipykernel>=6.25.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
```

### Environment Variables

Create `.env` from `.env.example`:

```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Paths
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
CHROMA_PERSIST_DIR=./chroma_db
MODELS_CACHE_DIR=./models

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000

# API (for future FastAPI)
API_HOST=0.0.0.0
API_PORT=8001

# Development
DEBUG=true
LOG_LEVEL=INFO
```

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import chromadb; import sentence_transformers; print('✅ All dependencies installed')"
```

---

## 🏗️ Key Patterns & Architecture

### RAG Architecture Flow

```
User Query
    ↓
[1. Embedding Generator]
    ↓
Query Vector
    ↓
[2. Vector Store Search] ← ChromaDB
    ↓
Top-K Relevant Notes
    ↓
[3. Context Builder]
    ↓
Prompt with Context
    ↓
[4. Claude API]
    ↓
Generated Answer
```

### Data Flow

1. **Indexing Pipeline** (One-time or periodic):
   ```
   Obsidian Vault (.md files)
        ↓
   [ObsidianLoader] → Parse & Clean
        ↓
   List[Dict] (notes)
        ↓
   [EmbeddingGenerator] → Vectorize
        ↓
   List[np.ndarray] (embeddings)
        ↓
   [VectorStore] → Store
        ↓
   ChromaDB (persisted)
   ```

2. **Query Pipeline** (Per user question):
   ```
   User Question (str)
        ↓
   [EmbeddingGenerator] → Vectorize
        ↓
   Query Vector (np.ndarray)
        ↓
   [VectorStore.search()] → Find similar
        ↓
   Top-K Notes (with metadata)
        ↓
   [Retriever] → Format context (PLANNED)
        ↓
   [ClaudeClient] → Generate answer (PLANNED)
        ↓
   Answer + Sources
   ```

### Design Patterns Used

1. **Facade Pattern**: Each module (`ObsidianLoader`, `EmbeddingGenerator`, `ObsidianVectorStore`) provides a high-level interface hiding complexity

2. **Strategy Pattern**: Different embedding models can be swapped via `model_name` parameter

3. **Builder Pattern**: `ObsidianLoader._parse_note()` builds complex note dictionaries step-by-step

4. **Singleton-like**: ChromaDB client is initialized once per `ObsidianVectorStore` instance

### Key Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| **ChromaDB over FAISS/Pinecone** | Local-first, no API costs, persistent, simple API |
| **Sentence Transformers over OpenAI embeddings** | Local inference, no API costs, privacy, faster for batch |
| **all-MiniLM-L6-v2 model** | Good balance: fast (384 dim) vs quality, small size (~90MB) |
| **Simple YAML parsing (no PyYAML for frontmatter)** | Reduce dependencies, Obsidian frontmatter is simple |
| **Spanish documentation in code** | Developer is Spanish-speaking, aids learning |
| **Logging with emojis** | Visual clarity in terminal, easy to scan |

---

## 🔨 Common Tasks

### 1. Adding a New Module

```bash
# Create module file
touch src/new_module.py

# Template
cat > src/new_module.py << 'EOF'
"""
Brief description of module.

Longer explanation...

Autor: Gabriel
Fecha: 2025-01
"""

import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewClass:
    """Docstring."""

    def __init__(self, param: str):
        """Initialize."""
        self.param = param
        logger.info("✅ NewClass initialized")

    def method(self) -> str:
        """Docstring."""
        pass


if __name__ == "__main__":
    """Test script."""
    print("🧪 Testing new_module...")
    instance = NewClass("test")
    print("✅ Tests passed!")
EOF

# Create test file
touch tests/test_new_module.py
```

### 2. Indexing a New Vault

```python
from src.obsidian_loader import ObsidianLoader
from src.embeddings import EmbeddingGenerator
from src.vectorstore import ObsidianVectorStore

# Load notes
loader = ObsidianLoader("/path/to/vault")
notes = loader.load_notes()

# Generate embeddings
generator = EmbeddingGenerator()
contents = [note['content'] for note in notes]
embeddings = generator.embed_batch(contents)

# Store in vector database
store = ObsidianVectorStore()
store.create_collection("my_notes")
store.add_notes("my_notes", notes, embeddings)

print(f"✅ Indexed {len(notes)} notes")
```

### 3. Semantic Search

```python
from src.embeddings import EmbeddingGenerator
from src.vectorstore import ObsidianVectorStore, format_search_results

# Initialize
generator = EmbeddingGenerator()
store = ObsidianVectorStore()

# Search
query = "algoritmo de ordenamiento rápido"
query_vec = generator.embed_text(query)

results = store.search(
    collection_name="my_notes",
    query_embedding=query_vec,
    n_results=5,
    where={"deck": "Algoritmos"}  # Optional filter
)

# Format and display
formatted = format_search_results(results)
for i, result in enumerate(formatted, 1):
    print(f"{i}. [{result['distance']:.3f}] {result['metadata']['file_name']}")
    print(f"   {result['document'][:100]}...")
```

### 4. Running Module Tests

```bash
# Test individual module directly
python src/obsidian_loader.py /path/to/vault
python src/embeddings.py
python src/vectorstore.py

# Each module has a __main__ block for quick testing
```

### 5. Updating Dependencies

```bash
# Update requirements.txt
pip freeze > requirements.txt

# Or manually edit requirements.txt, then:
pip install -r requirements.txt --upgrade
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. ChromaDB Persistence Errors

**Problem**: `"Could not load collection"` or `"Collection not found"`

**Solution**:
```python
# Delete and recreate
store = ObsidianVectorStore(persist_directory="./chroma_db")
store.delete_collection("problematic_collection")
store.create_collection("problematic_collection", get_or_create=True)
```

#### 2. Sentence Transformers Model Download Fails

**Problem**: Network timeout when downloading model

**Solution**:
```bash
# Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', cache_folder='./models')"

# Or set environment variable
export MODELS_CACHE_DIR=./models
```

#### 3. Memory Issues with Large Vaults

**Problem**: OOM when processing 1000+ notes

**Solution**:
```python
# Process in smaller batches
from src.obsidian_loader import ObsidianLoader
from src.embeddings import EmbeddingGenerator

loader = ObsidianLoader(vault_path)
notes = loader.load_notes()

generator = EmbeddingGenerator()

# Batch process
batch_size = 100
for i in range(0, len(notes), batch_size):
    batch = notes[i:i+batch_size]
    contents = [note['content'] for note in batch]
    embeddings = generator.embed_batch(contents, batch_size=32)
    store.add_notes("my_notes", batch, embeddings)
```

#### 4. Empty Embeddings

**Problem**: Getting zero vectors for some notes

**Solution**:
```python
# Check content cleaning
from src.obsidian_loader import ObsidianLoader

loader = ObsidianLoader(vault_path)
notes = loader.load_notes()

# Inspect cleaned content
for note in notes:
    if len(note['content'].strip()) < 10:
        print(f"⚠️ Short content: {note['file_name']}")
        print(f"   Raw: {note['content_raw'][:100]}")
        print(f"   Cleaned: {note['content'][:100]}")
```

#### 5. Wikilink Parsing Issues

**Problem**: Wikilinks not extracted correctly

**Solution**:
```python
import re

content = "Test [[Link1]] and [[Link2|Alias]]"
pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
matches = re.findall(pattern, content)
print(matches)  # Should be: ['Link1', 'Link2']
```

### Debug Mode

Enable verbose logging:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 📚 Additional Resources

### Project Documentation
- **README.md**: User-facing documentation (Spanish)
- **.env.example**: Configuration template
- **requirements.txt**: Python dependencies

### External Documentation
- [Sentence Transformers](https://www.sbert.net/)
- [ChromaDB](https://docs.trychroma.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Obsidian](https://obsidian.md/)

### Learning Resources
- RAG fundamentals: `docs/conceptos/RAG.md` (planned)
- Embeddings explained: `docs/conceptos/embeddings.md` (planned)
- Vector databases: `docs/conceptos/vector-db.md` (planned)

---

## 🎯 Working with AI Assistants (Meta-Guide)

### Best Practices for AI Coding Assistants

When working on this project:

1. **Always Read First**: Before modifying any module, read it completely to understand context

2. **Follow Existing Patterns**: This codebase has consistent patterns (logging, docstrings, error handling) - maintain them

3. **Test Your Changes**: Run the module's `__main__` block or write tests

4. **Update This File**: If you make architectural changes, update CLAUDE.md

5. **Respect Language Choices**: Code/docstrings can be in Spanish (developer preference) or English

6. **Be Explicit**: When suggesting changes, show full context with line numbers

7. **Consider Phase**: This is early development - focus on core functionality over optimization

### Red Flags to Avoid

❌ Don't introduce new dependencies without discussion
❌ Don't change the embedding model without testing
❌ Don't modify the note format returned by ObsidianLoader (breaking change)
❌ Don't remove logging statements
❌ Don't skip type hints
❌ Don't commit to main branch

### Green Flags to Embrace

✅ Add comprehensive docstrings
✅ Include usage examples in docstrings
✅ Add logging for important operations
✅ Handle edge cases gracefully
✅ Write descriptive commit messages
✅ Add tests for new features
✅ Update documentation when changing behavior

---

## 📊 Project Status & Roadmap

### Current Status (as of 2025-01-17)

**Completed** ✅:
- ObsidianLoader module (parsing, frontmatter, wikilinks, content cleaning)
- EmbeddingGenerator module (text vectorization, batch processing, similarity)
- ObsidianVectorStore module (ChromaDB wrapper, CRUD, search)
- Project structure and configuration
- Documentation (README, CLAUDE.md, inline docs)

**In Progress** 🚧:
- Testing framework setup
- Integration between modules

**Next Priorities** 📋:
1. Write comprehensive unit tests for existing modules
2. Implement Retriever module (semantic search orchestration)
3. Implement Claude client (API integration)
4. Create RAG chain (full pipeline)
5. Build FastAPI endpoints
6. Docker containerization
7. Web UI (Streamlit)

### Known Limitations

- No tests yet (test structure exists but empty)
- No RAG pipeline integration (modules work independently)
- No API endpoints
- No Docker setup
- Spanish documentation may need English translation for broader audience
- No CI/CD pipeline

### Future Enhancements

- Incremental indexing (only update changed notes)
- Support for images and attachments
- Graph visualization of note connections
- Anki flashcard integration
- Multi-language embeddings (better Spanish support)
- Query history and analytics
- Caching layer for frequent queries

---

## 🤝 Contributing Guidelines

While this is primarily a personal learning project, contributions or suggestions are welcome:

1. **Fork & Branch**: Create a feature branch
2. **Follow Conventions**: Match existing code style
3. **Add Tests**: New features should have tests
4. **Document**: Update CLAUDE.md and docstrings
5. **Commit**: Use conventional commits
6. **Pull Request**: Describe changes clearly

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 📧 Contact & Support

**Developer**: Gabriel
**Project**: Personal learning project for Data Science portfolio
**Purpose**: Learn RAG, embeddings, vector databases, and system design

---

**End of CLAUDE.md**

> This document is a living guide. Update it as the project evolves.
> Last comprehensive update: 2025-01-17
