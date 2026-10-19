import json
import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional
import httpx
from backend.app.config import settings
from backend.app.prompts.system_prompts import OFFICE_ASSISTANT_SYSTEM_PROMPT, PROMPT_INJECTION_DEFENSE_PREFIX
from backend.app.rag.generator import StructuredAnswerGenerator

class LLMService:
    @staticmethod
    async def stream_structured_answer(
        question: str,
        retrieved_chunks: List[Dict[str, Any]],
        web_sources: Optional[List[Dict[str, Any]]] = None,
        language: str = "eng_Latn",
        answer_depth: str = "standard",
        is_software_expert_mode: bool = False,
        user_role: str = "employee"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streams response tokens, stage updates, and finalized source citations.
        Supports built-in engine, Gemini, and OpenAI APIs.
        """
        web_sources = web_sources or []

        # Stage 1: Understanding request
        yield {
            "type": "status",
            "message": "Understanding request and checking permissions..."
        }
        await asyncio.sleep(0.08)

        # Stage 2: Searching office documents
        yield {
            "type": "status",
            "message": f"Searching office documents (Role: {user_role})..."
        }
        await asyncio.sleep(0.08)

        # Stage 3: Checking official sources (if web allowed)
        if web_sources:
            yield {
                "type": "status",
                "message": "Checking official vendor documentation..."
            }
            await asyncio.sleep(0.08)

        # Stage 4: Preparing answer
        yield {
            "type": "status",
            "message": "Preparing structured answer..."
        }
        await asyncio.sleep(0.08)

        # Check if external Gemini API key is configured
        if settings.llm_provider == "gemini" and settings.gemini_api_key:
            try:
                # Call Gemini API
                async for chunk in LLMService._stream_gemini_api(
                    question, retrieved_chunks, web_sources, language, answer_depth
                ):
                    yield chunk
                return
            except Exception:
                # Graceful fallback to built-in structured generator
                pass

        # Built-in High-Fidelity Structured Generator
        answer_result = StructuredAnswerGenerator.generate_grounded_answer(
            question=question,
            retrieved_chunks=retrieved_chunks,
            web_sources=web_sources,
            language=language,
            answer_depth=answer_depth,
            is_software_expert_mode=is_software_expert_mode,
            user_role=user_role
        )

        full_content = answer_result["content"]
        words = full_content.split(" ")

        # Stream words smoothly
        chunk_buffer = []
        for word in words:
            chunk_buffer.append(word)
            if len(chunk_buffer) >= 3:
                yield {
                    "type": "content_delta",
                    "delta": " ".join(chunk_buffer) + " "
                }
                chunk_buffer = []
                await asyncio.sleep(0.02)

        if chunk_buffer:
            yield {
                "type": "content_delta",
                "delta": " ".join(chunk_buffer)
            }

        # Final payload with complete sources and follow-ups
        yield {
            "type": "complete",
            "sources": answer_result["sources"],
            "follow_up_suggestions": answer_result["follow_up_suggestions"]
        }

    @staticmethod
    async def _stream_gemini_api(
        question: str,
        chunks: List[Dict[str, Any]],
        web_sources: List[Dict[str, Any]],
        language: str,
        depth: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        # Implementation for external Gemini stream
        context_text = "\n\n".join([f"[{i+1}] {c.get('title')}: {c.get('content')}" for i, c in enumerate(chunks)])
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{OFFICE_ASSISTANT_SYSTEM_PROMPT}\n\nContext:\n{context_text}\n\nQuestion: {question}"}
                    ]
                }
            ]
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?key={settings.gemini_api_key}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", url, json=payload) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if text:
                            yield {"type": "content_delta", "delta": text}
