from typing import Annotated, Any, Literal, Optional, Union

from pydantic import BaseModel, Field

from archi_bot.models.misc import ArchiVersion
from archi_bot.models.server import (
    ArchiGameData,
    ArchiJSONMessagePart,
    ArchiNetworkItem,
    ArchiNetworkPlayer,
    ArchiNetworkSlot,
)
from archi_bot.types import (
    ConnectionRefusedError,
    MessageCommand,
    Permission,
    PrintJsonType,
)


class RoomInfoPacket(BaseModel):
    cmd: Literal[MessageCommand.ROOM_INFO]
    version: ArchiVersion
    generator_version: ArchiVersion
    tags: list[str]
    password: bool
    permissions: dict[str, Permission]
    hint_cost: int
    location_check_points: int
    games: list[str]
    datapackage_checksums: dict[str, str]
    seed_name: str
    time: float


class ConnectionRefusedPacket(BaseModel):
    cmd: Literal[MessageCommand.CONNECTION_REFUSED]
    errors: Optional[list[ConnectionRefusedError]]


class ConnectedPacket(BaseModel):
    cmd: Literal[MessageCommand.CONNECTED]
    team: int
    slot: int
    players: list[ArchiNetworkPlayer]
    missing_locations: list[int]
    checked_locations: list[int]
    slot_data: Optional[dict[str, Any]]
    slot_info: dict[str, ArchiNetworkSlot]
    hint_points: int


class ReceivedItemsPacket(BaseModel):
    cmd: Literal[MessageCommand.RECEIVED_ITEMS]
    index: int
    items: list[ArchiNetworkItem]


class LocationInfoPacket(BaseModel):
    cmd: Literal[MessageCommand.LOCATION_INFO]
    locations: list[ArchiNetworkItem]


class RoomUpdatePacket(BaseModel):
    cmd: Literal[MessageCommand.ROOM_UPDATE]
    players: Optional[list[ArchiNetworkPlayer]]
    checked_locations: Optional[list[int]]


class DataPackagePacket(BaseModel):
    cmd: Literal[MessageCommand.DATA_PACKAGE]
    data: dict[Literal["games"], dict[str, ArchiGameData]]


class BouncedPacket(BaseModel):
    cmd: Literal[MessageCommand.BOUNCED]
    games: Optional[list[str]] = None
    slots: Optional[list[int]] = None
    tags: Optional[list[str]] = None
    data: dict


class InvalidPacketPacket(BaseModel):
    cmd: Literal[MessageCommand.INVALID_PACKET]
    type: str
    original_cmd: Optional[str]
    text: str


class RetrievedPacket(BaseModel):
    cmd: Literal[MessageCommand.RETRIEVED]
    keys: dict[str, Any]


class SetReplyPacket(BaseModel):
    cmd: Literal[MessageCommand.SET_REPLY]
    key: str
    value: Any
    original_value: Any
    slot: int


# PrintJSONPacket and Sub-types


class PrintJSONPacketBase(BaseModel):
    cmd: Literal[MessageCommand.PRINT_JSON]
    data: list[ArchiJSONMessagePart]


class PJItemSendPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.ITEM_SEND]
    receiving: int
    item: ArchiNetworkItem


class PJItemCheatPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.ITEM_CHEAT]
    receiving: int
    item: ArchiNetworkItem
    team: int


class PJHintPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.HINT]
    receiving: int
    item: ArchiNetworkItem
    found: bool


class PJJoinPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.JOIN]
    team: int
    slot: int
    tags: list[str]


class PJPartPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.PART]
    team: int
    slot: int


class PJChatPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.CHAT]
    team: int
    slot: int
    message: str


class PJServerChatPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.SERVER_CHAT]
    message: str


class PJTutorialPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.TUTORIAL]


class PJTagsChangedPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.TAGS_CHANGED]
    team: int
    slot: int
    tags: list[str]


class PJCommandResultPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.COMMAND_RESULT]


class PJAdminCommandResultPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.ADMIN_COMMAND_RESULT]


class PJGoalPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.GOAL]
    team: int
    slot: int


class PJReleasePacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.RELEASE]
    team: int
    slot: int


class PJCollectPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.COLLECT]
    team: int
    slot: int


class PJCountdownPacket(PrintJSONPacketBase):
    type: Literal[PrintJsonType.COUNTDOWN]
    countdown: int


PrintJSONPacket = Annotated[
    Union[
        PJItemSendPacket,
        PJItemCheatPacket,
        PJHintPacket,
        PJJoinPacket,
        PJPartPacket,
        PJChatPacket,
        PJServerChatPacket,
        PJTutorialPacket,
        PJTagsChangedPacket,
        PJCommandResultPacket,
        PJAdminCommandResultPacket,
        PJGoalPacket,
        PJReleasePacket,
        PJCollectPacket,
        PJCountdownPacket,
    ],
    Field(discriminator="type"),
]

ArchiPacket = Annotated[
    Union[
        RoomInfoPacket,
        ConnectionRefusedPacket,
        ConnectedPacket,
        ReceivedItemsPacket,
        LocationInfoPacket,
        RoomUpdatePacket,
        PrintJSONPacket,
        DataPackagePacket,
        BouncedPacket,
        InvalidPacketPacket,
        RetrievedPacket,
        SetReplyPacket,
    ],
    Field(discriminator="cmd"),
]
