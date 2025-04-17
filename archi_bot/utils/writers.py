"""Utilities for writing various types of data for Archipelago games."""

from typing import TYPE_CHECKING

from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from archi_bot.db import (
    DB,
    ArchiPlayer,
    ArchiRoom,
    ArchiSlot,
    GameDataPackage,
    Item,
    Location,
)
from archi_bot.models.packets import (
    ConnectedPacket,
    DataPackagePacket,
    RoomInfoPacket,
)

if TYPE_CHECKING:
    from archi_bot.models.server import ArchiGameData


def write_data_package(packet: DataPackagePacket):
    with Session(DB) as sess:
        orig_data: ArchiGameData
        for orig_game, orig_data in packet.data["games"].items():
            try:
                cur_game = sess.exec(
                    select(GameDataPackage).where(GameDataPackage.name == orig_game),
                ).one()
                if cur_game.package_checksum == orig_data.checksum:
                    # If checksums match, then don't insert any data
                    return
                # Current stored checksum doesn't match, so drop current data and re-insert it.
                sess.delete(select(Item).where(Item.game == orig_game))
                sess.delete(select(Location).where(Location.game == orig_game))
                sess.delete(cur_game)
                sess.commit()
            except NoResultFound:
                # If there's no checksum(so no game data for this game in the DB), add the current data
                pass

            game: GameDataPackage = GameDataPackage(
                name=orig_game,
                package_checksum=orig_data.checksum,
            )
            sess.add(game)
            for orig_item, orig_id in orig_data.item_name_to_id.items():
                item: Item = Item(name=orig_item, item_id=orig_id, game=game.name)
                sess.add(item)
            for orig_loc, orig_id in orig_data.location_name_to_id.items():
                loc: Location = Location(
                    name=orig_loc,
                    location_id=orig_id,
                    game=game.name,
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


def write_room_info(packet: RoomInfoPacket, room_id: str | None) -> str:
    if not room_id:
        room_id = packet.seed_name
    with Session(DB, expire_on_commit=True) as sess:
        try:
            # Check if there's a room with the same ID already in the database
            # If there is, do nothing, since we assume we've already inserted the needed data.
            res = sess.exec(
                select(ArchiRoom).where(ArchiRoom.id == packet.seed_name),
            ).one()
            if res:
                pass
        except NoResultFound:
            # If there's no results found, we must not have been in this room before.
            # Therefore, write this room data to the database.
            room = ArchiRoom(
                id=room_id,
                version=packet.generator_version.model_dump(),
                password=packet.password,
                hint_cost=packet.hint_cost,
                location_check_points=packet.location_check_points,
            )
            sess.add(room)
            sess.commit()

    # Return the room id, to be passed to `write_connection_package()`.
    return packet.seed_name
