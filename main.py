import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Listing, User

app = FastAPI(title="Readopt API", description="Backend for the Readopt used books marketplace")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Readopt backend running"}


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
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
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

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# DTOs for responses
class ListingOut(BaseModel):
    id: str
    title: str
    author: str
    price: float
    condition: str
    description: Optional[str]
    image_url: Optional[str]
    seller_name: str
    seller_email: str
    location: Optional[str]
    category: Optional[str]


@app.post("/api/listings", response_model=dict)
def create_listing(payload: Listing):
    try:
        inserted_id = create_document("listing", payload)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/listings", response_model=List[ListingOut])
def list_listings(q: Optional[str] = None, category: Optional[str] = None):
    try:
        filt = {}
        if category:
            filt["category"] = category
        # Simple text search approximation
        if q:
            filt["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"author": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"category": {"$regex": q, "$options": "i"}},
            ]
        docs = get_documents("listing", filt, limit=100)
        items: List[ListingOut] = []
        for d in docs:
            items.append(
                ListingOut(
                    id=str(d.get("_id")),
                    title=d.get("title"),
                    author=d.get("author"),
                    price=float(d.get("price", 0)),
                    condition=d.get("condition"),
                    description=d.get("description"),
                    image_url=d.get("image_url"),
                    seller_name=d.get("seller_name"),
                    seller_email=d.get("seller_email"),
                    location=d.get("location"),
                    category=d.get("category"),
                )
            )
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/listings/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: str):
    try:
        from bson.objectid import ObjectId
        doc = db["listing"].find_one({"_id": ObjectId(listing_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Listing not found")
        return ListingOut(
            id=str(doc.get("_id")),
            title=doc.get("title"),
            author=doc.get("author"),
            price=float(doc.get("price", 0)),
            condition=doc.get("condition"),
            description=doc.get("description"),
            image_url=doc.get("image_url"),
            seller_name=doc.get("seller_name"),
            seller_email=doc.get("seller_email"),
            location=doc.get("location"),
            category=doc.get("category"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
