from typing import Literal

from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from archi_bot.db import DB, RandoGame


def get_rando_game(channel_id: int) -> RandoGame | Literal["NoSuchGame"]:
    with Session(DB) as sess:
        try:
            return sess.exec(
                select(RandoGame).where(RandoGame.game_channel == channel_id)
            ).one()
        except NoResultFound:
            return "NoSuchGame"


def deactivate_game(channel_id: int) -> tuple[bool, str] | Literal["NoActiveGame"]:
    """Deactivate the current Archipelago game in the channel specified.

    Args:
        channel_id:
            The channel to find and stop the game for.
    """
    rando_game = get_rando_game(channel_id)
    if rando_game == "NoSuchGame" or rando_game.active == False:
        return "NoActiveGame"

    with Session(DB) as sess:
        rando_game.active = False
        sess.add(rando_game)
        sess.commit()
    if rando_game.display_name:
        return (True, rando_game.display_name)

    return (True, rando_game.room_id)
