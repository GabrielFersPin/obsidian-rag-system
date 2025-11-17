"""
Módulo de carga y parsing de notas de Obsidian

Este módulo se encarga de:
1. Leer archivos .md de un vault de Obsidian
2. Extraer frontmatter (YAML)
3. Parsear wikilinks
4. Limpiar contenido para embeddings
5. Extraer metadata del archivo

NO extrae flashcards (esas ya están en Anki)

Autor: Gabriel
Fecha: 2025-01
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ObsidianLoader:
    """
    Cargador de notas de Obsidian.
    
    Lee archivos Markdown de un vault de Obsidian, extrae frontmatter,
    wikilinks, y prepara el contenido para embeddings.
    
    Attributes:
        vault_path: Path al vault de Obsidian
        ignore_patterns: Patrones de archivos/carpetas a ignorar
    
    Example:
        >>> loader = ObsidianLoader("/path/to/vault")
        >>> notas = loader.load_notes()
        >>> print(f"Cargadas {len(notas)} notas")
    """
    
    def __init__(
        self,
        vault_path: str,
        ignore_patterns: Optional[List[str]] = None
    ):
        """
        Inicializa el loader.
        
        Args:
            vault_path: Ruta al vault de Obsidian
            ignore_patterns: Patrones a ignorar (ej: ["template", ".trash"])
        """
        self.vault_path = Path(vault_path)
        
        if not self.vault_path.exists():
            raise ValueError(f"Vault path no existe: {vault_path}")
        
        if not self.vault_path.is_dir():
            raise ValueError(f"Vault path no es directorio: {vault_path}")
        
        # Patrones por defecto a ignorar
        self.ignore_patterns = ignore_patterns or [
            'template',
            '.trash',
            '.obsidian',
            '.git',
            '__pycache__'
        ]
        
        logger.info(f"📁 Vault cargado: {self.vault_path}")
        logger.info(f"🚫 Ignorando patrones: {self.ignore_patterns}")
    
    def should_ignore(self, path: Path) -> bool:
        """
        Determina si un archivo/carpeta debe ser ignorado.
        
        Args:
            path: Path a verificar
        
        Returns:
            True si debe ser ignorado
        """
        path_str = str(path).lower()
        
        # Ignorar archivos/carpetas ocultos
        if any(part.startswith('.') for part in path.parts):
            return True
        
        # Ignorar por patrones
        for pattern in self.ignore_patterns:
            if pattern.lower() in path_str:
                return True
        
        return False
    
    def load_notes(
        self,
        file_extensions: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Carga todas las notas del vault.
        
        Args:
            file_extensions: Extensiones a cargar (default: ['.md'])
        
        Returns:
            Lista de diccionarios con datos de notas
        
        Example:
            >>> notas = loader.load_notes()
            >>> for nota in notas:
            ...     print(nota['file_name'])
        """
        if file_extensions is None:
            file_extensions = ['.md']
        
        logger.info(f"📚 Cargando notas del vault...")
        logger.info(f"   Extensiones: {file_extensions}")
        
        notas = []
        archivos_procesados = 0
        archivos_ignorados = 0
        
        # Recorrer vault recursivamente
        for md_file in self.vault_path.rglob('*'):
            # Solo archivos con extensión correcta
            if md_file.suffix not in file_extensions:
                continue
            
            # Ignorar según patrones
            if self.should_ignore(md_file):
                archivos_ignorados += 1
                continue
            
            # Parsear nota
            try:
                nota = self._parse_note(md_file)
                if nota:
                    notas.append(nota)
                    archivos_procesados += 1
            except Exception as e:
                logger.warning(f"⚠️ Error parseando {md_file.name}: {e}")
                continue
        
        logger.info(f"✅ Carga completada:")
        logger.info(f"   Procesados: {archivos_procesados}")
        logger.info(f"   Ignorados: {archivos_ignorados}")
        logger.info(f"   Total notas: {len(notas)}")
        
        return notas
    
    def _parse_note(self, file_path: Path) -> Optional[Dict]:
        """
        Parsea una nota individual.
        
        Args:
            file_path: Path al archivo .md
        
        Returns:
            Diccionario con datos de la nota o None si hay error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"❌ Error leyendo {file_path}: {e}")
            return None
        
        # Extraer componentes
        frontmatter = self._extract_frontmatter(content)
        wikilinks = self._extract_wikilinks(content)
        title = self._extract_title(content)
        content_clean = self._clean_content(content)
        
        # Metadata del archivo
        file_stat = file_path.stat()
        
        return {
            # Identificación
            'file_name': file_path.stem,
            'file_path': str(file_path),
            'title': title or file_path.stem,
            
            # Contenido
            'content': content_clean,
            'content_raw': content,
            
            # Metadata de frontmatter
            'deck': frontmatter.get('cards-deck', 'general'),
            'status': frontmatter.get('status', ''),
            'tipo_nota': frontmatter.get('tipo_nota', ''),
            'created': frontmatter.get('created', ''),
            'modified': frontmatter.get('modified', ''),
            'frontmatter': frontmatter,
            
            # Enlaces y relaciones
            'wikilinks': wikilinks,
            'num_links': len(wikilinks),
            
            # Metadata del archivo
            'file_size': file_stat.st_size,
            'last_modified': datetime.fromtimestamp(file_stat.st_mtime),
            'last_accessed': datetime.fromtimestamp(file_stat.st_atime)
        }
    
    def _extract_frontmatter(self, content: str) -> Dict:
        """
        Extrae frontmatter YAML del contenido.
        
        Args:
            content: Contenido completo del archivo
        
        Returns:
            Diccionario con campos del frontmatter
        
        Example:
            >>> content = "---\ncards-deck: Algoritmos\n---\nContenido..."
            >>> fm = loader._extract_frontmatter(content)
            >>> print(fm['cards-deck'])
            'Algoritmos'
        """
        frontmatter = {}
        
        # Buscar bloque entre ---
        pattern = r'^---\n(.*?)\n---'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return frontmatter
        
        yaml_content = match.group(1)
        
        # Parsear líneas YAML (simple, sin dependencias)
        for line in yaml_content.split('\n'):
            line = line.strip()
            
            # Ignorar comentarios y líneas vacías
            if not line or line.startswith('#'):
                continue
            
            # Parsear "key: value"
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Remover comillas si existen
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                frontmatter[key] = value
        
        return frontmatter
    
    def _extract_wikilinks(self, content: str) -> List[str]:
        """
        Extrae wikilinks del contenido.
        
        Args:
            content: Contenido del archivo
        
        Returns:
            Lista de nombres de notas enlazadas (sin aliases)
        
        Example:
            >>> content = "Ver [[QuickSort]] y [[Nota|Alias]]"
            >>> links = loader._extract_wikilinks(content)
            >>> print(links)
            ['QuickSort', 'Nota']
        """
        # Pattern: [[nota]] o [[nota|alias]]
        pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
        matches = re.findall(pattern, content)
        
        # Limpiar y deduplicar
        links = []
        seen = set()
        
        for match in matches:
            # Ignorar embeddings (![[imagen]])
            if match.startswith('!'):
                continue
            
            # Limpiar espacios
            link = match.strip()
            
            # Solo añadir si no lo hemos visto
            if link and link not in seen:
                links.append(link)
                seen.add(link)
        
        return links
    
    def _extract_title(self, content: str) -> Optional[str]:
        """
        Extrae el título (primer heading de nivel 1).
        
        Args:
            content: Contenido del archivo
        
        Returns:
            Título de la nota o None
        """
        # Buscar primer # Título (después del frontmatter)
        # Remover frontmatter primero
        content_without_fm = re.sub(
            r'^---\n.*?\n---\n',
            '',
            content,
            flags=re.DOTALL
        )
        
        # Buscar primer heading nivel 1
        pattern = r'^#\s+(.+)$'
        match = re.search(pattern, content_without_fm, re.MULTILINE)
        
        if match:
            return match.group(1).strip()
        
        return None
    
    def _clean_content(self, content: str) -> str:
        """
        Limpia contenido para embeddings.
        
        Remueve:
        - Frontmatter
        - Bloques de código
        - Comentarios
        - Sintaxis Markdown (pero mantiene texto)
        - Callouts (mantiene contenido)
        
        Args:
            content: Contenido crudo
        
        Returns:
            Contenido limpio para embeddings
        """
        cleaned = content
        
        # 1. Remover frontmatter
        cleaned = re.sub(r'^---\n.*?\n---\n', '', cleaned, flags=re.DOTALL)
        
        # 2. Remover bloques de código
        cleaned = re.sub(r'```.*?```', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'`[^`]+`', '', cleaned)  # Código inline
        
        # 3. Remover comentarios HTML
        cleaned = re.sub(r'<!--.*?-->', '', cleaned, flags=re.DOTALL)
        
        # 4. Remover comentarios Obsidian
        cleaned = re.sub(r'%%.*?%%', '', cleaned, flags=re.DOTALL)
        
        # 5. Remover sintaxis de callouts pero mantener contenido
        cleaned = re.sub(r'>\s*\[!(\w+)\]\s*', '', cleaned)
        cleaned = re.sub(r'^>\s*', '', cleaned, flags=re.MULTILINE)
        
        # 6. Convertir wikilinks a texto plano
        # [[Nota|Alias]] → Alias
        # [[Nota]] → Nota
        cleaned = re.sub(
            r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]',
            lambda m: m.group(2) if m.group(2) else m.group(1),
            cleaned
        )
        
        # 7. Remover sintaxis de headings
        cleaned = re.sub(r'^#{1,6}\s+', '', cleaned, flags=re.MULTILINE)
        
        # 8. Remover énfasis (pero mantener texto)
        cleaned = re.sub(r'\*\*(.+?)\*\*', r'\1', cleaned)  # **bold**
        cleaned = re.sub(r'__(.+?)__', r'\1', cleaned)      # __bold__
        cleaned = re.sub(r'\*(.+?)\*', r'\1', cleaned)      # *italic*
        cleaned = re.sub(r'_(.+?)_', r'\1', cleaned)        # _italic_
        cleaned = re.sub(r'~~(.+?)~~', r'\1', cleaned)      # ~~strike~~
        cleaned = re.sub(r'==(.+?)==', r'\1', cleaned)      # ==highlight==
        
        # 9. Remover URLs de imágenes embebidas
        cleaned = re.sub(r'!\[\[.*?\]\]', '', cleaned)
        
        # 10. Remover IDs de bloques
        cleaned = re.sub(r'\^[\w-]+$', '', cleaned, flags=re.MULTILINE)
        
        # 11. Limpiar espacios múltiples
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        
        return cleaned.strip()
    
    def get_vault_stats(self) -> Dict:
        """
        Obtiene estadísticas del vault.
        
        Returns:
            Diccionario con estadísticas
        """
        notas = self.load_notes()
        
        # Estadísticas por deck
        decks = {}
        statuses = {}
        tipos = {}
        
        for nota in notas:
            # Por deck
            deck = nota['deck']
            decks[deck] = decks.get(deck, 0) + 1
            
            # Por status
            status = nota['status']
            statuses[status] = statuses.get(status, 0) + 1
            
            # Por tipo
            tipo = nota['tipo_nota']
            if tipo:
                tipos[tipo] = tipos.get(tipo, 0) + 1
        
        # Estadísticas de enlaces
        total_links = sum(nota['num_links'] for nota in notas)
        avg_links = total_links / len(notas) if notas else 0
        
        return {
            'total_notes': len(notas),
            'by_deck': decks,
            'by_status': statuses,
            'by_type': tipos,
            'total_links': total_links,
            'avg_links_per_note': round(avg_links, 2)
        }


# ============================================
# Funciones de utilidad
# ============================================

def find_orphan_notes(notes: List[Dict]) -> List[str]:
    """
    Encuentra notas sin enlaces (huérfanas).
    
    Args:
        notes: Lista de notas
    
    Returns:
        Lista de nombres de notas huérfanas
    """
    # Notas que tienen 0 links salientes
    return [
        nota['file_name']
        for nota in notes
        if nota['num_links'] == 0
    ]


def build_link_graph(notes: List[Dict]) -> Dict[str, List[str]]:
    """
    Construye grafo de enlaces entre notas.
    
    Args:
        notes: Lista de notas
    
    Returns:
        Diccionario {nota: [notas_enlazadas]}
    """
    graph = {}
    
    for nota in notes:
        graph[nota['file_name']] = nota['wikilinks']
    
    return graph


# ============================================
# Script de prueba
# ============================================

if __name__ == "__main__":
    """
    Script de prueba del loader.
    
    Uso:
        python src/obsidian_loader.py /path/to/vault
    """
    import sys
    
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        # Path por defecto (ajustar según tu setup)
        vault_path = "./data/vault"
        print(f"⚠️ Usando vault por defecto: {vault_path}")
        print(f"   Uso: python src/obsidian_loader.py /path/to/vault")
    
    print(f"\n🧪 Probando ObsidianLoader...\n")
    
    try:
        # Crear loader
        loader = ObsidianLoader(vault_path)
        
        # Cargar notas
        notas = loader.load_notes()
        
        if not notas:
            print("⚠️ No se encontraron notas")
            sys.exit(0)
        
        # Mostrar ejemplo
        print(f"\n📄 Ejemplo de nota parseada:")
        nota_ejemplo = notas[0]
        print(f"   Nombre: {nota_ejemplo['file_name']}")
        print(f"   Deck: {nota_ejemplo['deck']}")
        print(f"   Status: {nota_ejemplo['status']}")
        print(f"   Links: {nota_ejemplo['wikilinks'][:3]}...")
        print(f"   Contenido: {nota_ejemplo['content'][:100]}...")
        
        # Estadísticas
        print(f"\n📊 Estadísticas del vault:")
        stats = loader.get_vault_stats()
        print(f"   Total notas: {stats['total_notes']}")
        print(f"   Por deck: {stats['by_deck']}")
        print(f"   Enlaces promedio: {stats['avg_links_per_note']}")
        
        # Notas huérfanas
        orphans = find_orphan_notes(notas)
        print(f"   Notas huérfanas: {len(orphans)}")
        if orphans:
            print(f"      Ejemplos: {orphans[:3]}")
        
        print("\n✅ Pruebas completadas!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)