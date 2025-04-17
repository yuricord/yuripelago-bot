import asyncio

import arc
import hikari
from sqlalchemy import Engine
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from archi_bot.db import ArchiRoom, RandoGame
from archi_bot.tracker_client import TrackerClient
from archi_bot.utils.archi_games import deactivate_game

plugin = arc.GatewayPlugin("management")


@plugin.include
@arc.slash_command("create_game", "Register a new Archipelago game with ArchiBot.")
async def creategame_command(
    ctx: arc.GatewayContext,
    port: arc.Option[
        int, arc.IntParams("The server-provided port number for your game.")
    ],
    tracker_url: arc.Option[
        str,
        arc.StrParams(
            "The server's tracker URL for the page. Generally formatted like `server_url/tracker/<something>`"
        ),
    ],
    room_url: arc.Option[
        str,
        arc.StrParams(
            "The room URL for your game. Same as `tracker_url`, but formatted like `server_url/room/<something>`"
        ),
    ],
    spoil_traps: arc.Option[
        bool,
        arc.BoolParams(
            "(optional) If True, the bot will display traps in certain commands like `catchup. Defaults to True.`"
        ),
    ] = True,
    display_name: arc.Option[
        str | None, arc.StrParams("(optional) The display name for the game in logs.")
    ] = None,
    server_url: arc.Option[
        str,
        arc.StrParams(
            "(optional) The server that the game is hosted on. Defaults to wss://archipelago.gg"
        ),
    ] = "wss://archipelago.gg",
    bot_slot: arc.Option[
        str,
        arc.StrParams(
            "(optional) The game slot assigned to the bot. Defaults to ArchiBot."
        ),
    ] = "ArchiBot",
    db: Engine = arc.inject(),
) -> None:
    # Immediately defer so that we can do work in the background.
    await ctx.defer()
    # Check if there is already a game registered to this channel. We don't support multiple games per channel,
    # so error if so.
    with Session(db) as sess:
        try:
            res = sess.exec(
                select(RandoGame).where(
                    RandoGame.game_channel == ctx.channel_id, RandoGame.active == True
                ),
            ).one()
            # Already an active game in the same channel.
            if res:
                await ctx.respond(
                    "Error: There is already an active game registered for this channel. Please try again in a new channel, or stop the old game!"
                )
                return
        except NoResultFound:
            pass
        # Check if a game with the same tracker_url exists. If this is true, it must have been
        # registered before.
        try:
            res = sess.exec(
                select(RandoGame).where(RandoGame.tracker_url == tracker_url),
            ).one()
            # There's already a registered game with the same tracker url.
            if res:
                await ctx.respond(
                    f"Error: There is already a game registered from the same room at <#{res.game_channel}>!"
                )
                return
        except NoResultFound:
            pass

        # No registered game with same tracker URL or in the same channel, so register this game.
        room_id = room_url.split("/")[4]
        new_game = RandoGame(
            display_name=display_name,
            server_url=server_url,
            port=port,
            bot_slot=bot_slot,
            game_channel=ctx.channel_id,
            tracker_url=tracker_url,
            room_url=room_url,
            spoil_traps=spoil_traps,
            room_id=room_id,
        )
        sess.add(new_game)
        sess.commit()
        temp_client = TrackerClient(
            server_uri=server_url,
            port=port,
            slot_name=bot_slot,
            room_id=room_id,
            verbose_logging=True,
        )
        await temp_client.start()
        await asyncio.sleep(1)
        registered_room = None
        while not registered_room:
            await asyncio.sleep(1)
            try:
                temp_room = sess.exec(
                    select(ArchiRoom).where(ArchiRoom.id == room_id)
                ).one()
                registered_room = temp_room
            except NoResultFound:
                print(f"Could not find room {room_id} in database")
                continue

        await temp_client.connection.close()

        await ctx.respond(f"Registered new game `{display_name}`!")

    return


@plugin.include
@arc.with_hook(arc.utils.has_permissions(hikari.Permissions.MANAGE_THREADS))
@arc.slash_command("stop_game", "Stop the bot for the game in this channel")
async def stop_game_command(ctx: arc.GatewayContext) -> None:
    res = deactivate_game(ctx.channel_id)
    if res == "NoActiveGame":
        await ctx.respond(
            "Error: No active game in channel. Please ensure you're running this command in a channel with an active game."
        )
        return

    await ctx.respond(f"Deactivated game {res[1]}")


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
