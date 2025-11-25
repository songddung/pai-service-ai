import httpx
from fastapi import HTTPException
from application.port.outbound.image_fetch_port import ImageFetchPort

class ImageFetchAdapter(ImageFetchPort):

    async def fetch_image_from_url(self, url: str) -> bytes:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"이미지 다운로드 실패: {e}")
