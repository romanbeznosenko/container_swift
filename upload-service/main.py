"""
SWIFT Code Upload Service

A microservice for parsing and validating SWIFT codes from CSV files
and sending them to the main SWIFT code API.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.routers import upload_router
from utils.logger import setup_logger

load_dotenv()

logger = setup_logger("upload_service")

app = FastAPI(
    title="SWIFT Code Upload Service",
    description="API for parsing, validating, and uploading SWIFT codes from CSV files",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router.router)

@app.get("/", tags=["root"])
async def root():
    """Root endpoint that returns API information."""
    return {
        "message": "SWIFT Code Upload Service",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)