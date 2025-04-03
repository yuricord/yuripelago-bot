from sqlalchemy import Engine
from sqlmodel import Field, Relationship, SQLModel, create_engine

from archi_bot.types import ArchiVersion, SlotType

DB: Engine = create_engine("sqlite:///archi-bot.db")


class Room(SQLModel, table=True):
    id: str
    version: ArchiVersion
    password: bool
    hint_cost: int
    location_check_points: int
    games: list[str]
    datapackage_checksums: dict[str, str]


# Create our DB Entity Classes
class Hint(SQLModel, table=True):
    receiving_player: int
    finding_player: int
    location: int
    item: int
    found: bool
    entrance: str = ""
    item_flags: int = 0
    room_id: str = Field(foreign_key="room.id")


class Game(SQLModel, table=True):
    name: str
    package_checksum: str


class ItemGroup(SQLModel, table=True):
    # Custom Table Name for safety
    __tablename__: str = "item_group"  # type:ignore
    name: str
    game: str = Field(foreign_key="game.name")


class Item(SQLModel, table=True):
    item_id: int
    game: str = Field(foreign_key="game.name")
    name: str
    group: str = Field(foreign_key="item_group.name")


class LocationGroup(SQLModel, table=True):
    __tablename__: str = "location_group"  # type:ignore
    name: str
    game: str = Field(foreign_key="game.name")


class Location(SQLModel, table=True):
    location_id: int
    game: str = Field(foreign_key="game.name")
    name: str
    group: str = Field(foreign_key="location_group.name")


class DiscordSlotLink(SQLModel, table=True):
    slot_id: int | None = Field(default=None, foreign_key="slot.id", primary_key=True)
    discord_id: int | None = Field(
        default=None, foreign_key="discord_user.id", primary_key=True
    )


class Slot(SQLModel, table=True):
    name: str
    game: str
    type: SlotType
    group_members: list[int] = []  # Only populated if `self.type == SlotType.group`
    room_id: str = Field(foreign_key="room.id")
    players: list["DiscordUser"] = Relationship(
        back_populates="slots", link_model=DiscordSlotLink
    )


class DiscordUser(SQLModel, table=True):
    __tablename__: str = "discord_user"  # type:ignore
    id: int
    slots: list[Slot] = Relationship(
        back_populates="players", link_model=DiscordSlotLink
    )


# Create db and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(DB)
