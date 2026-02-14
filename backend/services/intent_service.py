from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from models.intent import PlayIntent


class IntentService:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=PlayIntent)

        self.prompt = PromptTemplate(
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
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )

        self.llm = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0.6,
        )

        self.chain = self.prompt | self.llm | self.parser

    def classify(self, text: str) -> PlayIntent:
        return self.chain.invoke({"input": text})
