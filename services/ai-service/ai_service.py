#!/usr/bin/env python3
"""
AUREON AI Service
=================
FastAPI-based AI proxy service with Ollama, OpenAI-compatible, and mock mode.
Privacy: logs nothing to disk, all in-memory.

Run: python3 aureon/services/ai-service/ai_service.py
"""

import json
import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

# ---------------------------------------------------------------------------
# Try FastAPI, fall back to stdlib http.server
# ---------------------------------------------------------------------------
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
    import httpx
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CONFIG_PATH = Path.home() / ".aureon" / "ai_config.json"
DEFAULT_CONFIG = {
    "mode": "mock",                        # "ollama" | "openai" | "mock"
    "ollama_endpoint": "http://localhost:11434",
    "openai_endpoint": "https://api.openai.com/v1",
    "openai_api_key": "",
    "default_model": "llama3",
    "temperature": 0.7,
    "max_tokens": 1024,
    "service_host": "127.0.0.1",
    "service_port": 8766
}

def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                user = json.load(f)
            cfg = {**DEFAULT_CONFIG, **user}
            return cfg
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)

CONFIG = load_config()

# ---------------------------------------------------------------------------
# In-memory request log (never written to disk)
# ---------------------------------------------------------------------------
REQUEST_LOG: List[Dict] = []
MAX_LOG_ENTRIES = 500

def log_request(endpoint: str, model: str, success: bool):
    if len(REQUEST_LOG) >= MAX_LOG_ENTRIES:
        REQUEST_LOG.pop(0)
    REQUEST_LOG.append({
        "ts": time.time(),
        "endpoint": endpoint,
        "model": model,
        "success": success
    })

# ---------------------------------------------------------------------------
# AI Backend Implementations
# ---------------------------------------------------------------------------

async def call_ollama(messages: List[Dict], model: str, temperature: float, max_tokens: int) -> str:
    endpoint = CONFIG["ollama_endpoint"]
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{endpoint}/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "") or data.get("response", "")


async def call_openai_compatible(
    messages: List[Dict],
    model: str,
    temperature: float,
    max_tokens: int,
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None
) -> str:
    base = endpoint or CONFIG["openai_endpoint"]
    key = api_key or CONFIG.get("openai_api_key", "")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{base}/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def mock_response(messages: List[Dict]) -> str:
    """Rule-based mock AI for offline use."""
    last_user = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
    )
    t = last_user.lower().strip()

    if any(x in t for x in ["hello", "hi", "hey"]):
        return "Hello! I'm Aureon AI running in mock mode. For real AI responses, configure Ollama or an OpenAI-compatible API."

    if "time" in t:
        return f"The current time is {time.strftime('%H:%M:%S')} (server time)."

    if "help" in t:
        return (
            "I'm Aureon AI Service in mock mode.\n"
            "Real capabilities require Ollama (local) or an OpenAI-compatible API.\n"
            "Configure via ~/.aureon/ai_config.json"
        )

    if "summarize" in t or "summary" in t:
        return "To summarize text, use the POST /summarize endpoint with your text in the request body."

    return (
        f"[Mock mode] I received: '{last_user[:100]}'. "
        "Configure an AI backend in ~/.aureon/ai_config.json for real responses."
    )


# ---------------------------------------------------------------------------
# File search ranking
# ---------------------------------------------------------------------------

def rank_files_by_relevance(query: str, files: List[Dict]) -> List[Dict]:
    """Simple keyword-based relevance ranking."""
    keywords = set(query.lower().split())
    scored = []
    for f in files:
        name = f.get("name", "").lower()
        path = f.get("path", "").lower()
        score = sum(2 if kw in name else (1 if kw in path else 0) for kw in keywords)
        scored.append({**f, "_score": score})
    return sorted(scored, key=lambda x: x["_score"], reverse=True)


# ===========================================================================
# FastAPI Application
# ===========================================================================

if HAS_FASTAPI:

    app = FastAPI(
        title="AUREON AI Service",
        description="Local AI proxy for AUREON OS",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Pydantic models ----

    class Message(BaseModel):
        role: str
        content: str

    class ChatRequest(BaseModel):
        messages: List[Message]
        model: Optional[str] = None
        temperature: Optional[float] = None
        max_tokens: Optional[int] = None
        endpoint: Optional[str] = None
        api_key: Optional[str] = None
        mode: Optional[str] = None  # "ollama" | "openai" | "mock"

    class SummarizeRequest(BaseModel):
        text: str
        model: Optional[str] = None
        max_length: Optional[int] = 200

    class SearchFilesRequest(BaseModel):
        query: str
        files: List[Dict[str, Any]]
        top_k: Optional[int] = 10

    # ---- Endpoints ----

    @app.get("/status")
    async def status():
        """Health check."""
        ollama_ok = False
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{CONFIG['ollama_endpoint']}/api/tags")
                ollama_ok = r.status_code == 200
        except Exception:
            pass

        return {
            "status": "ok",
            "mode": CONFIG["mode"],
            "ollama_available": ollama_ok,
            "ollama_endpoint": CONFIG["ollama_endpoint"],
            "version": "1.0.0",
            "uptime_requests": len(REQUEST_LOG)
        }

    @app.get("/models")
    async def list_models():
        """List available Ollama models."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{CONFIG['ollama_endpoint']}/api/tags")
                r.raise_for_status()
                data = r.json()
                models = [
                    {
                        "name": m["name"],
                        "size": m.get("size", 0),
                        "modified_at": m.get("modified_at", ""),
                        "source": "ollama"
                    }
                    for m in data.get("models", [])
                ]
                return {"models": models, "source": "ollama"}
        except Exception as e:
            return {
                "models": [
                    {"name": "mock", "source": "built-in", "size": 0}
                ],
                "source": "mock",
                "error": str(e)
            }

    @app.post("/chat")
    async def chat(req: ChatRequest):
        """Proxy chat to Ollama / OpenAI / mock."""
        messages = [{"role": m.role, "content": m.content} for m in req.messages]
        model = req.model or CONFIG["default_model"]
        temperature = req.temperature if req.temperature is not None else CONFIG["temperature"]
        max_tokens = req.max_tokens or CONFIG["max_tokens"]
        mode = req.mode or CONFIG["mode"]

        try:
            if mode == "ollama":
                content = await call_ollama(messages, model, temperature, max_tokens)
                log_request("chat", f"ollama/{model}", True)
            elif mode == "openai":
                content = await call_openai_compatible(
                    messages, model, temperature, max_tokens,
                    endpoint=req.endpoint,
                    api_key=req.api_key
                )
                log_request("chat", f"openai/{model}", True)
            else:
                content = mock_response(messages)
                log_request("chat", "mock", True)

            return {
                "message": {"role": "assistant", "content": content},
                "model": model,
                "mode": mode
            }

        except httpx.ConnectError:
            log_request("chat", model, False)
            # Fall back to mock
            content = mock_response(messages)
            return {
                "message": {"role": "assistant", "content": content},
                "model": "mock",
                "mode": "mock",
                "fallback": True,
                "error": "Could not connect to AI backend; using mock mode."
            }
        except Exception as e:
            log_request("chat", model, False)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/summarize")
    async def summarize(req: SummarizeRequest):
        """Summarize text using AI."""
        messages = [
            {
                "role": "system",
                "content": "You are a concise summarization assistant. Summarize the given text clearly and briefly."
            },
            {
                "role": "user",
                "content": f"Please summarize the following text in {req.max_length} words or less:\n\n{req.text}"
            }
        ]
        model = req.model or CONFIG["default_model"]
        mode = CONFIG["mode"]

        try:
            if mode == "ollama":
                summary = await call_ollama(messages, model, 0.3, req.max_length * 5)
            elif mode == "openai":
                summary = await call_openai_compatible(messages, model, 0.3, req.max_length * 5)
            else:
                # Simple mock summarization
                words = req.text.split()
                if len(words) <= req.max_length:
                    summary = req.text
                else:
                    summary = " ".join(words[:req.max_length]) + "..."
                    summary = f"[Mock summary] {summary}"

            return {"summary": summary, "original_length": len(req.text), "model": model}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/search-files")
    async def search_files(req: SearchFilesRequest):
        """Search and rank files using AI-powered relevance scoring."""
        ranked = rank_files_by_relevance(req.query, req.files)
        top = ranked[:req.top_k]
        # Remove internal score field
        for f in top:
            f.pop("_score", None)
        return {"results": top, "query": req.query, "total_searched": len(req.files)}

    @app.get("/stats")
    async def stats():
        """In-memory request stats (never written to disk)."""
        if not REQUEST_LOG:
            return {"total": 0, "success_rate": 1.0, "by_endpoint": {}}
        total = len(REQUEST_LOG)
        successful = sum(1 for r in REQUEST_LOG if r["success"])
        by_endpoint: Dict[str, int] = {}
        for r in REQUEST_LOG:
            by_endpoint[r["endpoint"]] = by_endpoint.get(r["endpoint"], 0) + 1
        return {
            "total": total,
            "successful": successful,
            "success_rate": successful / total,
            "by_endpoint": by_endpoint
        }

    def run_fastapi():
        host = CONFIG["service_host"]
        port = CONFIG["service_port"]
        print(f"[AUREON AI Service] Starting FastAPI on http://{host}:{port}")
        print(f"[AUREON AI Service] Mode: {CONFIG['mode']}")
        print(f"[AUREON AI Service] Docs: http://{host}:{port}/docs")
        uvicorn.run(app, host=host, port=port, log_level="warning")


# ===========================================================================
# Fallback stdlib HTTP server (no FastAPI)
# ===========================================================================

else:
    import http.server
    import urllib.request
    import urllib.error
    import threading

    class AureonAIHandler(http.server.BaseHTTPRequestHandler):
        """Minimal stdlib HTTP handler for the AI service."""

        def log_message(self, format, *args):
            pass  # Suppress default logging

        def send_json(self, data: dict, code: int = 200):
            body = json.dumps(data).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.end_headers()
            self.wfile.write(body)

        def read_body(self) -> dict:
            length = int(self.headers.get("Content-Length", 0))
            if length:
                return json.loads(self.rfile.read(length))
            return {}

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.end_headers()

        def do_GET(self):
            if self.path == "/status":
                self.send_json({
                    "status": "ok",
                    "mode": CONFIG["mode"],
                    "version": "1.0.0",
                    "fastapi": False
                })
            elif self.path == "/models":
                try:
                    req = urllib.request.urlopen(
                        f"{CONFIG['ollama_endpoint']}/api/tags", timeout=3
                    )
                    data = json.loads(req.read())
                    models = [{"name": m["name"], "source": "ollama"} for m in data.get("models", [])]
                    self.send_json({"models": models})
                except Exception:
                    self.send_json({"models": [{"name": "mock", "source": "built-in"}]})
            else:
                self.send_json({"error": "Not found"}, 404)

        def do_POST(self):
            body = self.read_body()

            if self.path == "/chat":
                messages = body.get("messages", [])
                content = mock_response(messages)
                self.send_json({
                    "message": {"role": "assistant", "content": content},
                    "model": "mock",
                    "mode": "mock"
                })
            elif self.path == "/summarize":
                text = body.get("text", "")
                words = text.split()
                max_len = body.get("max_length", 200)
                summary = " ".join(words[:max_len]) + ("..." if len(words) > max_len else "")
                self.send_json({"summary": summary, "original_length": len(text)})
            elif self.path == "/search-files":
                query = body.get("query", "")
                files = body.get("files", [])
                top_k = body.get("top_k", 10)
                ranked = rank_files_by_relevance(query, files)[:top_k]
                for f in ranked:
                    f.pop("_score", None)
                self.send_json({"results": ranked, "query": query})
            else:
                self.send_json({"error": "Not found"}, 404)

    def run_stdlib():
        host = CONFIG["service_host"]
        port = CONFIG["service_port"]
        print(f"[AUREON AI Service] Starting stdlib HTTP server on http://{host}:{port}")
        print(f"[AUREON AI Service] Mode: mock (install fastapi+uvicorn for full features)")
        server = http.server.HTTPServer((host, port), AureonAIHandler)
        server.serve_forever()


# ===========================================================================
# Entry Point
# ===========================================================================

if __name__ == "__main__":
    # Ensure config dir exists
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Write default config if missing
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"[AUREON AI Service] Created default config at {CONFIG_PATH}")

    if HAS_FASTAPI:
        run_fastapi()
    else:
        print("[AUREON AI Service] FastAPI not available. Install with:")
        print("  pip3 install fastapi uvicorn httpx pydantic")
        print("[AUREON AI Service] Starting minimal stdlib fallback...")
        run_stdlib()
