import os

import arc
import hikari

from bot_vars import RegistrationDirectory
from events import DebugMessageEvent

plugin = arc.GatewayPlugin("register")


@plugin.include
@arc.slash_command("register", "Register a slot in the current game")
async def register_command(
    ctx: arc.GatewayContext,
    slot: arc.Option[str, arc.StrParams("The slot name to register.")],
    bot: hikari.GatewayBot = arc.inject(),
):
    try:
        ArchSlot = slot
        Sender = ctx.author.id
        RegistrationFile = RegistrationDirectory + str(Sender) + ".csv"
        RegistrationContent = ArchSlot + "\n"
        # Generate the Registration File if it doesn't exist
        o = open(RegistrationFile, "a")
        o.close()
        # Get contents of the registration file and save it to 'line'
        o = open(RegistrationFile, "r")
        line = o.read()
        o.close()
        # Check the registration file for ArchSlot, if they are not registered; do so. If they already are; tell them.
        if ArchSlot not in line:
            message = "Registering " + ctx.author.mention + " for slot " + ArchSlot
            await ctx.respond(message)
            o = open(RegistrationFile, "a")
            o.write(RegistrationContent)
            o.close()
        else:
            await ctx.respond("You're already registered for that slot.")
    except Exception as e:
        print(e)
        bot.dispatch(
            DebugMessageEvent(content="ERROR IN REGISTER <@" + DiscordAlertUserID + ">")
        )


@plugin.include
@arc.slash_command("clearreg", "Delete all known registrations for yourself")
async def clearreg_command(
    ctx: arc.GatewayContext, bot: hikari.GatewayBot = arc.inject()
):
    try:
        Sender = ctx.author.id
        RegistrationFile = RegistrationDirectory + str(Sender) + ".csv"
        os.remove(RegistrationFile)
    except Exception as e:
        print(e)
        bot.dispatch(
            DebugMessageEvent(content="ERROR IN CLEARREG <@" + DiscordAlertUserID + ">")
        )


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
