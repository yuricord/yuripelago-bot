"""Utilities for fetching slot data."""

from collections.abc import Sequence
from functools import lru_cache
from typing import Literal

from hikari import Snowflake
from hikari.errors import NotFoundError
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlmodel import Session, select

from archi_bot.db import DB, ArchiSlot, DiscordUser


@lru_cache
def get_archi_slot_name(room_id: str, slot: int) -> str:
    """Get the name for a slot in a specific room.

    Args:
        room_id:
            The room to filter slots from.
        slot:
            The slot index to get the name of.

    Returns:
        The name of the slot if found, or "NULL" if no slot can be found.
    """
    with Session(DB) as sess:
        try:
            res = sess.exec(
                select(ArchiSlot).where(
                    ArchiSlot.id == slot,
                    ArchiSlot.room_id == room_id,
                ),
            ).one()
            name = res.name
        except NoResultFound:
            name = "NULL"

    return name


@lru_cache
def get_slots_for_room(room_id: str) -> Sequence[ArchiSlot] | None:
    """Get all the slots in a specific room by its ID.

    Args:
        room_id:
            The room to fetch slots for.

    Returns:
        Sequence[ArchiSlot] when slots are found.

        None when no slots can be found.
    """
    with Session(DB) as sess:
        try:
            res = sess.exec(
                select(ArchiSlot).where(ArchiSlot.room_id == room_id),
            ).all()
            sess.expunge_all()
            return res
        except SQLAlchemyError:
            return None


@lru_cache
def get_archi_slot_by_name(
    room_id: str,
    name: str,
) -> ArchiSlot | Literal["NoSuchSlot"]:
    """Get a slot in the selected game, by the name of the slot.

    Args:
        room_id:
            The room_id assigned to the game you want to find the slot in.
        name:
            The name of the slot you're searching for.

    Returns:
        Either an `ArchiSlot` when a slot is found, or the literal string "NoSuchSlot" when
        no slot can be found. It's up to the caller to check for success and to handle the error as needed.
    """
    with Session(DB) as sess:
        try:
            res = sess.exec(
                select(ArchiSlot).where(
                    ArchiSlot.room_id == room_id,
                    ArchiSlot.name == name,
                ),
            ).one()
            sess.expunge(res)
            return res
        except NotFoundError:
            return "NoSuchSlot"


def get_slots_for_player(
    room_id: str,
    discord_id: Snowflake,
) -> Sequence[str] | None:
    """Get a list of ArchiSlot names in the current room using the author's discord ID.

    Args:
        room_id:
            The room_id assigned to the game you want to fetch slots for. Generally fetched with
            `get_rando_game(channel_id).room.id`
        discord_id:
            The Discord User ID to fetch slots for. This is `ctx.author.id` if called from a
            command function.

    Returns:
        A sequence of strings, where each string is a slot name assigned to that player in the
        selected game.

        If the player has no slots, None is returned instead.
    """
    with Session(DB) as sess:
        try:
            discord_user = sess.exec(
                select(DiscordUser).where(DiscordUser.id == discord_id),
            ).one()
            sess.expunge(discord_user)
        except NotFoundError:
            new_user = DiscordUser(id=discord_id, slots=[])
            sess.add(new_user)
            sess.commit()
            discord_user = new_user
            sess.refresh(discord_user)
            sess.expunge(discord_user)
    if not discord_user.slots:
        return None

    return [s.name for s in discord_user.slots if s.room_id == room_id]
