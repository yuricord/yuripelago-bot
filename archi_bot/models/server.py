from typing import Literal, Optional

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
    type: Optional[str] = None
    text: Optional[str] = None
    color: Optional[str] = None
    flags: Optional[int] = None
    player: Optional[int] = None
    hint_status: Optional[HintStatus] = None


class ArchiGameData(BaseModel):
    item_name_to_id: dict[str, int]
    location_name_to_id: dict[str, int]
    checksum: str
