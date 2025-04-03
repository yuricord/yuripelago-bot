from enum import IntEnum, IntFlag, StrEnum
from typing import Literal, NamedTuple


class MessageCommand(StrEnum):
    ROOM_INFO = "RoomInfo"
    CONNECTION_REFUSED = "ConnectionRefused"
    CONNECTED = "Connected"
    RECEIVED_ITEMS = "ReceivedItems"
    LOCATION_INFO = "LocationInfo"
    ROOM_UPDATE = "RoomUpdate"
    PRINT_JSON = "PrintJSON"
    DATA_PACKAGE = "DataPackage"
    BOUNCED = "Bounced"
    INVALID_PACKET = "InvalidPacket"
    RETRIEVED = "Retrieved"
    SET_REPLY = "SetReply"


class ConnectionRefusedError(StrEnum):
    INVALID_SLOT = "InvalidSlot"
    INVALID_GAME = "InvalidGame"
    INCOMPATIBLE_VERSION = "IncompatibleVersion"
    INVALID_PASSWORD = "InvalidPassword"
    INVALID_ITEMS_HANDLING = "InvalidItemsHandling"


class HintStatus(IntEnum):
    UNSPECIFIED = 0
    NO_PRIORITY = 10
    AVOID = 20
    PRIORITY = 30
    FOUND = 40


class Permission(IntEnum):
    disabled = 0b000
    enabled = 0b001
    goal = 0b010
    auto = 0b110
    auto_enabled = 0b111


class SlotType(IntFlag):
    spectator = 0b00
    player = 0b01
    group = 0b10


class ItemFlags(IntFlag):
    NONE = 0
    ADVANCEMENT = 0b001
    USEFUL = 0b010
    TRAP = 0b100


class ArchiVersion(NamedTuple):
    major: int
    minor: int
    build: int
    type_class: Literal["Version"]


class PrintJsonType(StrEnum):
    ITEM_SEND = "ItemSend"
    ITEM_CHEAT = "ItemCheat"
    HINT = "Hint"
    JOIN = "Join"
    PART = "Part"
    CHAT = "Chat"
    SERVER_CHAT = "ServerChat"
    TUTORIAL = "Tutorial"
    TAGS_CHANGED = "TagsChanged"
    COMMAND_RESULT = "CommandResult"
    ADMIN_COMMAND_RESULT = "AdminCommandResult"
    GOAL = "Goal"
    RELEASE = "Release"
    COLLECT = "Collect"
    COUNTDOWN = "Countdown"
