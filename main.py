from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(title="JARVIS v6 - Automotive OS")

# ─── MODELY ────────────────────────────────────────────
class Product(BaseModel):
    ean: Optional[str] = None
    oem: Optional[str] = None
    name: str
    brand: str
    price_buy: float
    margin_pct: float = 25.0
    stock: int = 0
    status: str = "ACTIVE"

# ─── ZÁKLADNÍ ENDPOINTY ────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "online",
        "system": "JARVIS v6",
        "modules": 11,
        "version": "0.2.0"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

# ─── PRICING ENGINE ────────────────────────────────────
@app.post("/pricing/calculate")
def calculate_price(product: Product):
    price_sell = product.price_buy * (1 + product.margin_pct / 100)
    profit = price_sell - product.price_buy
    
    status = "OK"
    if product.margin_pct < 12:
        status = "LOW_MARGIN"
    if product.stock == 0:
        status = "OUT_OF_STOCK"
    
    return {
        "name": product.name,
        "price_buy": product.price_buy,
        "price_sell": round(price_sell, 2),
        "profit": round(profit, 2),
        "margin_pct": product.margin_pct,
        "stock": product.stock,
        "status": status
    }

# ─── PRODUCT VALIDATOR ─────────────────────────────────
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
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "product": product.name,
        "recommendation": "BLOCK" if len(issues) > 0 else "PUBLISH"
    }

# ─── JARVIS STATUS ─────────────────────────────────────
@app.get("/jarvis/status")
def jarvis_status():
    return {
        "system": "JARVIS v6",
        "status": "NORMAL",
        "modules": {
            "feed_engine": "ready",
            "pricing_engine": "online",
            "product_validator": "online",
            "order_engine": "pending",
            "tracking_engine": "pending",
            "security_engine": "pending",
            "legal_engine": "pending",
            "ai_helpdesk": "pending",
            "monitoring": "pending"
        }
    }
    from fastapi.responses import HTMLResponse
from pathlib import Path

@app.get("/web", response_class=HTMLResponse)
def web():
    return Path("index.html").read_text(encoding="utf-8")
