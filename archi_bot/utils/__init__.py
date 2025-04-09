from functools import lru_cache
from typing import Literal

from hikari import Snowflake
from hikari.errors import NotFoundError
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from archi_bot.db import (
    DB,
    ArchiPlayer,
    ArchiRoom,
    ArchiSlot,
    DiscordUser,
    GameDataPackage,
    Item,
    Location,
    RandoGame,
)
from archi_bot.models.packets import (
    ConnectedPacket,
    DataPackagePacket,
    RoomInfoPacket,
)
from archi_bot.models.server import ArchiGameData
from archi_bot.vars import ItemFilterLevel

from .slots import get_archi_slot_by_name, get_archi_slot_name, get_slots_for_room

__all__ = [
    "write_data_package",
    "write_connection_package",
    "write_room_info",
    "get_archi_item",
    "get_archi_location_name",
    "get_archi_game_name",
    "get_rando_game",
    "get_archi_slot_name",
    "get_archi_slot_by_name",
    "get_discord_user",
    "get_slots_for_room",
    "item_filter",
]


def write_data_package(packet: DataPackagePacket):
    with Session(DB) as sess:
        orig_data: ArchiGameData
        for orig_game, orig_data in packet.data["games"].items():
            try:
                cur_game = sess.exec(
                    select(GameDataPackage).where(GameDataPackage.name == orig_game)
                ).one()
                if cur_game.package_checksum == orig_data.checksum:
                    # If checksums match, then don't insert any data
                    return
                else:
                    # Current stored checksum doesn't match, so drop current data and re-insert it.
                    sess.delete(select(Item).where(Item.game == orig_game))
                    sess.delete(select(Location).where(Location.game == orig_game))
                    sess.delete(cur_game)
                    sess.commit()
            except NoResultFound:
                # If there's no checksum(so no game data for this game in the DB), add the current data
                pass

            game: GameDataPackage = GameDataPackage(
                name=orig_game, package_checksum=orig_data.checksum
            )
            sess.add(game)
            for orig_item, orig_id in orig_data.item_name_to_id.items():
                item: Item = Item(name=orig_item, item_id=orig_id, game=game.name)
                sess.add(item)
            for orig_loc, orig_id in orig_data.location_name_to_id.items():
                loc: Location = Location(
                    name=orig_loc, location_id=orig_id, game=game.name
                )
                sess.add(loc)

            sess.commit()


def write_connection_package(packet: ConnectedPacket, room_id: str):
    with Session(DB) as sess:
        try:
            # Find all slots with the same room ID. If they exist, we must have inserted all
            # of these rooms already, so do nothing.
            res = sess.exec(select(ArchiSlot).where(ArchiSlot.room_id == room_id)).all()
            if res:
                # We've found slots. Don't do anything
                pass
        except NoResultFound:
            # We haven't found any slots! Insert all of the ones in this connection package.
            for slot, data in packet.slot_info.items():
                s = ArchiSlot(
                    id=slot,
                    name=data.name,
                    game=data.game,
                    type=data.type,
                    group_members=data.group_members,
                    room_id=room_id,
                )
                sess.add(s)
            sess.commit()
            # Insert all the players
            for player in packet.players:
                p = ArchiPlayer(
                    team=player.team,
                    slot=player.slot,
                    name=player.name,
                    room_id=room_id,
                )
                sess.add(p)
            sess.commit()


def write_room_info(packet: RoomInfoPacket) -> str:
    with Session(DB) as sess:
        try:
            # Check if there's a room with the same ID already in the database
            # If there is, do nothing, since we assume we've already inserted the needed data.
            res = sess.exec(
                select(ArchiRoom).where(ArchiRoom.id == packet.seed_name)
            ).one()
            if res:
                pass
        except NoResultFound:
            # If there's no results found, we must not have been in this room before.
            # Therefore, write this room data to the database.
            room = ArchiRoom(
                id=packet.seed_name,
                version=packet.generator_version.model_dump(),
                password=packet.password,
                hint_cost=packet.hint_cost,
                location_check_points=packet.location_check_points,
            )
            sess.add(room)
            sess.commit()

    # Return the room id, to be passed to `write_connection_package()`.
    return packet.seed_name


@lru_cache
def get_archi_item(game: str, id: int, room_id: str):
    with Session(DB) as sess:
        try:
            res = sess.exec(
                select(Item).where(Item.game == game, Item.item_id == id)
            ).one()
            name = res.name
        except NoResultFound:
            name = "NULL"

    return name


@lru_cache
def get_archi_location_name(game: str, id: int, room_id: str) -> str:
    with Session(DB) as sess:
        try:
            res = sess.exec(
                select(Location).where(
                    Location.game == game, Location.location_id == id
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
def get_rando_game(channel_id: int) -> RandoGame | Literal["NoSuchGame"]:
    with Session(DB) as sess:
        try:
            res = sess.exec(
                select(RandoGame).where(RandoGame.game_channel == channel_id)
            ).one()
            return res
        except NotFoundError:
            return "NoSuchGame"


def get_discord_user(id: Snowflake) -> DiscordUser:
    with Session(DB) as sess:
        try:
            res = sess.exec(select(DiscordUser).where(DiscordUser.id == id)).one()
            return res
        except NotFoundError:
            new_user = DiscordUser(id=id, slots=[])
            sess.add(new_user)
            sess.commit()
            return new_user


def item_filter(itemclass):
    if ItemFilterLevel == 2:
        if itemclass == 1:
            return True
        else:
            return False
    elif ItemFilterLevel == 1:
        if itemclass == 1 or itemclass == 2:
            return True
        else:
            return False
    elif ItemFilterLevel == 0:
        return True
    else:
        return True
