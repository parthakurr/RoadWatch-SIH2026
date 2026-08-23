from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import engine, Base
from routers import detections, potholes, analytics, export

# Create SQLite tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RoadWatch Municipal Backend API",
    description="Central ingestion, spatial deduplication, GIS map service, and repair tracking API for RoadWatch SIH Project.",
    version="1.0.0"
)

# Enable CORS for React frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(detections.router)
app.include_router(potholes.router)
app.include_router(analytics.router)
app.include_router(export.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "RoadWatch Central Backend",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
