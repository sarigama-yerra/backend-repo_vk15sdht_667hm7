import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List

from database import create_document
from schemas import Lead as LeadSchema

app = FastAPI(title="Syed Mehar Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Syed Mehar Portfolio Backend Running"}


@app.get("/api/testimonials")
def get_testimonials():
    """Return a curated set of real-style testimonials"""
    testimonials = [
        {
            "name": "Ayesha Khan",
            "role": "Product Manager",
            "company": "TaraTech",
            "avatar": "https://i.pravatar.cc/100?img=47",
            "quote": "Syed delivered our web app ahead of schedule with pixel-perfect execution. His attention to performance and UX reduced our bounce rate by 32%."
        },
        {
            "name": "Michael Chen",
            "role": "CTO",
            "company": "NovaLabs",
            "avatar": "https://i.pravatar.cc/100?img=12",
            "quote": "We migrated a legacy React/Node stack to a modern architecture. Syed led the effort end-to-end and cut our build times from minutes to seconds. Rock solid engineer."
        },
        {
            "name": "Fatima Al-Zahra",
            "role": "Founder",
            "company": "Bloom Wellness",
            "avatar": "https://i.pravatar.cc/100?img=5",
            "quote": "Our mobile app MVP launched smoothly on both iOS and Android. Syed’s communication and iteration speed were exceptional throughout."
        },
    ]
    return {"items": testimonials}


class LeadIn(BaseModel):
    name: str
    email: EmailStr
    message: str
    company: str | None = None
    budget: str | None = None
    source: str | None = "portfolio"


@app.post("/api/leads")
def create_lead(lead: LeadIn):
    """Store a contact/lead submission in the database"""
    try:
        lead_doc = LeadSchema(**lead.model_dump())
        inserted_id = create_document("lead", lead_doc)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        # Surface a readable error message for UI
        raise HTTPException(status_code=500, detail=str(e))


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
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
