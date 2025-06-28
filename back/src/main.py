import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Import routes
from src.api.routes.chat_routes import router as chat_router
from src.api.routes.lesion_routes import router as lesion_router
from src.api.routes.cough_routes import router as cough_router

app = FastAPI(
    title="Convolucionados API",
    description="API for AI services with Gemini and image classification",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(chat_router)
app.include_router(lesion_router)
app.include_router(cough_router)

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Welcome to Convolucionados API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat/generate",
            "lesion_evaluation": "/lesion/evaluate",
            "upload_image": "/upload-image"
        }
    }

@app.post("/upload-image")
async def upload_image(
    image: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """Endpoint for uploading images (maintained for compatibility)"""
    return {
        "filename": image.filename,
        "content_type": image.content_type,
        "description": description
    }

