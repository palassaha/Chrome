from fastapi import APIRouter, File, UploadFile

from services.intent_service import IntentService
from services.transcription_service import TranscriptionService
from utils.file_validator import validate_audio_blob
from utils.url_builder import build_platform_url

router = APIRouter()

transcription_service = TranscriptionService()
intent_service = IntentService()


@router.post("/process-voice")
async def process_voice(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    validate_audio_blob(file, audio_bytes)
    print(f"Validated audio type: {file.content_type}")

    user_text = transcription_service.transcribe(audio_bytes)
    print(f"Raw user input: {user_text}")

    try:
        intent = intent_service.classify(user_text)
    except Exception:
        return {
            "text": user_text,
            "platform": "unknown",
            "url": None,
        }
    print(f"Parsed intent -> platform: {intent.platform}, query: {intent.query}")

    url = build_platform_url(intent)
    print(f" Generated URL: {url}")

    response = {
        "text": user_text,
        "platform": intent.platform,
        "url": url,
        "extracted_query": intent.query,
    }
    print(f"Response payload: {response}")

    return response
