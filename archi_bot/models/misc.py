from typing import Literal

from pydantic import BaseModel, Field


class ArchiVersion(BaseModel):
    major: int
    minor: int
    build: int
    type_class: Literal["Version"] = Field(alias="class", default="Version")
