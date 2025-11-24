import httpx
from typing import Optional
from fastapi import HTTPException
from application.port.outbound.media_port import MediaPort
from domain.model.media_model import MediaInfo

class MediaAdapter(MediaPort):

    def __init__(self, base_url: str = "http://darami.life:3002"):
        self.base_url = base_url

    async def get_media_info(self, media_id: str, token: Optional[str] = None) -> MediaInfo:
        """Get media information from media API"""
        url = f"{self.base_url}/api/media"
        headers = {}

        # Add authorization header with JWT token from request
        if token:
            headers["Authorization"] = f"Bearer {token}"
            print(f"DEBUG: Sending request to {url}")
            print(f"DEBUG: Looking for mediaId={media_id}")
            print(f"DEBUG: Using token from request header (length: {len(token)})")
        else:
            print("WARNING: No token provided for media API request")

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                response_data = response.json()

                # LOG: Print full response
                print("="*50)
                print("DEBUG: Full API Response:")
                print(response_data)
                print("="*50)

                # Parse response: data is wrapped in a "data" array
                if "data" in response_data and isinstance(response_data["data"], list):
                    media_list = response_data["data"]

                    if len(media_list) == 0:
                        raise HTTPException(status_code=404, detail=f"미디어 ID {media_id}를 찾을 수 없습니다.")

                    # Find the media with matching mediaId
                    media_data = None
                    for item in media_list:
                        if str(item.get("mediaId")) == str(media_id):
                            media_data = item
                            break

                    if media_data is None:
                        raise HTTPException(status_code=404, detail=f"미디어 ID {media_id}를 찾을 수 없습니다.")
                else:
                    # Fallback: if response is not wrapped in "data" array
                    media_data = response_data

                # LOG: Print parsed media data
                print("DEBUG: Parsed Media Data:")
                print(media_data)
                print("="*50)

                # LOG: Print CDN URL
                cdn_url = media_data.get("cdnUrl")
                print(f"DEBUG: Extracted CDN URL: {cdn_url}")
                print("="*50)

                return MediaInfo(**media_data)
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"미디어 정보 조회 실패: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"미디어 API 호출 오류: {str(e)}")
