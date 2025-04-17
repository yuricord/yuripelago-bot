from functools import lru_cache

from hikari import Snowflake
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from archi_bot.db import (
    DB,
    ArchiSlot,
    DiscordUser,
    Item,
    Location,
)
from archi_bot.vars import ItemFilterLevel

from .archi_games import deactivate_game, get_rando_game
from .slots import get_archi_slot_by_name, get_archi_slot_name, get_slots_for_room
from .writers import write_connection_package, write_data_package, write_room_info

__all__ = [
    "deactivate_game",
    "get_archi_game_name",
    "get_archi_item",
    "get_archi_location_name",
    "get_archi_slot_by_name",
    "get_archi_slot_name",
    "get_discord_user",
    "get_rando_game",
    "get_slots_for_room",
    "item_filter",
    "write_connection_package",
    "write_data_package",
    "write_room_info",
]


@lru_cache
def get_archi_item(game: str, item_id: int):
    with Session(DB) as sess:
        try:
            res = sess.exec(
                select(Item).where(Item.game == game, Item.item_id == item_id),
            ).one()
            name = res.name
        except NoResultFound:
            name = "NULL"

    return name


@lru_cache
def get_archi_location_name(game: str, loc_id: int) -> str:
    with Session(DB) as sess:
        try:
            res = sess.exec(
                select(Location).where(
                    Location.game == game, Location.location_id == loc_id
                )
            ).one()
            name = res.name
        except NoResultFound:
            name = "NULL"

    return name


@lru_cache
def get_archi_game_name(slot: int, room_id: str) -> str:
    with Session(DB) as sess:
        try:
            res = sess.exec(
                select(ArchiSlot).where(
                    ArchiSlot.id == slot and ArchiSlot.room_id == room_id
                )
            ).one()
            game = res.game
        except NoResultFound:
            game = "NULL"

    return game


@lru_cache
def get_discord_user(id: Snowflake) -> DiscordUser:
    with Session(DB) as sess:
        try:
            return sess.exec(select(DiscordUser).where(DiscordUser.id == id)).one()
        except NoResultFound:
            new_user = DiscordUser(id=id, slots=[])
            sess.add(new_user)
            sess.commit()
            return new_user


def item_filter(itemclass: int):
    if ItemFilterLevel == 2:
        return itemclass == 1
    if ItemFilterLevel == 1:
        return itemclass == 1 or itemclass == 2

    return True
