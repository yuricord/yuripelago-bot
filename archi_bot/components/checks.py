import os

import arc
import hikari
import requests
from bs4 import BeautifulSoup

from archi_bot.events import DebugMessageEvent
from archi_bot.vars import ArchTrackerURL, DiscordAlertUserID, ItemQueueDirectory

plugin = arc.GatewayPlugin("checks")


@plugin.include
@arc.slash_command("groupcheck", "DMs all checks from the specified slot")
async def groupcheck_command(
    ctx: arc.GatewayContext,
    slot: arc.Option[str, arc.StrParams("Slot name to get checks for")],
    bot: hikari.GatewayBot = arc.inject(),
):
    dm_channel = await ctx.author.fetch_dm_channel()
    try:
        ItemQueueFile = ItemQueueDirectory + slot + ".csv"
        if not os.path.isfile(ItemQueueFile):
            await dm_channel.send("There are no items for " + slot + " :/")
        else:
            k = open(ItemQueueFile, "r")
            ItemQueueLines = k.readlines()
            k.close()

            message = "```You || Item || Sender || Location \n"
            for line in ItemQueueLines:
                message = message + line
                if len(message) > 1900:
                    message = message + "```"
                    await dm_channel.send(message)
                    message = "```"
            message = message + "```"
            await dm_channel.send(message)
    except Exception as e:
        print(e)
        bot.dispatch(
            DebugMessageEvent(
                app=bot, content=f"ERROR IN GROUPCHECK <@{DiscordAlertUserID}>"
            )
        )


@plugin.include
@arc.slash_command("checkcount", "Get check counts for all slots")
async def checkcount_command(
    ctx: arc.GatewayContext,
    bot: hikari.GatewayBot = arc.inject(),
):
    try:
        page = requests.get(ArchTrackerURL)
        soup = BeautifulSoup(page.content, "html.parser")

        # Yoinks table rows from the checks table
        tables = soup.find("table", id="checks-table")
        for slots in tables.find_all("tbody"):
            rows = slots.find_all("tr")

        SlotWidth = 0
        GameWidth = 0
        StatusWidth = 0
        ChecksWidth = 0
        SlotArray = [0]
        GameArray = [0]
        StatusArray = [0]
        ChecksArray = [0]

        # Moves through rows for data
        for row in rows:
            slot = (row.find_all("td")[1].text).strip()
            game = (row.find_all("td")[2].text).strip()
            status = (row.find_all("td")[3].text).strip()
            checks = (row.find_all("td")[4].text).strip()

            SlotArray.append(len(slot))
            GameArray.append(len(game))
            StatusArray.append(len(status))
            ChecksArray.append(len(checks))

        SlotArray.sort(reverse=True)
        GameArray.sort(reverse=True)
        StatusArray.sort(reverse=True)
        ChecksArray.sort(reverse=True)

        SlotWidth = SlotArray[0]
        GameWidth = GameArray[0]
        StatusWidth = StatusArray[0]
        ChecksWidth = ChecksArray[0]

        slot = "Slot"
        game = "Game"
        status = "Status"
        checks = "Checks"
        percent = "%"

        # Preps check message
        checkmessage = (
            "```"
            + slot.ljust(SlotWidth)
            + " || "
            + game.ljust(GameWidth)
            + " || "
            + checks.ljust(ChecksWidth)
            + " || "
            + percent
            + "\n"
        )

        for row in rows:
            slot = (row.find_all("td")[1].text).strip()
            game = (row.find_all("td")[2].text).strip()
            status = (row.find_all("td")[3].text).strip()
            checks = (row.find_all("td")[4].text).strip()
            percent = (row.find_all("td")[5].text).strip()
            checkmessage = (
                checkmessage
                + slot.ljust(SlotWidth)
                + " || "
                + game.ljust(GameWidth)
                + " || "
                + checks.ljust(ChecksWidth)
                + " || "
                + percent
                + "\n"
            )
            if len(checkmessage) > 1900:
                checkmessage = checkmessage + "```"
                await ctx.respond(checkmessage)
                checkmessage = "```"

        # Finishes the check message
        checkmessage = checkmessage + "```"
        await ctx.respond(content=checkmessage)
    except Exception as e:
        print(e)
        bot.dispatch(
            DebugMessageEvent(
                app=bot, content=f"ERROR IN CHECKCOUNT <@{DiscordAlertUserID}>"
            )
        )


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
