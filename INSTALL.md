# Quick Installation Guide

## Error: ModuleNotFoundError

Si ves este error al ejecutar los scripts:
```
ModuleNotFoundError: No module named 'sentence_transformers'
```

## Solución: Instalar Dependencias

### Opción 1: Instalación Completa (Recomendada)

```bash
pip install -r requirements.txt
```

### Opción 2: Instalación Manual de Dependencias Principales

```bash
# Core dependencies
pip install anthropic>=0.34.0
pip install python-dotenv>=1.0.0

# Embeddings
pip install sentence-transformers>=2.2.0
pip install torch>=2.0.0

# Vector Database
pip install chromadb>=0.4.22

# Text processing
pip install markdown>=3.5.0
pip install tiktoken>=0.5.0

# Utils
pip install pyyaml>=6.0
pip install tqdm>=4.66.0
pip install numpy>=1.24.0
pip install pandas>=2.0.0
```

### Opción 3: Instalación Mínima (Solo para Probar)

Si solo quieres probar el sistema sin todos los extras:

```bash
pip install anthropic sentence-transformers chromadb python-dotenv tqdm
```

**Nota**: Esto instalará PyTorch automáticamente, que es un paquete grande (~2GB). La instalación puede tardar varios minutos.

## Configuración Después de Instalar

1. Configura tu API key de Anthropic:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-api03-...
   ```

2. O crea un archivo `.env`:
   ```bash
   cp .env.example .env
   # Edita .env y añade tu API key
   ```

3. Prueba el sistema:
   ```bash
   python scripts/quick_start.py /path/to/vault
   ```

## Verificar Instalación

```bash
python -c "import anthropic; import sentence_transformers; import chromadb; print('✅ Todas las dependencias instaladas')"
```

## Problemas Comunes

### Error de permisos con pip

Si ves:
```
WARNING: The directory '/root/.cache/pip' or its parent directory is not owned...
```

Usa:
```bash
pip install --user -r requirements.txt
```

O en un virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows

pip install -r requirements.txt
```

### Error con PyTorch en CPU-only

Si no tienes GPU y quieres una instalación más ligera:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers chromadb anthropic python-dotenv tqdm
```

### Instalación muy lenta

PyTorch es un paquete grande. Si la instalación es muy lenta:

1. Asegúrate de tener buena conexión a internet
2. Considera usar la versión CPU-only (más pequeña)
3. Si estás en un environment con limitaciones, considera usar Docker

## Docker (Alternativa)

Si prefieres usar Docker para evitar problemas de dependencias:

```bash
# TODO: Añadir Dockerfile en el futuro
```

Para más información, consulta:
- `docs/guias/claude-integration.md` - Guía completa
- `README.md` - Documentación general
