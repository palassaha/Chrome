from typing import Literal

from pydantic import BaseModel, Field


class PlayIntent(BaseModel):
    platform: Literal["youtube", "spotify", "unknown"] = Field(
        description="Platform choice"
    )
    query: str = Field(description="Media name")
