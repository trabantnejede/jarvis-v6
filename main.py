Y
from fastapi import FastAPI, HTTPException, Query
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
    category: Optional[str] = None
    car_brand: Optional[str] = None
    car_model: Optional[str] = None
    price_buy: float
    margin_pct: float = 25.0
    stock: int = 0
    status: str = "ACTIVE"
    supplier_code: Optional[str] = "ELIT_CZ"
 
 
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
 
 
system_mode = {"mode": "NORMAL", "checkout_enabled": True}
orders_db = []
order_counter = 1
 
products_db = [
    {"id": 1, "ean": "4047024132609", "oem": "0986494534", "name": "Brzdove desticky Bosch", "brand": "Bosch", "category": "Brzdy", "car_brand": "Skoda", "car_model": "Octavia", "price_buy": 450.0, "margin_pct": 25.0, "price_sell": 562.5, "stock": 15, "status": "ACTIVE", "supplier_code": "ELIT_CZ"},
    {"id": 2, "ean": "4009026037204", "oem": "W712/16", "name": "Olej Castrol Edge 5W-30", "brand": "Castrol", "category": "Oleje", "car_brand": None, "car_model": None, "price_buy": 320.0, "margin_pct": 28.0, "price_sell": 409.6, "stock": 42, "status": "ACTIVE", "supplier_code": "INTER_CARS"},
    {"id": 3, "ean": "4009026041690", "oem": "OC67", "name": "Olejovy filtr Mann", "brand": "Mann", "category": "Filtry", "car_brand": "VW", "car_model": "Golf", "price_buy": 85.0, "margin_pct": 30.0, "price_sell": 110.5, "stock": 28, "status": "ACTIVE", "supplier_code": "ELIT_CZ"},
    {"id": 4, "ean": "4009026058162", "oem": "C26009", "name": "Vzduchovy filtr Purflux", "brand": "Purflux", "category": "Filtry", "car_brand": "Skoda", "car_model": "Fabia", "price_buy": 95.0, "margin_pct": 25.0, "price_sell": 118.75, "stock": 0, "status": "ACTIVE", "supplier_code": "ELIT_CZ"},
    {"id": 5, "ean": "3413523003204", "oem": "DF4052", "name": "Brzdovy kotouc Ferodo", "brand": "Ferodo", "category": "Brzdy", "car_brand": "Skoda", "car_model": "Octavia", "price_buy": 380.0, "margin_pct": 22.0, "price_sell": 463.6, "stock": 8, "status": "ACTIVE", "supplier_code": "INTER_CARS"},
    {"id": 6, "ean": "4047024321409", "oem": "1987432386", "name": "Klinovy remen Bosch", "brand": "Bosch", "category": "Remeny", "car_brand": "Ford", "car_model": "Focus", "price_buy": 220.0, "margin_pct": 20.0, "price_sell": 264.0, "stock": 5, "status": "ACTIVE", "supplier_code": "WENCO_SK"},
    {"id": 7, "ean": "4009026099027", "oem": "CU22003", "name": "Kabinovy filtr Mann", "brand": "Mann", "category": "Filtry", "car_brand": "VW", "car_model": "Passat", "price_buy": 120.0, "margin_pct": 30.0, "price_sell": 156.0, "stock": 19, "status": "ACTIVE", "supplier_code": "ELIT_CZ"},
    {"id": 8, "ean": "5901547774109", "oem": "SP203", "name": "Zapalovaci svicka NGK", "brand": "NGK", "category": "Svicky", "car_brand": "Skoda", "car_model": "Octavia", "price_buy": 65.0, "margin_pct": 35.0, "price_sell": 87.75, "stock": 0, "status": "RISKY", "supplier_code": "INTER_CARS"},
]
 
suppliers_db = [
    {"code": "ELIT_CZ", "name": "Elit CZ", "status": "ACTIVE", "contact": "info@elit.cz", "products": 4, "avg_delivery_days": 1},
    {"code": "INTER_CARS", "name": "Inter Cars CZ", "status": "ACTIVE", "contact": "info@intercars.cz", "products": 3, "avg_delivery_days": 2},
    {"code": "WENCO_SK", "name": "WENCO SK", "status": "ACTIVE", "contact": "info@wenco.sk", "products": 1, "avg_delivery_days": 3},
]
 
 
@app.get("/")
def root():
    return {"status": "online", "system": "JARVIS v6", "version": "0.8.0", "modules": 11}
 
 
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
        "version": "0.8.0",
        "modules": {
            "feed_engine": "ready",
            "pricing_engine": "online",
            "product_validator": "online",
            "order_engine": "online",
            "search_engine": "online",
            "supplier_engine": "online",
            "truth_layer": "online",
            "control_layer": "online",
            "tracking_engine": "pending",
            "security_engine": "pending",
            "legal_engine": "pending",
            "ai_helpdesk": "pending",
            "monitoring": "pending"
        }
    }
 
 
@app.get("/products/search")
def search_products(
    q: Optional[str] = Query(None, description="Hledat podle nazvu, OEM, EAN"),
    category: Optional[str] = Query(None),
    car_brand: Optional[str] = Query(None),
    car_model: Optional[str] = Query(None),
    supplier: Optional[str] = Query(None),
    in_stock: Optional[bool] = Query(None),
):
    results = products_db.copy()
 
    if q:
        q_lower = q.lower()
        results = [p for p in results if
            q_lower in p["name"].lower() or
            q_lower in (p["oem"] or "").lower() or
            q_lower in (p["ean"] or "").lower() or
            q_lower in p["brand"].lower()
        ]
 
    if category:
        results = [p for p in results if (p.get("category") or "").lower() == category.lower()]
 
    if car_brand:
        results = [p for p in results if (p.get("car_brand") or "").lower() == car_brand.lower()]
 
    if car_model:
        results = [p for p in results if (p.get("car_model") or "").lower() == car_model.lower()]
 
    if supplier:
        results = [p for p in results if (p.get("supplier_code") or "").lower() == supplier.lower()]
 
    if in_stock is not None:
        if in_stock:
            results = [p for p in results if p["stock"] > 0]
        else:
            results = [p for p in results if p["stock"] == 0]
 
    return {
        "total": len(results),
        "query": q,
        "filters": {"category": category, "car_brand": car_brand, "car_model": car_model},
        "results": results
    }
 
 
@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in products_db:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Produkt nenalezen")
 
 
@app.get("/products/categories/list")
def list_categories():
    categories = list(set(p["category"] for p in products_db if p.get("category")))
    return {"categories": sorted(categories)}
 
 
@app.get("/products/cars/list")
def list_cars():
    brands = list(set(p["car_brand"] for p in products_db if p.get("car_brand")))
    return {"car_brands": sorted(brands)}
 
 
@app.get("/suppliers")
def list_suppliers():
    return {"total": len(suppliers_db), "suppliers": suppliers_db}
 
 
@app.get("/suppliers/{supplier_code}")
def get_supplier(supplier_code: str):
    for s in suppliers_db:
        if s["code"] == supplier_code:
            products = [p for p in products_db if p.get("supplier_code") == supplier_code]
            return {**s, "product_list": products}
    raise HTTPException(status_code=404, detail="Dodavatel nenalezen")
 
 
@app.post("/control/pause_supplier/{supplier_code}")
def pause_supplier(supplier_code: str):
    for s in suppliers_db:
        if s["code"] == supplier_code:
            s["status"] = "PAUSED"
            return {"action": "PAUSE_SUPPLIER", "supplier": supplier_code, "status": "paused"}
    raise HTTPException(status_code=404, detail="Dodavatel nenalezen")
 
 
@app.post("/control/resume_supplier/{supplier_code}")
def resume_supplier(supplier_code: str):
    for s in suppliers_db:
        if s["code"] == supplier_code:
            s["status"] = "ACTIVE"
            return {"action": "RESUME_SUPPLIER", "supplier": supplier_code, "status": "active"}
    raise HTTPException(status_code=404, detail="Dodavatel nenalezen")
 
 
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
