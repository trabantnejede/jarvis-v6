from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path

app = FastAPI(title="JARVIS v6 - Automotive OS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Product(BaseModel):
    ean: Optional[str] = None
    oem: Optional[str] = None
    name: str
    brand: str
    price_buy: float
    margin_pct: float = 25.0
    stock: int = 0
    status: str = "ACTIVE"


class OrderItem(BaseModel):
    product_name: str
    ean: Optional[str] = None
    oem: Optional[str] = None
    quantity: int = 1
    price_unit: float
    supplier_code: Optional[str] = "ELIT_CZ"


class Order(BaseModel):
    customer_email: str
    customer_name: str
    delivery_address: str
    items: List[OrderItem]


@app.get("/")
def root():
    return {"status": "online", "system": "JARVIS v6", "version": "0.7.0", "modules": 11}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/web", response_class=HTMLResponse)
def web():
    try:
        return Path("index.html").read_text(encoding="utf-8")
    except Exception:
        return "<h1>JARVIS v6 online</h1>"


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    try:
        return Path("dashboard.html").read_text(encoding="utf-8")
    except Exception:
        return "<h1>Dashboard nenalezen</h1>"


@app.get("/jarvis/status")
def jarvis_status():
    return {
        "system": "JARVIS v6",
        "status": system_mode["mode"],
        "version": "0.7.0",
        "modules": {
            "feed_engine": "ready",
            "pricing_engine": "online",
            "product_validator": "online",
            "order_engine": "online",
            "truth_layer": "online",
            "control_layer": "online",
            "tracking_engine": "pending",
            "security_engine": "pending",
            "legal_engine": "pending",
            "ai_helpdesk": "pending",
            "monitoring": "pending"
        }
    }


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


orders_db = []
order_counter = 1


@app.post("/orders/create")
def create_order(order: Order):
    global order_counter
    if not system_mode["checkout_enabled"]:
        return {"status": "REJECTED", "issues": ["CHECKOUT_DISABLED"], "order_id": None}
    issues = []
    if not order.customer_email:
        issues.append("MISSING_EMAIL")
    if not order.customer_name:
        issues.append("MISSING_NAME")
    if not order.delivery_address:
        issues.append("MISSING_ADDRESS")
    if not order.items:
        issues.append("NO_ITEMS")
    if issues:
        return {"status": "REJECTED", "issues": issues, "order_id": None}
    total = sum(item.price_unit * item.quantity for item in order.items)
    new_order = {
        "id": order_counter,
        "customer_email": order.customer_email,
        "customer_name": order.customer_name,
        "delivery_address": order.delivery_address,
        "items": [item.dict() for item in order.items],
        "price_total": round(total, 2),
        "status": "CREATED",
        "tracking_number": None,
        "reason_code": None
    }
    orders_db.append(new_order)
    order_counter += 1
    return {"status": "CREATED", "order_id": new_order["id"], "price_total": new_order["price_total"], "customer_email": order.customer_email}


@app.get("/orders")
def list_orders():
    return {"total": len(orders_db), "orders": orders_db}


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders_db:
        if order["id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Objednavka nenalezena")


@app.post("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for order in orders_db:
        if order["id"] == order_id:
            order["status"] = "CONFIRMED"
            order["reason_code"] = "MANUAL_CONFIRM"
            return {"order_id": order_id, "status": "CONFIRMED"}
    raise HTTPException(status_code=404, detail="Objednavka nenalezena")


@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int):
    for order in orders_db:
        if order["id"] == order_id:
            if order["status"] in ["CONFIRMED", "SENT_TO_SUPPLIER"]:
                return {"order_id": order_id, "error": "Nelze zrusit"}
            order["status"] = "CANCELLED"
            return {"order_id": order_id, "status": "CANCELLED"}
    raise HTTPException(status_code=404, detail="Objednavka nenalezena")


system_mode = {"mode": "NORMAL", "checkout_enabled": True}


@app.get("/control/status")
def control_status():
    return system_mode


@app.post("/control/stop_checkout")
def stop_checkout():
    system_mode["checkout_enabled"] = False
    system_mode["mode"] = "DEGRADED"
    return {"action": "STOP_CHECKOUT", "status": "done"}


@app.post("/control/start_checkout")
def start_checkout():
    system_mode["checkout_enabled"] = True
    system_mode["mode"] = "NORMAL"
    return {"action": "START_CHECKOUT", "status": "done"}


@app.post("/control/safe_mode")
def safe_mode():
    system_mode["checkout_enabled"] = False
    system_mode["mode"] = "SAFE"
    return {"action": "SAFE_MODE", "status": "activated"}


@app.post("/control/normal_mode")
def normal_mode():
    system_mode["checkout_enabled"] = True
    system_mode["mode"] = "NORMAL"
    return {"action": "NORMAL_MODE", "status": "activated"}
 
