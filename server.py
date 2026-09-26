"""Local web interface for IKEAssist. Run with: python server.py."""
import ast
import importlib.util
import json
import logging
import os
import socket
import threading
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODEL_LOCK = threading.Lock()
pipeline = None


class IKEAssistServer(ThreadingHTTPServer):
    # Windows address reuse can let two servers answer on the same port.
    allow_reuse_address = os.name != "nt"
    allow_reuse_port = False

    def server_bind(self):
        if os.name == "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def answer(question):
    global pipeline
    with MODEL_LOCK:
        if pipeline is None:
            from langchain_ollama import OllamaLLM
            from langchain_core.prompts import ChatPromptTemplate
            from vector import retriever
            prompt = ChatPromptTemplate.from_template(
                "You are IKEAssist, a helpful IKEA product assistant. Answer only from "
                "the supplied product descriptions. Explain when information is missing. "
                "Prices are a July 2025 snapshot. Use readable paragraphs or short lists. "
                "Product descriptions: {products}\nQuestion: {question}"
            )
            pipeline = (retriever, prompt | OllamaLLM(model="llama3.2", client_kwargs={"timeout": 180}))
        retriever, chain = pipeline
        products = retriever.invoke(question)
        result = chain.invoke({"products": "\n\n".join(p.page_content for p in products), "question": question})
        sources = []
        for doc in products:
            sections = []
            for line in doc.page_content.splitlines():
                try:
                    value = ast.literal_eval(line)
                    if isinstance(value, dict):
                        sections.append(value)
                except (ValueError, SyntaxError):
                    pass
            data = {str(k).lower(): v for section in sections for k, v in section.items()}
            sources.append({"name": data.get("name", "IKEA product"), "description": data.get("description", doc.page_content[:250]), "price": data.get("price"), "url": data.get("url", "")})
        return {"answer": result, "sources": sources}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "frontend"), **kwargs)

    def log_message(self, format, *args):
        # Keep routine browser requests out of the terminal.
        if getattr(self, "command", None) in ("GET", "HEAD"):
            return
        super().log_message(format, *args)

    def end_headers(self):
        if self.command in ("GET", "HEAD"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/favicon.ico":
            # Browsers may request an icon even when the page has none.
            self.send_response(204)
            self.end_headers()
        elif self.path == "/api/status":
            if any(importlib.util.find_spec(name) is None for name in ("langchain_ollama", "langchain_chroma", "commercetxt")):
                self.send_json(200, {"ready": False, "message": "Python setup needed"})
                return
            try:
                with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as response:
                    names = {m["name"].split(":")[0] for m in json.load(response).get("models", [])}
                ready = {"llama3.2", "mxbai-embed-large"}.issubset(names)
                self.send_json(200, {"ready": ready, "message": "Ready to explore" if ready else "Required models missing"})
            except (OSError, ValueError):
                self.send_json(200, {"ready": False, "message": "Ollama is offline"})
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_json(404, {"error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 20000:
                raise ValueError("Invalid request size")
            data = json.loads(self.rfile.read(length))
            question = data.get("question") if isinstance(data, dict) else None
            if not isinstance(question, str) or not question.strip() or len(question) > 4000:
                raise ValueError("Enter a question of up to 4,000 characters.")
        except (ValueError, UnicodeDecodeError) as exc:
            self.send_json(400, {"error": str(exc)})
            return
        try:
            self.send_json(200, answer(question.strip()))
        except ImportError:
            logging.exception("Missing Python dependency")
            self.send_json(503, {"error": "A Python dependency is missing. Install the project requirements in your active environment, restart the server, and try again."})
        except Exception:
            logging.exception("Unable to answer question")
            self.send_json(503, {"error": "The assistant could not connect to its models. Start Ollama and make sure llama3.2 and mxbai-embed-large are installed, then try again."})


if __name__ == "__main__":
    os.chdir(ROOT)
    try:
        server = IKEAssistServer(("127.0.0.1", 8000), Handler)
    except OSError as exc:
        raise SystemExit(
            "Could not start IKEAssist on port 8000. Stop the existing server "
            f"with Ctrl+C before running this script again. ({exc})"
        ) from exc
    with server:
        print("IKEAssist is running at http://localhost:8000", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nIKEAssist stopped.", flush=True)
