from fastapi import FastAPI

app = FastAPI(title="JARVIS v6 - Automotive OS")

@app.get("/")
def root():
    return {
        "status": "online",
        "system": "JARVIS v6",
        "modules": 11
    }

@app.get("/health")
def health():
    return {"status": "ok"}
