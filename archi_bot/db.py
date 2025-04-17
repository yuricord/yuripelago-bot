import uuid
from typing import Any, Optional

from sqlalchemy import JSON, Engine
from sqlmodel import BLOB, Field, Relationship, SQLModel, create_engine

from archi_bot.types import SlotType

DB: Engine = create_engine("sqlite:///archi-bot.db")


class ArchiRoom(SQLModel, table=True):
    id: str = Field(primary_key=True)
    version: dict[str, str | int] = Field(
        sa_type=JSON,
    )  # The simplified form of archi_bot.types.ArchiVersion for SQLAlchemy Reasons(tm)
    password: bool
    hint_cost: int
    location_check_points: int
    rando_game: Optional["RandoGame"] = Relationship(
        back_populates="room", sa_relationship_kwargs={"lazy": "selectin"}
    )


class RandoGame(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    display_name: str | None = Field(default=None)
    room: ArchiRoom = Relationship(
        back_populates="rando_game", sa_relationship_kwargs={"lazy": "selectin"}
    )
    room_id: str = Field(default=None, foreign_key="archiroom.id")
    server_url: str = Field(default="archipelago.gg")
    port: int
    bot_slot: str = Field(default="ArchiBot")
    game_channel: int
    tracker_url: str
    room_url: str
    spoil_traps: bool
    active: bool = True


# Create our DB Entity Classes
class Hint(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    receiving_player: int
    finding_player: int
    location: int
    item: int
    found: bool
    entrance: str = ""
    item_flags: int = 0
    room_id: str = Field(foreign_key="archiroom.id")


class GameDataPackage(SQLModel, table=True):
    name: str = Field(primary_key=True)
    package_checksum: str


class ItemGroup(SQLModel, table=True):
    # Custom Table Name for safety
    name: str = Field(primary_key=True)
    game: str = Field(foreign_key="gamedatapackage.name", primary_key=True)


class Item(SQLModel, table=True):
    item_id: int = Field(primary_key=True)
    game: str = Field(foreign_key="gamedatapackage.name", primary_key=True)
    name: str
    group: str | None = Field(default=None, foreign_key="itemgroup.name")


class LocationGroup(SQLModel, table=True):
    name: str = Field(primary_key=True)
    game: str = Field(foreign_key="gamedatapackage.name", primary_key=True)


class Location(SQLModel, table=True):
    location_id: int = Field(primary_key=True)
    game: str = Field(foreign_key="gamedatapackage.name", primary_key=True)
    name: str
    group: str | None = Field(default=None, foreign_key="locationgroup.name")


class DiscordSlotLink(SQLModel, table=True):
    slot_id: int | None = Field(
        default=None, foreign_key="archislot.global_id", primary_key=True
    )
    discord_id: int | None = Field(
        default=None, foreign_key="discorduser.id", primary_key=True
    )


class ArchiSlot(SQLModel, table=True):
    global_id: int | None = Field(default=None, primary_key=True)
    id: int
    name: str
    game: str = Field(foreign_key="gamedatapackage.name")
    type: SlotType
    group_members: list[int] = Field(
        default=[],
        sa_type=JSON,
    )  # Only populated if `self.type == SlotType.group`
    room_id: str = Field(foreign_key="archiroom.id")
    discord_users: list["DiscordUser"] = Relationship(
        back_populates="slots", link_model=DiscordSlotLink
    )
    deaths: int | None = Field(default=0)


class ArchiPlayer(SQLModel, table=True):
    team: int = Field(primary_key=True)
    slot: int = Field(primary_key=True)
    name: str
    room_id: str = Field(foreign_key="archiroom.id", primary_key=True)


class DiscordUser(SQLModel, table=True):
    id: int = Field(primary_key=True)
    slots: list[ArchiSlot] = Relationship(
        back_populates="discord_users", link_model=DiscordSlotLink
    )


class RetrievedPacketQueue(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True)
    data: Any = Field(sa_type=BLOB)


# Create db and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(DB)
