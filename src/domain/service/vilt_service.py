import torch
import io
from PIL import Image
from transformers import ViltProcessor, ViltForQuestionAnswering
from application.port.outbound.vqa_model_port import VQAModelPort

class ViltService(VQAModelPort):

    def __init__(self, model_name: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = ViltProcessor.from_pretrained(model_name)
        self.model = ViltForQuestionAnswering.from_pretrained(model_name)
        self.model.eval()
        self.model.to(self.device)

    def answer_question(self, image_bytes: bytes, question: str) -> str:
        if not self.processor or not self.model:
            return "VQA model is not available."
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            inputs = self.processor(image, question, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)
            logits = outputs.logits
            idx = logits.argmax(-1).item()
            return self.model.config.id2label[idx]
        except Exception as e:
            return f"Error during VQA inference: {e}"
