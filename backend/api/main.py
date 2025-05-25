"""
Main application module for the SWIFT Code API.

This module sets up the FastAPI application and includes the SWIFT code router.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.swiftCodeRouter import router as swift_code_router

app = FastAPI(
    title="SWIFT Code API",
    description="API for managing bank SWIFT/BIC codes",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(swift_code_router)

@app.get("/", tags=["root"])
async def root():
    """Root endpoint that returns API information."""
    return {
        "message": "Welcome to the SWIFT Code API",
        "docs": "/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)