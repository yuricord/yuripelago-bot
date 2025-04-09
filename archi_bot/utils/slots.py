from functools import lru_cache
from typing import Literal, Sequence

from hikari import Snowflake
from hikari.errors import NotFoundError
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from archi_bot.db import DB, ArchiSlot

from . import get_discord_user


@lru_cache
def get_archi_slot_name(slot: int, room_id: str) -> str:
    with Session(DB) as sess:
        try:
            res = sess.exec(
                select(ArchiSlot).where(
                    ArchiSlot.id == slot and ArchiSlot.room_id == room_id
                )
            ).one()
            name = res.name
        except NoResultFound:
            name = "NULL"

    return name


@lru_cache
def get_slots_for_room(room_id: str) -> Sequence[ArchiSlot] | None:
    with Session(DB) as sess:
        try:
            res = sess.exec(select(ArchiSlot).where(ArchiSlot.room_id == room_id)).all()
            return res
        except Exception:
            return


@lru_cache
def get_archi_slot_by_name(
    room_id: str, slot: str
) -> ArchiSlot | Literal["NoSuchSlot"]:
    with Session(DB) as sess:
        try:
            res = sess.exec(
                select(ArchiSlot).where(
                    ArchiSlot.room_id == room_id, ArchiSlot.name == slot
                )
            ).one()
            return res
        except NotFoundError:
            return "NoSuchSlot"


def get_slots_for_player(
    room_id: str,
    discord_id: Snowflake,
) -> Sequence[str] | None:
    """Get a list of ArchiSlot names in the current room using the author's discord ID."""
    discord_user = get_discord_user(discord_id)
    if not discord_user.slots:
        return
    else:
        return [s.name for s in discord_user.slots if s.room_id == room_id]
