import os
import webbrowser
from typing import Literal

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()


class PlayIntent(BaseModel):
    platform: Literal["youtube", "spotify", "unknown"] = Field(
        description="Where the user wants to play the media"
    )
    query: str = Field(description="Song name or video title")


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


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)


chain: RunnableSequence = prompt | llm | parser


def play_youtube(query: str):
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    print(f"▶️ Playing on YouTube: {query}")


def play_spotify(query: str):
    url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
    webbrowser.open(url)
    print(f"🎵 Playing on Spotify: {query}")


def main():
    user_input = input("> ").strip()
    result: PlayIntent = chain.invoke({"input": user_input})

    # print(result)

    if result.platform == "youtube":
        play_youtube(result.query)

    elif result.platform == "spotify":
        play_spotify(result.query)

    else:
        print("❓ I couldn't tell where to play this.")
        print("Try saying: 'play <song> on spotify' or 'play <video> on youtube'")


if __name__ == "__main__":
    main()
