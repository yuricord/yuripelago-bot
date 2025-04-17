from pathlib import Path

import arc
import hikari
from aiofiles import open
from bs4 import BeautifulSoup
from httpx import AsyncClient

from archi_bot.events import DebugMessageEvent
from archi_bot.vars import ArchTrackerURL, ItemQueueDirectory

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
        item_queue_file = Path(ItemQueueDirectory) / f"{slot}.csv"
        if not item_queue_file.is_file():
            await dm_channel.send(f"There are no items for {slot}!")
        else:
            async with open(item_queue_file) as f:
                item_queue_lines = await f.readlines()

            message = "```You || Item || Sender || Location \n"
            for line in item_queue_lines:
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
                app=bot,
                content=f"""
                    Error with Group Check command:
                    ```
                    {e}
                    ```
                """,
            )
        )


@plugin.include
@arc.slash_command("checkcount", "Get check counts for all slots")
async def checkcount_command(
    ctx: arc.GatewayContext,
    bot: hikari.GatewayBot = arc.inject(),
):
    try:
        req_sess = AsyncClient()
        page = await req_sess.get(ArchTrackerURL)
        soup = BeautifulSoup(page.content, "html.parser")
        await req_sess.aclose()

        # Yoinks table rows from the checks table
        tables = soup.find("table", id="checks-table")
        for slots in tables.find_all("tbody"):
            rows = slots.find_all("tr")

        slot_width = 0
        game_width = 0
        status_width = 0
        checks_width = 0
        slot_array = [0]
        game_array = [0]
        status_array = [0]
        checks_array = [0]

        # Moves through rows for data
        for row in rows:
            slot = (row.find_all("td")[1].text).strip()
            game = (row.find_all("td")[2].text).strip()
            status = (row.find_all("td")[3].text).strip()
            checks = (row.find_all("td")[4].text).strip()

            slot_array.append(len(slot))
            game_array.append(len(game))
            status_array.append(len(status))
            checks_array.append(len(checks))

        slot_array.sort(reverse=True)
        game_array.sort(reverse=True)
        status_array.sort(reverse=True)
        checks_array.sort(reverse=True)

        slot_width = slot_array[0]
        game_width = game_array[0]
        status_width = status_array[0]
        checks_width = checks_array[0]

        slot = "Slot"
        game = "Game"
        status = "Status"
        checks = "Checks"
        percent = "%"

        # Preps check message
        checkmessage = (
            "```"
            + slot.ljust(slot_width)
            + " || "
            + game.ljust(game_width)
            + " || "
            + checks.ljust(checks_width)
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
                + slot.ljust(slot_width)
                + " || "
                + game.ljust(game_width)
                + " || "
                + checks.ljust(checks_width)
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
                app=bot,
                content=f"""
                    Error with Check Count command:
                    ```
                    {e}
                    ```
                """,
            )
        )


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
