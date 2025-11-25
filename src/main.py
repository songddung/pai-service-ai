import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from fastapi import FastAPI

# Import VQA router and model loader
from adapter.inbound.web.vqa_controller import vqa_router
from application.service.vqa_service import load_vqa_models


app = FastAPI(
    title="PAI-service-AI",
    version="1.0",
    description="PAI AI Server - Visual Question Answering (VQA) Service"
)

@app.on_event("startup")
def on_startup():
    """Load VQA models on server startup."""
    print("--- Server startup sequence initiated ---")
    load_vqa_models()
    print("--- VQA models loaded. Server startup complete. ---")


@app.get("/")
def read_root():
    return {"message": "Welcome to PAI AI VQA Server. Visit /docs for API details."}

# Include VQA router
app.include_router(vqa_router, prefix="/api/ai/vqa", tags=["VQA"])
