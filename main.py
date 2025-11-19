import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Product, DistributorApplication, CheckoutRequest

app = FastAPI(title="Luxuria API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Sample catalog (used when DB is empty or unavailable) --------

def sample_products() -> List[dict]:
    return [
        {
            "_id": "demo-royal-chrono",
            "title": "Royal Chrono 42mm",
            "description": "Swiss automatic chronograph crafted in 18k rose gold with sapphire crystal.",
            "price": 18990.0,
            "category": "watches",
            "images": [
                "https://images.unsplash.com/photo-1518544801976-3e188ea47b1d?q=80&w=1600&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?q=80&w=1600&auto=format&fit=crop"
            ],
            "in_stock": True,
            "featured": True,
        },
        {
            "_id": "demo-diamond-aurora",
            "title": "Aurora Diamond Necklace",
            "description": "Hand-set VS1 diamonds on platinum. Timeless brilliance for evening glamour.",
            "price": 12950.0,
            "category": "jewelry",
            "images": [
                "https://images.unsplash.com/photo-1520962918287-7448c2878f65?q=80&w=1600&auto=format&fit=crop"
            ],
            "in_stock": True,
            "featured": True,
        },
        {
            "_id": "demo-maldives-escape",
            "title": "Maldives Water Villa Escape",
            "description": "5 nights in an overwater villa with private plunge pool and butler service.",
            "price": 8990.0,
            "category": "holidays",
            "images": [
                "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?q=80&w=1600&auto=format&fit=crop"
            ],
            "in_stock": True,
            "featured": True,
        },
        {
            "_id": "demo-silk-sofa",
            "title": "Silk & Walnut Lounge Sofa",
            "description": "Handcrafted Italian sofa in walnut with bespoke silk upholstery.",
            "price": 7490.0,
            "category": "home",
            "images": [
                "https://images.unsplash.com/photo-1501045661006-fcebe0257c3f?q=80&w=1600&auto=format&fit=crop"
            ],
            "in_stock": True,
            "featured": False,
        },
        {
            "_id": "demo-platinum-massager",
            "title": "Platinum Deep Tissue Massager",
            "description": "Medical-grade percussive therapy device with intelligent pressure control.",
            "price": 499.0,
            "category": "health",
            "images": [
                "https://images.unsplash.com/photo-1615634260167-c8cdede054de?q=80&w=1600&auto=format&fit=crop"
            ],
            "in_stock": True,
            "featured": False,
        },
    ]

CATEGORIES = [
    {"id": "watches", "name": "Watches"},
    {"id": "jewelry", "name": "Jewelry"},
    {"id": "holidays", "name": "Holiday Destinations"},
    {"id": "home", "name": "Home Living"},
    {"id": "health", "name": "Health"},
]

# ----------------------------- Routes ---------------------------------

@app.get("/")
def read_root():
    return {"message": "Luxuria backend is running"}

@app.get("/api/categories")
def get_categories():
    return CATEGORIES

@app.get("/api/products")
def list_products(category: Optional[str] = None, featured: Optional[bool] = None):
    # Try DB first; if unavailable or empty, return sample catalog
    try:
        filter_query = {}
        if category:
            filter_query["category"] = category
        if featured is not None:
            filter_query["featured"] = featured
        docs = get_documents("product", filter_query, limit=100)
        for d in docs:
            d["_id"] = str(d.get("_id"))
            if "images" in d:
                d["images"] = [str(x) for x in d["images"]]
        if docs:
            return docs
    except Exception:
        pass
    # Fallback to samples and filter locally
    prods = sample_products()
    if category:
        prods = [p for p in prods if p["category"] == category]
    if featured is not None:
        prods = [p for p in prods if p.get("featured") is featured]
    return prods

@app.get("/api/products/{product_id}")
def get_product(product_id: str):
    # Try DB by _id
    try:
        from bson import ObjectId
        if ObjectId.is_valid(product_id):
            docs = get_documents("product", {"_id": ObjectId(product_id)}, limit=1)
            if docs:
                d = docs[0]
                d["_id"] = str(d.get("_id"))
                if "images" in d:
                    d["images"] = [str(x) for x in d["images"]]
                return d
    except Exception:
        pass
    # Fallback to sample by id
    for p in sample_products():
        if p["_id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/api/products")
def create_product(product: Product):
    try:
        inserted_id = create_document("product", product)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/checkout")
def checkout(data: CheckoutRequest):
    try:
        order_id = create_document("order", data.model_dump())
        return {"status": "success", "order_id": order_id}
    except Exception:
        # If DB not available, still return success demo
        return {"status": "success", "order_id": "demo-order-1234"}

@app.post("/api/distributor/apply")
def distributor_apply(apply: DistributorApplication):
    try:
        app_id = create_document("distributorapplication", apply)
        return {"status": "received", "application_id": app_id}
    except Exception:
        return {"status": "received", "application_id": "demo-application-1234"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
