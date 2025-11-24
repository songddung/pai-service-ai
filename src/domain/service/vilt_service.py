import torch
import io
from PIL import Image
from transformers import ViltProcessor, ViltForQuestionAnswering

processor: ViltProcessor = None
model: ViltForQuestionAnswering = None
device: torch.device = None

def load_vilt_model(model_name: str):
    global processor, model, device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    processor = ViltProcessor.from_pretrained(model_name)
    model = ViltForQuestionAnswering.from_pretrained(model_name)
    model.eval()
    model.to(device)

def answer_question_bytes(image_bytes: bytes, question: str) -> str:
    if not processor or not model:
        return "VQA model is not available."
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = processor(image, question, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits
        idx = logits.argmax(-1).item()
        return model.config.id2label[idx]
    except Exception as e:
        return f"Error during VQA inference: {e}"
