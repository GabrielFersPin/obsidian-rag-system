# Scripts de Obsidian RAG System

Este directorio contiene scripts útiles para trabajar con el sistema RAG.

## 📋 Scripts Disponibles

### 🚀 quick_start.py

Forma más rápida de empezar con el sistema. Inicia un modo interactivo de preguntas y respuestas.

**Uso:**
```bash
python scripts/quick_start.py /path/to/vault
```

**Requisitos:**
- `ANTHROPIC_API_KEY` configurada
- Vault de Obsidian válido

**Características:**
- Indexación automática
- Modo interactivo de Q&A
- Comandos especiales (stats, help, salir)

---

### 📚 index_vault.py

Script para indexar o reindexar tu vault de Obsidian.

**Uso:**
```bash
python scripts/index_vault.py /path/to/vault [opciones]
```

**Opciones:**
- `--force`: Fuerza reindexación (elimina índice existente)
- `--collection`: Nombre de la collection (default: obsidian_notes)
- `--batch-size`: Tamaño de batch para embeddings (default: 32)
- `--chroma-dir`: Directorio de ChromaDB (default: ./chroma_db)
- `--models-dir`: Directorio para modelos (default: ./models)
- `--embedding-model`: Modelo de embeddings a usar

**Ejemplos:**
```bash
# Indexar vault
python scripts/index_vault.py ~/Documents/ObsidianVault

# Forzar reindexación con batch size mayor
python scripts/index_vault.py ~/vault --force --batch-size 64

# Usar collection custom
python scripts/index_vault.py ~/vault --collection my_notes
```

---

### 📖 example_rag_usage.py

Script de ejemplo completo que demuestra todos los casos de uso del sistema RAG.

**Uso:**
```bash
python scripts/example_rag_usage.py
```

**Requiere:**
- Archivo `.env` configurado con todas las variables

**Demuestra:**
- Inicialización del sistema
- Indexación de vault
- Queries simples y complejas
- Modo conversacional
- Búsqueda de notas relacionadas
- Estadísticas del sistema

---

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
cp .env.example .env
```

Variables requeridas:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
VAULT_PATH=/path/to/vault
```

Variables opcionales (con defaults):
```
CHROMA_PERSIST_DIR=./chroma_db
MODELS_CACHE_DIR=./models
COLLECTION_NAME=obsidian_notes
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CLAUDE_MODEL=sonnet
DEFAULT_TOP_K=5
CLAUDE_TEMPERATURE=0.7
CLAUDE_MAX_TOKENS=2048
LOG_LEVEL=INFO
```

### Dependencias

Instala todas las dependencias:

```bash
pip install -r requirements.txt
```

Dependencias principales:
- `anthropic>=0.34.0` - API de Claude
- `sentence-transformers>=2.2.0` - Embeddings
- `chromadb>=0.4.22` - Vector store
- `python-dotenv>=1.0.0` - Variables de entorno

## 🎯 Flujo de Trabajo Recomendado

### Primera Vez

1. Configura tu `.env`:
   ```bash
   cp .env.example .env
   # Edita .env con tu API key y vault path
   ```

2. Indexa tu vault:
   ```bash
   python scripts/index_vault.py $VAULT_PATH
   ```

3. Prueba el sistema:
   ```bash
   python scripts/quick_start.py $VAULT_PATH
   ```

### Uso Regular

**Opción 1: Modo Interactivo**
```bash
python scripts/quick_start.py $VAULT_PATH
```

**Opción 2: Programático**
```python
from src.rag_chain import ObsidianRAG

rag = ObsidianRAG(vault_path="/path/to/vault")
result = rag.query("Tu pregunta")
print(result.answer)
```

### Actualizar Índice

Cuando agregues muchas notas nuevas:

```bash
python scripts/index_vault.py $VAULT_PATH --force
```

## 💡 Tips

1. **Desarrollo**: Usa `CLAUDE_MODEL=haiku` para desarrollo (más rápido y barato)
2. **Producción**: Usa `CLAUDE_MODEL=sonnet` para mejor calidad
3. **Batch Size**: Aumenta `--batch-size` si tienes buena GPU/RAM
4. **Reindexación**: Solo usa `--force` cuando sea necesario (es lento)
5. **Collections**: Usa diferentes collections para diferentes vaults

## 🐛 Troubleshooting

### Script no encuentra módulos

Asegúrate de ejecutar desde la raíz del proyecto:

```bash
cd /path/to/obsidian-rag-system
python scripts/script_name.py
```

### Error de API key

Verifica que está configurada:

```bash
echo $ANTHROPIC_API_KEY
# o
cat .env | grep ANTHROPIC_API_KEY
```

### Out of memory al indexar

Reduce el batch size:

```bash
python scripts/index_vault.py $VAULT_PATH --batch-size 16
```

### ChromaDB corrupto

Elimina y reindexa:

```bash
rm -rf ./chroma_db
python scripts/index_vault.py $VAULT_PATH
```

## 📚 Más Información

- Ver `docs/guias/claude-integration.md` para guía completa
- Ver `README.md` en la raíz para documentación general
- Ver código fuente en `src/` para detalles de implementación

## 🤝 Contribuir

Si quieres añadir nuevos scripts útiles, sigue estas convenciones:

1. Añade shebang: `#!/usr/bin/env python3`
2. Docstring descriptivo al inicio
3. Argumentos via `argparse` con `--help`
4. Manejo de errores apropiado
5. Logging informativo
6. Documenta en este README
