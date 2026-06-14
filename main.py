from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()

@app.get("/")
def root():
    return {"status": "online", "system": "JARVIS v6"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/web", response_class=HTMLResponse)
def web():
    try:
        return Path("index.html").read_text(encoding="utf-8")
    except:
        return "<h1>JARVIS v6 online</h1>"
