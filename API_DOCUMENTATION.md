# PAI VQA Service API Documentation

## 📋 Overview
PAI VQA (Visual Question Answering) 서비스는 이미지와 질문을 받아 AI 기반 답변을 제공하는 FastAPI 기반 서비스입니다.

## 🌐 Base URL
```
http://localhost:8000
```

---

## 🔍 VQA API

### Endpoint
```
POST /api/ai/vqa/
```

### Description
이미지와 질문을 받아 AI 기반 답변을 생성합니다.
- **이미지가 있는 경우**: YOLO 객체 감지 → ViLT VQA → GPT-4o 설명 생성
- **이미지가 없는 경우**: LLM을 통한 일반 질의응답

### Request

**Content-Type:** `multipart/form-data`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `media_id` | string | No | 미디어/이미지 ID |
| `question` | string | Yes | 사용자의 질문 (한국어/영어) |
| `child_name` | string | No | 아이 이름 (답변 개인화) |

### Response

#### 이미지가 있는 경우
```json
{
  "answer": "지민아, 이 그림에는 귀여운 강아지가 있어! 강아지는 네 발로 걸어다니고 꼬리를 흔드는 동물이야.",
  "vqa_direct_answer": "dog",
  "question": "이 그림에 무엇이 있어?",
  "detected_object": "dog"
}
```

**Fields:**
- `answer` (string): LLM이 생성한 아이 친화적인 설명
- `vqa_direct_answer` (string): ViLT 모델의 직접 답변
- `question` (string): 원본 질문
- `detected_object` (string): YOLO가 감지한 객체

#### 이미지가 없는 경우
```json
{
  "answer": "안녕! 하늘이 파란 이유는 태양 빛이 대기를 통과할 때 파란색 빛이 더 많이 퍼지기 때문이야.",
  "keywords": ["하늘", "파란색", "이유"],
  "question": "하늘은 왜 파란색이야?",
  "detected_object": "No image provided"
}
```

**Fields:**
- `answer` (string): LLM이 생성한 답변
- `keywords` (array): 질문에서 추출한 주요 키워드
- `question` (string): 원본 질문
- `detected_object` (string): "No image provided"

### Error Response

**500 Internal Server Error**
```json
{
  "detail": "VQA 처리 중 오류: {error_message}"
}
```

---

## 📝 Request Examples

### cURL
```bash
# 이미지가 있는 경우
curl -X POST "http://localhost:8000/api/ai/vqa/" \
  -H "Content-Type: multipart/form-data" \
  -F "media_id=image_123" \
  -F "question=이 그림에 무엇이 있어?" \
  -F "child_name=지민"

# 이미지가 없는 경우
curl -X POST "http://localhost:8000/api/ai/vqa/" \
  -H "Content-Type: multipart/form-data" \
  -F "question=하늘은 왜 파란색이야?" \
  -F "child_name=지민"
```

### Python
```python
import requests

url = "http://localhost:8000/api/ai/vqa/"

# 이미지가 있는 경우
data = {
    "media_id": "image_123",
    "question": "이 그림에 무엇이 있어?",
    "child_name": "지민"
}
response = requests.post(url, data=data)
print(response.json())

# 이미지가 없는 경우
data = {
    "question": "하늘은 왜 파란색이야?",
    "child_name": "지민"
}
response = requests.post(url, data=data)
print(response.json())
```

### JavaScript
```javascript
// 이미지가 있는 경우
const formData = new FormData();
formData.append('media_id', 'image_123');
formData.append('question', '이 그림에 무엇이 있어?');
formData.append('child_name', '지민');

fetch('http://localhost:8000/api/ai/vqa/', {
  method: 'POST',
  body: formData
})
  .then(res => res.json())
  .then(data => console.log(data));

// 이미지가 없는 경우
const formData2 = new FormData();
formData2.append('question', '하늘은 왜 파란색이야?');
formData2.append('child_name', '지민');

fetch('http://localhost:8000/api/ai/vqa/', {
  method: 'POST',
  body: formData2
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 🧩 Data Models

### VQARequest
```python
from pydantic import BaseModel
from typing import Optional

class VQARequest(BaseModel):
    image_url: str
    question: str
    child_name: Optional[str]
```

### VQAResponse
```python
from pydantic import BaseModel

class VQAResponse(BaseModel):
    answer: str
    vqa_direct_answer: str
    question: str
    detected_object: str
```

---

## ⚙️ Processing Pipeline

### 이미지가 있는 경우

```
1. 키워드 추출
   ↓
2. 언어 감지 (한국어/영어)
   ↓
3. 질문 번역 (한국어 → 영어)
   ↓
4. YOLO 객체 감지
   ↓
5. ViLT VQA 수행
   ↓
6. GPT-4o로 아이 친화적 설명 생성
   ↓
7. 답변 번역 (영어 → 한국어)
   ↓
8. 최종 응답 반환
```

### 이미지가 없는 경우

```
1. 키워드 추출
   ↓
2. 언어 감지 (한국어/영어)
   ↓
3. GPT-4o로 직접 답변 생성
   ↓
4. 최종 응답 반환
```

---

## 🤖 AI Models

| Model | Purpose | Details |
|-------|---------|---------|
| **YOLO** | 객체 감지 | Custom model: `src/models/best.pt` |
| **ViLT** | Visual QA | `dandelin/vilt-b32-finetuned-vqa` |
| **GPT-4o** | 설명 생성 | OpenRouter API |
| **LangDetect** | 언어 감지 | Python library |
| **Deep Translator** | 번역 | Google Translate backend |

---

## 🔧 Environment Variables

`.env` 파일을 생성하고 다음 변수를 설정하세요:

```bash
OPENROUTER_API_KEY=your_openrouter_api_key
```

---

## 🚀 Server Setup

### 1. Installation
```bash
cd pai-service-ai
pip install -r requirements.txt
```

### 2. Run Server
```bash
cd src
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📦 Dependencies

```
# Web Framework
fastapi==0.116.1
uvicorn==0.35.0
python-multipart
requests
python-dotenv

# AI/ML Libraries
torch==2.6.0
torchaudio==2.6.0
torchvision==0.21.0
transformers==4.49.0

# VQA Libraries
Pillow==10.2.0
opencv-python
ultralytics
deep-translator
langdetect

# Supporting
anyio==4.8.0
httpx==0.28.1
huggingface-hub==0.28.1
numpy==2.2.6
safetensors==0.5.3
```

---

## 📂 Project Structure

```
pai-service-ai/
├── src/
│   ├── adapter/
│   │   ├── inbound/
│   │   │   └── web/
│   │   │       └── vqa_controller.py       # VQA API 엔드포인트
│   │   └── outbound/
│   │       └── llm_adapter.py              # LLM 통신
│   ├── application/
│   │   ├── port/
│   │   │   ├── inbound/
│   │   │   │   └── vqa_use_case.py         # VQA 유스케이스 인터페이스
│   │   │   └── outbound/
│   │   │       └── llm_port.py             # LLM 포트 인터페이스
│   │   └── service/
│   │       └── vqa_service.py              # VQA 비즈니스 로직
│   ├── domain/
│   │   ├── model/
│   │   │   └── vqa_model.py                # VQA 데이터 모델
│   │   └── service/
│   │       ├── yolo_service.py             # YOLO 객체 감지
│   │       └── vilt_service.py             # ViLT VQA
│   ├── models/
│   │   └── best.pt                         # YOLO 커스텀 모델
│   └── main.py                             # FastAPI 애플리케이션
├── requirements.txt
├── API_DOCUMENTATION.md
└── README.md
```

---

## 💡 Usage Tips

### 1. 언어 지원
- 질문은 **한국어** 또는 **영어**로 입력 가능
- 한국어 질문은 자동으로 영어로 번역되어 처리
- 답변은 다시 한국어로 번역되어 반환

### 2. 개인화
- `child_name` 파라미터를 제공하면 더 개인화된 답변 생성
- 예: "지민아, 이 그림에는..." 형식으로 답변

### 3. 이미지 없는 질문
- `media_id` 없이 `question`만 제공 가능
- LLM이 직접 일반 지식 기반 답변 제공

### 4. 키워드 추출
- 모든 질문에서 자동으로 키워드 추출
- 불용어(stopwords) 제거 후 주요 키워드 5개 반환

---

## 🔍 API Testing

### Swagger UI에서 테스트
1. http://localhost:8000/docs 접속
2. `POST /api/ai/vqa/` 엔드포인트 클릭
3. "Try it out" 버튼 클릭
4. 파라미터 입력 후 "Execute" 클릭

### Example Test Cases

**테스트 케이스 1: 이미지 + 질문**
```
media_id: "dog_image_123"
question: "이 그림에 무엇이 있어?"
child_name: "지민"
```

**테스트 케이스 2: 질문만**
```
question: "공룡은 언제 살았어?"
child_name: "지민"
```

**테스트 케이스 3: 영어 질문**
```
media_id: "cat_image_456"
question: "What is in this picture?"
child_name: "John"
```

---

## 🐛 Troubleshooting

### 1. 모델 로딩 실패
```
Error: YOLO model not found
Solution: src/models/best.pt 파일이 존재하는지 확인
```

### 2. OpenRouter API 에러
```
Error: OpenRouter API key not found
Solution: .env 파일에 OPENROUTER_API_KEY 설정
```

### 3. 번역 실패
```
Error: Translation failed
Solution: 인터넷 연결 확인 (Google Translate API 사용)
```

---

## 📊 Performance

- **첫 요청**: 5-10초 (모델 로딩 포함)
- **이후 요청**: 2-5초
- **이미지 없는 요청**: 1-3초

---

## 🔒 Security Notes

- API 키는 `.env` 파일에 저장하고 `.gitignore`에 추가
- 프로덕션 환경에서는 HTTPS 사용 권장
- Rate limiting 구현 권장

---

## 📞 Support

- **API 문서**: http://localhost:8000/docs
- **프로젝트**: PAI Service AI
- **Version**: 1.0