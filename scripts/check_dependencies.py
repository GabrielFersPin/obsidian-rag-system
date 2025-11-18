#!/usr/bin/env python3
"""
Script para verificar dependencias del Obsidian RAG System

Ejecutar antes de usar el sistema para asegurarse de que todo está instalado.

Uso:
    python scripts/check_dependencies.py
"""

import sys

def check_dependency(package_name, import_name=None):
    """Verifica si un paquete está instalado."""
    if import_name is None:
        import_name = package_name.replace('-', '_')

    try:
        __import__(import_name)
        return True, None
    except ImportError as e:
        return False, str(e)

def main():
    print("🔍 Verificando dependencias del Obsidian RAG System\n")

    dependencies = [
        ('anthropic', 'anthropic', 'API de Claude'),
        ('sentence-transformers', 'sentence_transformers', 'Generación de embeddings'),
        ('chromadb', 'chromadb', 'Vector database'),
        ('python-dotenv', 'dotenv', 'Manejo de variables de entorno'),
        ('torch', 'torch', 'PyTorch (requerido por sentence-transformers)'),
        ('numpy', 'numpy', 'Operaciones numéricas'),
        ('tqdm', 'tqdm', 'Barras de progreso'),
    ]

    missing = []
    installed = []

    for package, import_name, description in dependencies:
        success, error = check_dependency(package, import_name)

        if success:
            try:
                module = __import__(import_name)
                version = getattr(module, '__version__', 'unknown')
                installed.append((package, version, description))
                print(f"✅ {package:25} v{version:10} - {description}")
            except:
                installed.append((package, 'unknown', description))
                print(f"✅ {package:25} (instalado)  - {description}")
        else:
            missing.append((package, description))
            print(f"❌ {package:25} FALTA       - {description}")

    print("\n" + "=" * 70)

    if not missing:
        print("✅ Todas las dependencias están instaladas!")
        print("\nPuedes empezar a usar el sistema:")
        print("  python scripts/quick_start.py /path/to/vault")
        return 0
    else:
        print(f"❌ Faltan {len(missing)} dependencias")
        print("\nPara instalar todas las dependencias:")
        print("  pip install -r requirements.txt")
        print("\nO instala las faltantes manualmente:")
        packages = ' '.join([p[0] for p in missing])
        print(f"  pip install {packages}")
        print("\nVer INSTALL.md para más información sobre instalación.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
