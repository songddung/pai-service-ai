import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# This will be adjusted to the new structure
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from fastapi import FastAPI

# Import routers from the new structure
from adapter.inbound.web.tts_controller import tts_router
from adapter.inbound.web.vqa_controller import vqa_router
from adapter.inbound.web.recommend_controller import recommend_router
from adapter.inbound.web.dependencies import get_yolo_service, get_vilt_service, get_tts_adapter


app = FastAPI(
    title="PAI-service-AI",
    version="1.0",
    description="An integrated server providing both Text-to-Speech (TTS) and Visual Question Answering (VQA) functionalities."
)

@app.on_event("startup")
def on_startup():
    """Load all AI models on server startup."""
    print("--- Server startup sequence initiated ---")
    # Initialize models eagerly for better performance
    print("--- TTS Module Loading ---")
    try:
        get_tts_adapter()
        print("--- TTS Module Loaded ---")
    except Exception as e:
        print(f"Warning: TTS adapter initialization failed: {e}")

    print("--- VQA Module Loading ---")
    get_yolo_service()
    get_vilt_service()
    print("--- VQA Module Loaded ---")
    print("--- All models loaded. Server startup complete. ---")


@app.get("/")
def read_root():
    return {"message": "Welcome to the PAI AI Server. Visit /docs for API details."}

# Include routers from each module with their own prefixes and tags
app.include_router(tts_router, prefix="/api/ai/tts", tags=["TTS - Voice Cloning"])
app.include_router(vqa_router, prefix="/api/ai/vqa", tags=["VQA - Visual Question Answering"])
app.include_router(recommend_router, prefix="/api/ai/recommend", tags=["Recommend - "])
