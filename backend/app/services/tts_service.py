"""讯飞在线语音合成（TTS）服务封装。

通过讯飞 TTS WebSocket v2 接口把文本转成 mp3 音频，用于视频分镜旁白，
配合前端 SVG 分镜动画实现"图文+语音"伪视频，补齐赛题多模态视频要求。

鉴权复用讯飞开放平台账号（与 Spark LLM 共用 APP_ID/API_KEY/API_SECRET），
需在开放平台控制台额外开通"在线语音合成"服务。

参考文档：https://www.xfyun.cn/doc/tts/online_tts/API.html
"""

import base64
import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

from app.core.config import settings

logger = logging.getLogger(__name__)

TTS_HOST = "tts-api.xfyun.cn"
TTS_PATH = "/v2/tts"

# 缓存：相同文本+发音人直接复用，避免重复调用 TTS
_audio_cache: dict[str, bytes] = {}
_CACHE_MAX = 50


def _build_auth_url(api_key: str, api_secret: str) -> str:
    """生成讯飞 TTS WebSocket 鉴权 URL（HMAC-SHA256 签名）。

    参考：https://www.xfyun.cn/doc/tts/online_tts/API.html
    """
    from urllib.parse import quote

    now = datetime.now(timezone.utc)
    date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
    # 签名原始串格式严格按文档：host: xxx\ndate: xxx\nGET /v2/tts HTTP/1.1
    signature_origin = f"host: {TTS_HOST}\ndate: {date}\nGET {TTS_PATH} HTTP/1.1"
    signature_sha = hmac.new(
        api_secret.encode("utf-8"),
        signature_origin.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature = base64.b64encode(signature_sha).decode()
    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode()
    # URL 参数需 encode
    return (
        f"wss://{TTS_HOST}{TTS_PATH}"
        f"?authorization={quote(authorization)}&date={quote(date)}&host={quote(TTS_HOST)}"
    )


def is_tts_available() -> bool:
    """TTS 服务是否可用（凭证齐全）。"""
    return bool(settings.spark_app_id and settings.spark_api_key and settings.spark_api_secret)


def synthesize(text: str, voice: str = "xiaoyan") -> bytes | None:
    """把文本合成为 mp3 音频字节。

    Args:
        text: 待合成文本（单次上限 8000 字符，超出会被截断）。
        voice: 发音人 vcn，常用值：xiaoyan(小燕/女)、aisjiuxu(男士)、aisxping(小萍/女)。

    Returns:
        mp3 音频字节；失败返回 None。
    """
    if not is_tts_available():
        logger.warning("TTS credentials missing, skip synthesis")
        return None

    text = (text or "").strip()
    if not text:
        return None
    # 讯飞 TTS 单次上限 8000 字符
    if len(text) > 8000:
        text = text[:8000]

    cache_key = f"{voice}:{text}"
    if cache_key in _audio_cache:
        return _audio_cache[cache_key]

    try:
        import websocket  # websocket-client 同步库
    except ImportError:
        logger.error("websocket-client not installed, TTS unavailable")
        return None

    auth_url = _build_auth_url(settings.spark_api_key, settings.spark_api_secret)
    audio_chunks: list[bytes] = []

    def _on_message(ws, message):  # type: ignore[no-untyped-def]
        try:
            data = json.loads(message)
            code = data.get("code", 0)
            if code != 0:
                logger.error("TTS error code=%s msg=%s", code, data.get("message"))
                ws.close()
                return
            audio_b64 = data.get("data", {}).get("audio")
            if audio_b64:
                audio_chunks.append(base64.b64decode(audio_b64))
            # status=2 表示合成结束
            if data.get("data", {}).get("status") == 2:
                ws.close()
        except Exception as exc:
            logger.error("TTS message parse failed: %s", exc)
            ws.close()

    def _on_error(ws, error):  # type: ignore[no-untyped-def]
        logger.error("TTS websocket error: %s", error)

    def _on_open(ws):  # type: ignore[no-untyped-def]
        frame = {
            "common": {"app_id": settings.spark_app_id},
            "business": {
                "aue": "lame",          # mp3 格式
                "sfl": 1,               # aue=lame 时必须传 sfl=1
                "auf": "audio/L16;rate=16000",
                "vcn": voice,           # 发音人参数名是 vcn（非 voice）
                "speed": 50,
                "volume": 50,
                "pitch": 50,
                "tte": "UTF8",          # 文本编码
            },
            "data": {
                "status": 2,            # 一次发送全部文本
                "text": base64.b64encode(text.encode("utf-8")).decode(),
            },
        }
        ws.send(json.dumps(frame))

    ws = websocket.WebSocketApp(
        auth_url,
        on_message=_on_message,
        on_error=_on_error,
        on_open=_on_open,
    )
    # 同步阻塞运行，用 ping_timeout 作为超时保护
    import threading
    ws_run_thread = threading.Thread(target=ws.run_forever, kwargs={"ping_timeout": 30})
    ws_run_thread.daemon = True
    ws_run_thread.start()
    ws_run_thread.join(timeout=45)  # 最多等 45 秒
    if ws_run_thread.is_alive():
        logger.error("TTS websocket timeout after 45s")
        try:
            ws.close()
        except Exception:
            pass

    if not audio_chunks:
        return None

    audio = b"".join(audio_chunks)

    # 写入缓存（FIFO 淘汰）
    if len(_audio_cache) >= _CACHE_MAX:
        _audio_cache.pop(next(iter(_audio_cache)))
    _audio_cache[cache_key] = audio
    return audio
