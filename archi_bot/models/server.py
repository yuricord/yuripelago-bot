from typing import Literal

from pydantic import BaseModel, Field

from archi_bot.types import HintStatus, ItemFlags, SlotType


class ArchiNetworkPlayer(BaseModel):
    team: int
    slot: int
    alias: str
    name: str
    type_class: Literal["NetworkPlayer"] = Field(alias="class", default="NetworkPlayer")


class ArchiNetworkSlot(BaseModel):
    name: str
    game: str
    type: SlotType
    group_members: list[int]
    type_class: Literal["NetworkSlot"] = Field(alias="class", default="NetworkSlot")


class ArchiNetworkItem(BaseModel):
    item: int
    location: int
    player: int
    flags: ItemFlags


class ArchiJSONMessagePart(BaseModel):
    type: str | None = None
    text: str | None = None
    color: str | None = None
    flags: int | None = None
    player: int | None = None
    hint_status: HintStatus | None = None


class ArchiGameData(BaseModel):
    item_name_to_id: dict[str, int]
    location_name_to_id: dict[str, int]
    checksum: str
