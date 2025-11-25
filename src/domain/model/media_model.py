from pydantic import BaseModel

class MediaInfo(BaseModel):
    mediaId: str
    cdnUrl: str
    fileName: str
    mimeType: str
    s3Key: str
    createdAt: str
