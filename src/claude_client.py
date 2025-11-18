"""
Módulo de Cliente Claude para Obsidian RAG System

Este módulo encapsula la interacción con la API de Anthropic (Claude).
Proporciona funcionalidad para generar respuestas basadas en contexto
recuperado del vector store.

Componentes principales:
1. ClaudeClient: Cliente principal para API de Anthropic
2. Prompt templates para RAG
3. Manejo de conversaciones multi-turn

Autor: Gabriel
Fecha: 2025-01
"""

import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging
from datetime import datetime

try:
    from anthropic import Anthropic, AnthropicError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("⚠️ Anthropic library no disponible. Instalar con: pip install anthropic")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ClaudeResponse:
    """
    Respuesta de Claude.

    Attributes:
        content: Texto de la respuesta
        model: Modelo usado
        tokens_input: Tokens de entrada consumidos
        tokens_output: Tokens de salida generados
        stop_reason: Razón de parada (end_turn, max_tokens, etc.)
        metadata: Metadata adicional
    """
    content: str
    model: str
    tokens_input: int
    tokens_output: int
    stop_reason: str
    metadata: Dict[str, Any]

    def __repr__(self) -> str:
        return (
            f"ClaudeResponse(model={self.model}, "
            f"tokens={self.tokens_input + self.tokens_output}, "
            f"stop_reason={self.stop_reason})"
        )


class ClaudeClient:
    """
    Cliente para interactuar con la API de Claude.

    Proporciona métodos de alto nivel para generar respuestas RAG,
    manejar conversaciones, y formatear prompts optimizados.

    Attributes:
        api_key: API key de Anthropic
        model: Modelo de Claude a usar
        client: Cliente de Anthropic
        max_tokens: Máximo de tokens por respuesta
        temperature: Temperatura para generación

    Example:
        >>> client = ClaudeClient(api_key="sk-...")
        >>> response = client.generate_rag_response(
        ...     query="¿Qué es QuickSort?",
        ...     context="QuickSort es un algoritmo..."
        ... )
        >>> print(response.content)
    """

    # Modelos disponibles
    MODELS = {
        'haiku': 'claude-3-5-haiku-20241022',
        'sonnet': 'claude-3-5-sonnet-20241022',
        'opus': 'claude-3-opus-20240229'
    }

    # Templates de sistema
    RAG_SYSTEM_PROMPT = """Eres un asistente de estudio inteligente especializado en ayudar con notas académicas.

Tu trabajo es responder preguntas basándote EXCLUSIVAMENTE en el contexto proporcionado de las notas de Obsidian del usuario.

REGLAS IMPORTANTES:
1. Solo usa información del contexto proporcionado
2. Si la respuesta no está en el contexto, di "No encontré esa información en tus notas"
3. Cita las notas relevantes cuando sea posible (menciona el nombre del documento)
4. Sé conciso pero completo
5. Si hay flashcards relevantes, menciónalas
6. Conecta conceptos entre diferentes notas cuando sea relevante

FORMATO DE RESPUESTA:
- Respuesta directa a la pregunta
- Explicación basada en las notas
- Conexiones con otros conceptos (si existen)
- Referencias a las notas usadas"""

    CONVERSATION_SYSTEM_PROMPT = """Eres un asistente de estudio inteligente que ayuda a revisar y entender notas académicas.

Puedes:
- Responder preguntas sobre conceptos
- Explicar conexiones entre temas
- Generar ejemplos basados en las notas
- Ayudar a preparar exámenes
- Resumir temas complejos

Siempre basa tus respuestas en las notas proporcionadas."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'sonnet',
        max_tokens: int = 2048,
        temperature: float = 0.7,
        timeout: float = 60.0
    ):
        """
        Inicializa el cliente de Claude.

        Args:
            api_key: API key de Anthropic (o usa ANTHROPIC_API_KEY env var)
            model: Modelo a usar ('haiku', 'sonnet', 'opus')
            max_tokens: Máximo de tokens por respuesta
            temperature: Temperatura (0.0-1.0). Menor = más determinista
            timeout: Timeout en segundos para requests

        Raises:
            ValueError: Si no hay API key o anthropic no está instalado
        """
        if not ANTHROPIC_AVAILABLE:
            raise ValueError(
                "Anthropic library no instalada. "
                "Instalar con: pip install anthropic"
            )

        # Obtener API key
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "API key no proporcionada. "
                "Usa el parámetro api_key o la variable ANTHROPIC_API_KEY"
            )

        # Validar modelo
        if model not in self.MODELS:
            raise ValueError(
                f"Modelo '{model}' no válido. "
                f"Opciones: {list(self.MODELS.keys())}"
            )

        self.model = self.MODELS[model]
        self.model_name = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        # Crear cliente
        try:
            self.client = Anthropic(
                api_key=self.api_key,
                timeout=timeout
            )
            logger.info(f"✅ Claude cliente inicializado")
            logger.info(f"   Modelo: {self.model_name} ({self.model})")
            logger.info(f"   Max tokens: {max_tokens}")
        except Exception as e:
            logger.error(f"❌ Error inicializando cliente Claude: {e}")
            raise

        # Historial de conversación (opcional)
        self.conversation_history: List[Dict] = []

    def generate_rag_response(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
        include_sources: bool = True,
        **kwargs
    ) -> ClaudeResponse:
        """
        Genera respuesta RAG basada en query y contexto.

        Args:
            query: Pregunta del usuario
            context: Contexto recuperado del vector store
            system_prompt: System prompt custom (usa default si None)
            include_sources: Si incluir referencias a fuentes
            **kwargs: Argumentos adicionales para la API

        Returns:
            ClaudeResponse con la respuesta generada

        Example:
            >>> response = client.generate_rag_response(
            ...     query="¿Qué es QuickSort?",
            ...     context="--- Documento 1: QuickSort ---\\nQuickSort es..."
            ... )
            >>> print(response.content)
        """
        logger.info(f"🤖 Generando respuesta RAG para: '{query[:50]}...'")

        # Usar system prompt por defecto si no se proporciona
        system = system_prompt or self.RAG_SYSTEM_PROMPT

        # Construir prompt de usuario
        user_prompt = self._build_rag_prompt(query, context, include_sources)

        # Generar respuesta
        response = self._call_api(
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
            **kwargs
        )

        logger.info(f"✅ Respuesta generada: {response.tokens_output} tokens")

        return response

    def chat(
        self,
        message: str,
        context: Optional[str] = None,
        use_history: bool = True,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> ClaudeResponse:
        """
        Modo conversacional con historial.

        Args:
            message: Mensaje del usuario
            context: Contexto opcional para esta interacción
            use_history: Si usar historial de conversación
            system_prompt: System prompt custom
            **kwargs: Argumentos adicionales para la API

        Returns:
            ClaudeResponse con la respuesta

        Example:
            >>> # Primera pregunta
            >>> response1 = client.chat("¿Qué es QuickSort?", context=ctx)
            >>> # Pregunta de seguimiento (usa historial)
            >>> response2 = client.chat("¿Y MergeSort?")
        """
        logger.info(f"💬 Chat: '{message[:50]}...'")

        # Construir mensaje
        if context:
            full_message = f"Contexto:\n{context}\n\nPregunta: {message}"
        else:
            full_message = message

        # Construir historial
        messages = []
        if use_history and self.conversation_history:
            messages = self.conversation_history.copy()

        messages.append({"role": "user", "content": full_message})

        # System prompt
        system = system_prompt or self.CONVERSATION_SYSTEM_PROMPT

        # Generar respuesta
        response = self._call_api(
            system=system,
            messages=messages,
            **kwargs
        )

        # Guardar en historial si se usa
        if use_history:
            self.conversation_history.append(
                {"role": "user", "content": full_message}
            )
            self.conversation_history.append(
                {"role": "assistant", "content": response.content}
            )
            logger.info(f"💾 Historial: {len(self.conversation_history)} mensajes")

        return response

    def summarize_notes(
        self,
        notes_content: str,
        style: str = 'concise',
        **kwargs
    ) -> ClaudeResponse:
        """
        Resume un conjunto de notas.

        Args:
            notes_content: Contenido de las notas a resumir
            style: Estilo de resumen:
                - 'concise': Resumen breve
                - 'detailed': Resumen detallado
                - 'bullet_points': Puntos clave
            **kwargs: Argumentos adicionales

        Returns:
            ClaudeResponse con el resumen
        """
        logger.info(f"📝 Resumiendo notas (estilo: {style})")

        style_prompts = {
            'concise': 'Resume las siguientes notas de forma concisa (2-3 párrafos):',
            'detailed': 'Crea un resumen detallado de las siguientes notas, manteniendo conceptos clave y ejemplos:',
            'bullet_points': 'Extrae los puntos clave de las siguientes notas en formato de bullet points:'
        }

        prompt = f"{style_prompts.get(style, style_prompts['concise'])}\n\n{notes_content}"

        return self._call_api(
            system="Eres un asistente que ayuda a resumir notas académicas de forma clara y útil.",
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )

    def explain_concept(
        self,
        concept: str,
        context: str,
        depth: str = 'medium',
        **kwargs
    ) -> ClaudeResponse:
        """
        Explica un concepto basándose en las notas.

        Args:
            concept: Concepto a explicar
            context: Contexto de las notas
            depth: Profundidad de explicación:
                - 'simple': Explicación simple
                - 'medium': Explicación estándar
                - 'deep': Explicación profunda con ejemplos
            **kwargs: Argumentos adicionales

        Returns:
            ClaudeResponse con la explicación
        """
        depth_prompts = {
            'simple': 'Explica de forma simple y directa',
            'medium': 'Explica claramente con ejemplos',
            'deep': 'Proporciona una explicación profunda con ejemplos, casos de uso, y conexiones con otros conceptos'
        }

        prompt = f"""Basándote en las siguientes notas, {depth_prompts.get(depth, depth_prompts['medium'])} el concepto: {concept}

Notas:
{context}

Explica: {concept}"""

        return self._call_api(
            system=self.RAG_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )

    def clear_history(self) -> None:
        """Limpia el historial de conversación."""
        self.conversation_history = []
        logger.info("🗑️ Historial de conversación limpiado")

    def _build_rag_prompt(
        self,
        query: str,
        context: str,
        include_sources: bool
    ) -> str:
        """
        Construye prompt optimizado para RAG.

        Args:
            query: Query del usuario
            context: Contexto recuperado
            include_sources: Si incluir instrucción de citar fuentes

        Returns:
            Prompt formateado
        """
        source_instruction = ""
        if include_sources:
            source_instruction = "\n\nRecuerda citar las notas específicas que usas en tu respuesta."

        prompt = f"""A continuación te proporciono contexto de mis notas de Obsidian:

{context}

Pregunta: {query}{source_instruction}

Responde basándote únicamente en el contexto proporcionado."""

        return prompt

    def _call_api(
        self,
        system: str,
        messages: List[Dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ClaudeResponse:
        """
        Llama a la API de Anthropic.

        Args:
            system: System prompt
            messages: Lista de mensajes
            temperature: Override de temperatura
            max_tokens: Override de max_tokens
            **kwargs: Argumentos adicionales para la API

        Returns:
            ClaudeResponse parseada

        Raises:
            AnthropicError: Si hay error en la API
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature if temperature is not None else self.temperature,
                system=system,
                messages=messages,
                **kwargs
            )

            # Parsear respuesta
            content = response.content[0].text if response.content else ""

            return ClaudeResponse(
                content=content,
                model=response.model,
                tokens_input=response.usage.input_tokens,
                tokens_output=response.usage.output_tokens,
                stop_reason=response.stop_reason,
                metadata={
                    'id': response.id,
                    'timestamp': datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"❌ Error llamando a API de Claude: {e}")
            raise

    def get_info(self) -> Dict:
        """
        Información del cliente.

        Returns:
            Diccionario con configuración
        """
        return {
            'model': self.model_name,
            'model_id': self.model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'conversation_length': len(self.conversation_history),
            'timeout': self.timeout
        }


# ============================================
# Funciones de utilidad
# ============================================

def estimate_tokens(text: str) -> int:
    """
    Estima el número de tokens en un texto.

    Usa una aproximación simple (4 chars ≈ 1 token para inglés/español).

    Args:
        text: Texto a estimar

    Returns:
        Número estimado de tokens
    """
    return len(text) // 4


def truncate_context(
    context: str,
    max_tokens: int = 4000,
    preserve_documents: bool = True
) -> str:
    """
    Trunca contexto para que quepa en límite de tokens.

    Args:
        context: Contexto a truncar
        max_tokens: Límite de tokens
        preserve_documents: Si mantener documentos completos (no cortar a mitad)

    Returns:
        Contexto truncado
    """
    estimated_tokens = estimate_tokens(context)

    if estimated_tokens <= max_tokens:
        return context

    logger.warning(f"⚠️ Truncando contexto de ~{estimated_tokens} a ~{max_tokens} tokens")

    if preserve_documents:
        # Dividir por documentos y añadir hasta llenar límite
        docs = context.split('\n\n---')
        truncated_docs = []
        current_tokens = 0

        for doc in docs:
            doc_tokens = estimate_tokens(doc)
            if current_tokens + doc_tokens <= max_tokens:
                truncated_docs.append(doc)
                current_tokens += doc_tokens
            else:
                break

        return '\n\n---'.join(truncated_docs)
    else:
        # Truncar directamente
        max_chars = max_tokens * 4
        return context[:max_chars] + "\n\n[... contexto truncado ...]"


# ============================================
# Script de prueba
# ============================================

if __name__ == "__main__":
    """
    Script de prueba del cliente Claude.

    Requiere ANTHROPIC_API_KEY en variables de entorno.

    Ejecutar con:
        export ANTHROPIC_API_KEY=sk-...
        python src/claude_client.py
    """
    import sys

    print("🧪 Probando módulo claude_client...\n")

    # Verificar API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY no configurada")
        print("   export ANTHROPIC_API_KEY=sk-...")
        sys.exit(1)

    # Crear cliente
    try:
        client = ClaudeClient(model='haiku')  # Usar haiku para tests (más barato)
        print("✅ Cliente creado\n")
    except Exception as e:
        print(f"❌ Error creando cliente: {e}")
        sys.exit(1)

    # Test 1: Respuesta RAG simple
    print("📝 Test 1: Respuesta RAG")
    context = """--- Documento 1: QuickSort ---
QuickSort es un algoritmo de ordenamiento eficiente que usa la estrategia divide y conquista.
Complejidad promedio: O(n log n)

--- Documento 2: MergeSort ---
MergeSort también usa divide y conquista pero garantiza O(n log n) en el peor caso."""

    query = "¿Qué algoritmo de ordenamiento me recomiendas y por qué?"

    try:
        response = client.generate_rag_response(query, context)
        print(f"Query: {query}")
        print(f"Respuesta: {response.content[:200]}...")
        print(f"Tokens: {response.tokens_input + response.tokens_output}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

    # Test 2: Estimación de tokens
    print("📊 Test 2: Estimación de tokens")
    test_text = "Este es un texto de prueba para estimar tokens"
    tokens = estimate_tokens(test_text)
    print(f"Texto: '{test_text}'")
    print(f"Tokens estimados: {tokens}\n")

    # Info del cliente
    print("ℹ️ Info del cliente:")
    info = client.get_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    print("\n✅ Pruebas completadas!")
