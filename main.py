import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Any
from pydantic import BaseModel

from database import db, get_documents

app = FastAPI(title="UMKM Lokal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductOut(BaseModel):
    id: str
    title: str
    price: float
    image_url: Optional[str] = None
    category: Optional[str] = None
    store_name: Optional[str] = None


@app.get("/")
def read_root():
    return {"message": "UMKM Lokal API Ready"}


@app.get("/api/products", response_model=List[ProductOut])
def list_products(q: Optional[str] = Query(None, description="Search by title or category"), limit: int = Query(24, ge=1, le=100)):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    filter_dict: dict[str, Any] = {}
    if q:
        # Simple case-insensitive search on title or category
        filter_dict = {
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"category": {"$regex": q, "$options": "i"}},
            ]
        }

    # Fetch products
    products = get_documents("product", filter_dict, limit)

    # Map store ids to names (best-effort)
    store_ids = [p.get("store_id") for p in products if p.get("store_id")]
    stores_map = {}
    if store_ids:
        try:
            stores = list(db["store"].find({"_id": {"$in": [__import__('bson').ObjectId(s) if len(str(s)) == 24 else s for s in store_ids]}}))
            for s in stores:
                stores_map[str(s.get("_id"))] = s.get("name")
        except Exception:
            pass

    # Serialize output
    result: List[ProductOut] = []
    from bson import ObjectId

    for p in products:
        _id = p.get("_id")
        if isinstance(_id, ObjectId):
            pid = str(_id)
        else:
            pid = str(_id)
        result.append(
            ProductOut(
                id=pid,
                title=p.get("title"),
                price=float(p.get("price", 0)),
                image_url=p.get("image_url"),
                category=p.get("category"),
                store_name=stores_map.get(str(p.get("store_id"))) or stores_map.get(p.get("store_id"))
            )
        )

    return result


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
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

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
