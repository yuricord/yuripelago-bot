import os

import arc
import hikari

from bot_vars import DeathFileLocation
from events import DebugMessageEvent, MainChannelMessageEvent

plugin = arc.GatewayPlugin("info")


@plugin.include
@arc.slash_command("deathcount", "Get the death count for all slots")
async def deathcount_command(
    ctx: arc.GatewayContext, bot: hikari.GatewayBot = arc.inject()
):
    try:
        d = open(DeathFileLocation, "r")
        DeathLines = d.readlines()
        d.close()
        deathdict = {}
        for deathline in DeathLines:
            DeathUser = deathline.split("||")[6]
            DeathUser = DeathUser.split("\n")[0]

            if not DeathUser in deathdict:
                deathdict[DeathUser] = 1
            else:
                deathdict[DeathUser] = deathdict[DeathUser] + 1

        deathdict = {key: value for key, value in sorted(deathdict.items())}
        deathnames = []
        deathcounts = []
        message = "**Death Counter:**\n```"
        deathkeys = deathdict.keys()
        for key in deathkeys:
            deathnames.append(str(key))
            deathcounts.append(int(deathdict[key]))
            message = message + "\n" + str(key) + ": " + str(deathdict[key])
        message = message + "```"
        bot.dispatch(MainChannelMessageEvent(content=message))
    except:
        bot.dispatch(
            DebugMessageEvent(content="ERROR DEATHCOUNT <@" + DiscordAlertUserID + ">")
        )
