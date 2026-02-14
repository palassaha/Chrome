import io

from groq import Groq

from core.config import settings


class TranscriptionService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def transcribe(self, audio_bytes: bytes) -> str:
        buffer = io.BytesIO(audio_bytes)
        buffer.name = "input.wav"

        transcription = self.client.audio.transcriptions.create(
            file=buffer,
            model="whisper-large-v3",
        )

        return transcription.text
