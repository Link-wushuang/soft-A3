import base64
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.models.user import User
from app.services.tts_service import is_tts_available, synthesize

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tts", tags=["tts"])


class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "xiaoyan"


@router.get("/available")
def tts_available(user: User = Depends(get_current_user)):
    """前端探测 TTS 是否可用，决定是否降级到浏览器 speechSynthesis。"""
    return {"available": is_tts_available()}


@router.post("/synthesize")
def synthesize_audio(req: SynthesizeRequest, user: User = Depends(get_current_user)):
    """把文本合成为 mp3 音频，返回 base64 编码。

    前端拿到后用 `data:audio/mp3;base64,...` 作为 <audio> src 播放。
    若 TTS 不可用返回 available=false，前端应降级到浏览器 Web Speech API。
    """
    if not is_tts_available():
        return {"available": False, "reason": "tts_credentials_missing"}

    audio = synthesize(req.text, req.voice)
    if not audio:
        return {"available": False, "reason": "tts_synthesis_failed"}

    return {
        "available": True,
        "format": "mp3",
        "audio_base64": base64.b64encode(audio).decode(),
    }
