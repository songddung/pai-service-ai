import os
import httpx

from application.port.outbound.llm_port import LLMPort

from dotenv import load_dotenv
load_dotenv()  # .env 파일 자동 로드

# 환경변수는 모듈 최상단에서 only once 로딩
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMAdapter(LLMPort):

    async def call_llm(self,prompt: str, lang: str) -> str:
        if not OPENROUTER_API_KEY:
            return "LLM API key is not configured."
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        }
        json_data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "developer", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 150,
            "temperature": 0.7,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.post(OPENROUTER_API_URL, headers=headers, json=json_data)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                return "간단 답변 생성에 실패했습니다. 서버 관리자에게 문의해 주세요."

    async def ask_simple(self, question: str, child_name:str,lang: str = "ko", max_tokens: int = 80) -> str:
        if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "":
            return "현재 AI 답변 기능이 비활성화되어 답변을 드릴 수 없습니다."
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "PAI-service-AI",
        }
        if lang == "ko":
            prompt = (
                f"{child_name}가 사진을 보면서 이렇게 물었어:\n"
                f'"{question}"\n\n'
                f"이제 부모님인 내가 {child_name}에게 짧고 쉽게, 따뜻하게 설명해줄게.\n"
                f"{child_name} 눈높이에 맞게 2~3문장 이내로 말해줘."
            )
        else:
            prompt = (
                f"{child_name} asked this question while looking at the picture:\n"
                f'"{question}"\n\n'
                f"Now, as a parent, explain it to {child_name} in a kind, simple way, within 2–3 sentences, easy for a child to understand."
            )
        json_data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "developer", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.post(OPENROUTER_API_URL, headers=headers, json=json_data)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                return "간단 답변 생성에 실패했습니다. 서버 관리자에게 문의해 주세요."
