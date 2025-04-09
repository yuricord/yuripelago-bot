import arc
import hikari
from hikari.errors import NotFoundError
from sqlalchemy import Engine
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from archi_bot.db import DiscordSlotLink
from archi_bot.events import DebugMessageEvent
from archi_bot.utils import get_archi_slot_by_name, get_discord_user, get_rando_game
from archi_bot.utils.autocomplete import (
    autocomplete_registered_slot_names,
    autocomplete_slot_names,
)

plugin = arc.GatewayPlugin("register")


@plugin.include
@arc.slash_command("register", "Register a slot in the current game")
async def register_command(
    ctx: arc.GatewayContext,
    slot: arc.Option[
        str,
        arc.StrParams(
            "The slot name to register.", autocomplete_with=autocomplete_slot_names
        ),
    ],
    bot: hikari.GatewayBot = arc.inject(),
    db: Engine = arc.inject(),
):
    await ctx.defer()
    try:
        # Add a link between the slot <-> Discord user using the DiscordSlotLink table
        # Error if:
        # # Already registered for slot

        # Look up game the command came from(by channel ID), and get its room id
        rando_game = get_rando_game(ctx.channel_id)
        # Error if no game found for channel
        if rando_game == "NoSuchGame":
            await ctx.respond(
                "Error: No game registered for this channel. Please make sure you're running this in the game's assigned channel!"
            )
            return
        # find the slot we're registering for
        archi_slot = get_archi_slot_by_name(rando_game.room.id, slot)

        # Error if no slot found
        if archi_slot == "NoSuchSlot":
            await ctx.respond(
                f"Error: No slot with the name `{slot}` in this game. Please make sure you're registering with the right game, and that you've spelled the slot name correctly!"
            )
            return
        discord_user = get_discord_user(ctx.author.id)
        # Check the registration file for ArchSlot, if they are not registered; do so. If they already are; tell them.
        with Session(db) as sess:
            try:
                link = sess.exec(
                    select(DiscordSlotLink).where(
                        DiscordSlotLink.slot_id == archi_slot.global_id,
                        DiscordSlotLink.discord_id == discord_user.id,
                    )
                ).one()
            except NotFoundError:
                # No registration for this player+slot, so register them
                discord_user.slots.append(archi_slot)
                sess.add(discord_user)
                sess.commit()
                await ctx.respond(f"Registered you for slot `{slot}`")
                return

            # This link already exists, so they must already be registered
            if link:
                await ctx.respond("You're already registered for this slot!")
                return
    except Exception as e:
        print(e)
        bot.dispatch(DebugMessageEvent(app=bot, content="Error with Registration"))


@plugin.include
@arc.slash_command("unregister", "Unregister one of your slots in this game")
async def unregister_command(
    ctx: arc.GatewayContext,
    slot: arc.Option[
        str,
        arc.StrParams(
            "Slot name", autocomplete_with=autocomplete_registered_slot_names
        ),
    ],
    db: Engine = arc.inject(),
):
    await ctx.defer()
    # Fetch needed data
    rando_game = get_rando_game(ctx.channel_id)
    if rando_game == "NoSuchGame":
        await ctx.respond(
            "Error: No game registered for this channel. Please make sure you're running this in the game's assigned channel!"
        )
        return
    # find the slot we're registering for
    archi_slot = get_archi_slot_by_name(rando_game.room.id, slot)
    # Error if no slot found
    if archi_slot == "NoSuchSlot":
        await ctx.respond(
            f"Error: No slot with the name `{slot}` in this game. Please make sure you're registering with the right game, and that you've spelled the slot name correctly!"
        )
        return
    with Session(db) as sess:
        try:
            # Find DiscordUser <-> ArchiSlot link.
            res = sess.exec(
                select(DiscordSlotLink).where(
                    DiscordSlotLink.discord_id == ctx.author.id,
                    DiscordSlotLink.slot_id == archi_slot.global_id,
                )
            ).one()
        except NoResultFound:
            # Not registered for that slot, send an error
            await ctx.respond(
                "Error: You're not currently registered for that slot. Please make sure you typed the slot correctly!"
            )
            return
        # If found, remove the link
        if res:
            sess.delete(res)
            sess.commit()
            await ctx.respond(
                f"Removed your registration for slot `{slot}` in this game."
            )
        return


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
