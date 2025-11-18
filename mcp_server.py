#!/usr/bin/env python3
"""
MCP Server para RAG de Obsidian

Este servidor expone el sistema RAG como herramientas MCP
que Claude Code puede usar desde la terminal.

Autor: Gabriel
Fecha: 2025-01
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Any, Sequence
from dotenv import load_dotenv

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Tu RAG
sys.path.insert(0, str(Path(__file__).parent))
from src.rag_chain import ObsidianRAGSystem

# Cargar env
load_dotenv()

# Crear servidor MCP
app = Server("obsidian-rag")

# Inicializar RAG (global para reutilizar)
vault_path = os.getenv('OBSIDIAN_VAULT_PATH', './data/vault')
rag_system = None


def get_rag_system():
    """Obtiene instancia del RAG (lazy loading)."""
    global rag_system
    if rag_system is None:
        rag_system = ObsidianRAGSystem(vault_path=vault_path)
    return rag_system


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    Lista las herramientas disponibles.
    Claude Code las verá en la terminal.
    """
    return [
        Tool(
            name="search_vault",
            description=(
                "Busca información en el vault de Obsidian de Gabriel. "
                "Contiene notas sobre: Algoritmos, Estructuras de Datos, "
                "Infraestructura en la Nube, Arquitectura de Computadores, "
                "Fundamentos de Ciencia de Datos. "
                "Devuelve contexto relevante de las notas."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "La pregunta o tema a buscar en las notas"
                    },
                    "deck": {
                        "type": "string",
                        "description": (
                            "Asignatura para filtrar (opcional): "
                            "'Algoritmos', 'Nube', 'DataScience', 'Arquitectura'"
                        ),
                        "enum": ["Algoritmos", "Nube", "DataScience", "Arquitectura", ""]
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Número de resultados a retornar (1-10)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_vault_stats",
            description=(
                "Obtiene estadísticas del vault de notas: "
                "total de notas, distribución por asignatura, "
                "última indexación, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_notes_by_deck",
            description=(
                "Lista todas las notas de una asignatura específica. "
                "Útil para ver qué temas hay disponibles."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "deck": {
                        "type": "string",
                        "description": "Asignatura a listar",
                        "enum": ["Algoritmos", "Nube", "DataScience", "Arquitectura"]
                    }
                },
                "required": ["deck"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """
    Ejecuta una herramienta cuando Claude la llama.
    """
    
    if name == "search_vault":
        # Buscar en el vault
        query = arguments.get("query")
        deck = arguments.get("deck", "").strip()
        n_results = arguments.get("n_results", 5)
        
        if not query:
            return [TextContent(
                type="text",
                text="Error: Se requiere una query para buscar."
            )]
        
        try:
            rag = get_rag_system()
            
            # Realizar búsqueda
            result = rag.query(
                question=query,
                n_results=n_results,
                deck_filter=deck if deck else None,
                return_sources=True
            )
            
            if 'error' in result:
                return [TextContent(
                    type="text",
                    text=f"Error: {result['error']}\n\nPor favor, indexa el vault primero ejecutando: python run_rag.py"
                )]
            
            # Formatear respuesta
            response_text = f"# Resultados de búsqueda en vault de Obsidian\n\n"
            response_text += f"**Query**: {query}\n"
            if deck:
                response_text += f"**Asignatura**: {deck}\n"
            response_text += f"**Resultados encontrados**: {result['n_results']}\n\n"
            response_text += "---\n\n"
            response_text += result['context']
            
            if result.get('sources'):
                response_text += "\n## Fuentes\n\n"
                for i, source in enumerate(result['sources'], 1):
                    response_text += f"{i}. **{source['file_name']}** ({source['deck']})\n"
                    response_text += f"   - Relevancia: {(1 - source['distance']) * 100:.1f}%\n"
            
            return [TextContent(
                type="text",
                text=response_text
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error ejecutando búsqueda: {str(e)}"
            )]
    
    elif name == "get_vault_stats":
        # Estadísticas del vault
        try:
            rag = get_rag_system()
            info = rag.get_system_info()
            
            stats_text = "# Estadísticas del Vault de Obsidian\n\n"
            stats_text += f"**Total de notas indexadas**: {info['indexed_notes']}\n"
            stats_text += f"**Última indexación**: {info['last_index_time'] or 'Nunca'}\n"
            stats_text += f"**Modelo de embeddings**: {info['embedding_model']}\n"
            stats_text += f"**Dimensión**: {info['embedding_dimension']}\n\n"
            
            if info['by_deck']:
                stats_text += "## Distribución por asignatura\n\n"
                for deck, count in sorted(info['by_deck'].items(), key=lambda x: -x[1]):
                    stats_text += f"- **{deck}**: {count} notas\n"
            else:
                stats_text += "⚠️ No hay notas indexadas.\n"
            
            return [TextContent(
                type="text",
                text=stats_text
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error obteniendo estadísticas: {str(e)}"
            )]
    
    elif name == "list_notes_by_deck":
        # Listar notas de un deck
        deck = arguments.get("deck")
        
        if not deck:
            return [TextContent(
                type="text",
                text="Error: Se requiere especificar un deck."
            )]
        
        try:
            rag = get_rag_system()
            
            # Hacer query genérica para ese deck
            result = rag.query(
                question=f"notas de {deck}",
                deck_filter=deck,
                n_results=20,
                return_sources=True
            )
            
            if 'error' in result:
                return [TextContent(
                    type="text",
                    text=f"Error: {result['error']}"
                )]
            
            list_text = f"# Notas de {deck}\n\n"
            
            if result.get('sources'):
                list_text += f"**Total encontradas**: {len(result['sources'])}\n\n"
                for i, source in enumerate(result['sources'], 1):
                    list_text += f"{i}. **{source['file_name']}**\n"
                    # Mostrar snippet corto
                    snippet = source.get('snippet', '')[:150]
                    if snippet:
                        list_text += f"   _{snippet}..._\n"
                    list_text += "\n"
            else:
                list_text += f"No se encontraron notas en {deck}.\n"
            
            return [TextContent(
                type="text",
                text=list_text
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error listando notas: {str(e)}"
            )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Error: Herramienta desconocida '{name}'"
        )]


async def main():
    """Punto de entrada del servidor MCP."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())