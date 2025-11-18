# Vault de Prueba

Este es un vault de ejemplo con notas para probar el sistema RAG.

## Contenido

- **QuickSort.md** - Algoritmo de ordenamiento rápido
- **MergeSort.md** - Algoritmo de ordenamiento estable
- **Docker.md** - Plataforma de contenedorización
- **RAG.md** - Retrieval-Augmented Generation
- **ChromaDB.md** - Base de datos vectorial

## Uso

Puedes usar este vault para probar el sistema:

```bash
python scripts/quick_start.py data/vault
```

O indexarlo primero:

```bash
python scripts/index_vault.py data/vault
```

## Crear Tu Propio Vault

Para usar tus notas reales de Obsidian, simplemente apunta al directorio de tu vault:

```bash
python scripts/quick_start.py /path/to/tu/vault
```
