import magic
from fastapi import HTTPException, UploadFile

ALLOWED_MIME_PREFIXES = {
    "audio/",
}

ALLOWED_MAGIC_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/webm",
    "audio/ogg",
}


def validate_audio_blob(file: UploadFile, file_bytes: bytes) -> None:
    if not any(
        file.content_type.startswith(prefix) for prefix in ALLOWED_MIME_PREFIXES
    ):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not audio.",
        )

    detected_type = magic.from_buffer(file_bytes, mime=True)

    if detected_type not in ALLOWED_MAGIC_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio format. Detected: {detected_type}",
        )
