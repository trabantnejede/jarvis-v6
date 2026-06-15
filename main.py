from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"status": "online", "system": "JARVIS v6", "version": "0.8.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/web", response_class=HTMLResponse)
def web():
    try:
        return Path("index.html").read_text(encoding="utf-8")
    except:
        return "<h1>JARVIS v6</h1>"

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    try:
        return Path("dashboard.html").read_text(encoding="utf-8")
    except:
        return "<h1>Dashboard</h1>"

@app.get("/jarvis/status")
def status():
    return {"system": "JARVIS v6", "status": "NORMAL", "version": "0.8.0"}

@app.get("/orders")
def orders():
    return {"total": 0, "orders": []}

@app.get("/suppliers")
def suppliers():
    return {"suppliers": [{"code": "ELIT_CZ", "name": "Elit CZ", "status": "ACTIVE"}, {"code": "INTER_CARS", "name": "Inter Cars", "status": "ACTIVE"}]}

@app.get("/products/search")
def search(q: str = ""):
    products = [
        {"id": 1, "name": "Brzdove desticky Bosch", "brand": "Bosch", "oem": "0986494534", "price_sell": 562.5, "stock": 15, "category": "Brzdy", "car_brand": "Skoda", "car_model": "Octavia"},
        {"id": 2, "name": "Olej Castrol 5W-30", "brand": "Castrol", "oem": "W712", "price_sell": 409.6, "stock": 42, "category": "Oleje", "car_brand": None, "car_model": None},
        {"id": 3, "name": "Olejovy filtr Mann", "brand": "Mann", "oem": "OC67", "price_sell": 110.5, "stock": 28, "category": "Filtry", "car_brand": "VW", "car_model": "Golf"},
    ]
    if q:
        products = [p for p in products if q.lower() in p["name"].lower() or q.lower() in p["brand"].lower()]
    return {"total": len(products), "results": products}

@app.post("/control/normal_mode")
def normal_mode():
    return {"action": "NORMAL_MODE", "status": "activated"}

@app.post("/control/safe_mode")
def safe_mode():
    return {"action": "SAFE_MODE", "status": "activated"}

@app.post("/control/stop_checkout")
def stop_checkout():
    return {"action": "STOP_CHECKOUT", "status": "done"}

@app.post("/control/start_checkout")
def start_checkout():
    return {"action": "START_CHECKOUT", "status": "done"}
