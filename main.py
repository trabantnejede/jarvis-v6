Výborně. TRUTH LAYER je v databázi.
Teď přidáme CONTROL LAYER — tvoje kontrolní tlačítka. Jdi na github.com/trabantnejede/jarvis-v6 → klikni na main.py → tužka ✏️ → smaž vše a vlož toto:
pythonfrom fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import os
import asyncpg

app = FastAPI(title="JARVIS v6 - Automotive OS")

DATABASE_URL = os.getenv("DATABASE_URL", "")

async def get_db():
    return await asyncpg.connect(DATABASE_URL)

class Product(BaseModel):
    ean: Optional[str] = None
    oem: Optional[str] = None
    name: str
    brand: str
    price_buy: float
    margin_pct: float = 25.0
    stock: int = 0
    status: str = "ACTIVE"

@app.get("/")
def root():
    return {"status": "online", "system": "JARVIS v6", "modules": 11, "version": "0.4.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/web", response_class=HTMLResponse)
def web():
    try:
        return Path("index.html").read_text(encoding="utf-8")
    except:
        return "<h1>JARVIS v6 online</h1>"

@app.get("/jarvis/status")
async def jarvis_status():
    try:
        db = await get_db()
        rows = await db.fetch("SELECT flag_name, flag_value FROM governance")
        await db.close()
        flags = {r["flag_name"]: r["flag_value"] for r in rows}
        mode = flags.get("system_mode", "NORMAL")
    except:
        flags = {}
        mode = "UNKNOWN"
    return {
        "system": "JARVIS v6",
        "status": mode,
        "governance": flags,
        "modules": {
            "feed_engine": "ready",
            "pricing_engine": "online",
            "product_validator": "online",
            "truth_layer": "online",
            "control_layer": "online",
            "order_engine": "pending",
            "tracking_engine": "pending",
            "security_engine": "pending",
            "legal_engine": "pending",
            "ai_helpdesk": "pending",
            "monitoring": "pending"
        }
    }

@app.post("/control/stop_checkout")
async def stop_checkout():
    db = await get_db()
    await db.execute("UPDATE governance SET flag_value='false', updated_at=NOW() WHERE flag_name='checkout_enabled'")
    await db.execute("INSERT INTO event_log (entity, action, new_value, reason) VALUES ('system', 'STOP_CHECKOUT', 'false', 'Manual override')")
    await db.close()
    return {"action": "STOP_CHECKOUT", "status": "done"}

@app.post("/control/start_checkout")
async def start_checkout():
    db = await get_db()
    await db.execute("UPDATE governance SET flag_value='true', updated_at=NOW() WHERE flag_name='checkout_enabled'")
    await db.execute("INSERT INTO event_log (entity, action, new_value, reason) VALUES ('system', 'START_CHECKOUT', 'true', 'Manual override')")
    await db.close()
    return {"action": "START_CHECKOUT", "status": "done"}

@app.post("/control/safe_mode")
async def safe_mode():
    db = await get_db()
    await db.execute("UPDATE governance SET flag_value='SAFE', updated_at=NOW() WHERE flag_name='system_mode'")
    await db.execute("UPDATE governance SET flag_value='false', updated_at=NOW() WHERE flag_name='checkout_enabled'")
    await db.execute("INSERT INTO event_log (entity, action, new_value, reason) VALUES ('system', 'SAFE_MODE', 'SAFE', 'Manual override')")
    await db.close()
    return {"action": "SAFE_MODE", "status": "activated", "warning": "Checkout disabled"}

@app.post("/control/normal_mode")
async def normal_mode():
    db = await get_db()
    await db.execute("UPDATE governance SET flag_value='NORMAL', updated_at=NOW() WHERE flag_name='system_mode'")
    await db.execute("UPDATE governance SET flag_value='true', updated_at=NOW() WHERE flag_name='checkout_enabled'")
    await db.execute("INSERT INTO event_log (entity, action, new_value, reason) VALUES ('system', 'NORMAL_MODE', 'NORMAL', 'Manual override')")
    await db.close()
    return {"action": "NORMAL_MODE", "status": "activated"}

@app.post("/control/freeze_sku/{product_id}")
async def freeze_sku(product_id: int):
    db = await get_db()
    await db.execute("UPDATE products SET status='PRICE_FROZEN', reason_code='MANUAL_FREEZE', updated_at=NOW() WHERE id=$1", product_id)
    await db.execute("INSERT INTO event_log (entity, entity_id, action, new_value, reason) VALUES ('product', $1, 'FREEZE_SKU', 'PRICE_FROZEN', 'Manual freeze')", product_id)
    await db.close()
    return {"action": "FREEZE_SKU", "product_id": product_id, "status": "frozen"}

@app.post("/pricing/calculate")
def calculate_price(product: Product):
    price_sell = product.price_buy * (1 + product.margin_pct / 100)
    profit = price_sell - product.price_buy
    status = "OK"
    if product.margin_pct < 12:
        status = "LOW_MARGIN"
    if product.stock == 0:
        status = "OUT_OF_STOCK"
    return {"name": product.name, "price_buy": product.price_buy, "price_sell": round(price_sell, 2), "profit": round(profit, 2), "margin_pct": product.margin_pct, "stock": product.stock, "status": status}

@app.post("/products/validate")
def validate_product(product: Product):
    issues = []
    if product.price_buy <= 0:
        issues.append("INVALID_PRICE")
    if product.stock < 0:
        issues.append("INVALID_STOCK")
    if not product.name:
        issues.append("MISSING_NAME")
    if product.margin_pct < 12:
        issues.append("LOW_MARGIN")
    if not product.ean and not product.oem:
        issues.append("MISSING_IDENTIFIER")
    return {"valid": len(issues) == 0, "issues": issues, "product": product.name, "recommendation": "BLOCK" if len(issues) > 0 else "PUBLISH"}

@app.get("/suppliers")
async def list_suppliers():
    try:
        db = await get_db()
        rows = await db.fetch("SELECT * FROM suppliers ORDER BY name")
        await db.close()
        return [dict(r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/control/pause_supplier/{supplier_code}")
async def pause_supplier(supplier_code: str):
    db = await get_db()
    await db.execute("UPDATE suppliers SET status='PAUSED' WHERE code=$1", supplier_code)
    await db.execute("INSERT INTO event_log (entity, action, new_value, reason) VALUES ('supplier', 'PAUSE_SUPPLIER', $1, 'Manual pause')", supplier_code)
    await db.close()
    return {"action": "PAUSE_SUPPLIER", "supplier": supplier_code, "status": "paused"}
Pak "Commit changes".
