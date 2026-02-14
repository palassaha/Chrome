import io
import json
import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class PlayIntent(BaseModel):
    platform: Literal["youtube", "spotify", "unknown"] = Field(
        description="Platform choice"
    )
    query: str = Field(description="Media name")


parser = PydanticOutputParser(pydantic_object=PlayIntent)

prompt = PromptTemplate(
    template="""
You are an intent classification assistant.

Your task:
- Decide whether the user wants to play media on YouTube or Spotify.
- Extract the media query.
- If the platform is unclear, mark it as "unknown".

Rules:
- YouTube → videos, podcasts, talks, mixes
- Spotify → songs, albums, artists, music
- If platform is not mentioned or ambiguous → unknown

User input:
{input}

{format_instructions}
""",
    input_variables=["input"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

chain = prompt | llm | parser


@app.post("/process-voice")
async def process_voice(file: UploadFile = File(...)):
    print("\n--- New Request Received ---")
    audio_bytes = await file.read()

    print(f"DEBUG: Received {len(audio_bytes)} bytes")

    buffer = io.BytesIO(audio_bytes)
    buffer.name = "input.wav"

    transcription = client.audio.transcriptions.create(
        file=buffer,
        model="whisper-large-v3",
    )
    user_text = transcription.text
    print(f"🎤 Transcription: '{user_text}'")

    try:
        result = chain.invoke({"input": user_text})
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return {"text": user_text, "platform": "unknown", "url": None}

    url = None
    if result.platform == "youtube":
        url = f"https://www.youtube.com/results?search_query={result.query.replace(' ', '+')}"
    elif result.platform == "spotify":
        url = f"https://open.spotify.com/search/{result.query.replace(' ', '%20')}"

    response_body = {
        "text": user_text,
        "platform": result.platform,
        "url": url,
        "extracted_query": result.query,
    }

    print(f"📤 Sending to Frontend: {json.dumps(response_body, indent=2)}")

    return response_body


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
