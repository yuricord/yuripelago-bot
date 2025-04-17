import os

import arc
import hikari
import hikari.messages
from bs4 import BeautifulSoup
from httpx import AsyncClient
from sqlalchemy import Engine

from archi_bot.events import DebugMessageEvent
from archi_bot.utils import get_rando_game
from archi_bot.utils.slots import get_slots_for_player
from archi_bot.vars import ArchTrackerURL

plugin = arc.GatewayPlugin("hints")


@plugin.include
@arc.slash_command("hints", "Sends you all your hints.")
async def hints_command(
    ctx: arc.GatewayContext,
    bot: hikari.GatewayBot = arc.inject(),
    db: Engine = arc.inject(),
):
    await ctx.defer(flags=hikari.messages.MessageFlag.LOADING)
    try:
        dm_channel = await ctx.author.fetch_dm_channel()
        rows = None

        sess = AsyncClient()
        page = await sess.get(ArchTrackerURL)
        soup = BeautifulSoup(page.content, "html.parser")
        await sess.aclose()

        # Yoinks table rows from the checks table
        tables = soup.find("table", id="hints-table")

        for slots in tables.find_all("tbody"):
            rows = slots.find_all("tr")

        if not rows:
            await ctx.respond(
                "Error: Exception fetching hints. Please try again in a bit!"
            )
            return

        rando_game = get_rando_game(ctx.channel_id)
        if rando_game == "NoSuchGame":
            await ctx.respond(
                "Error: No registered game for this channel. Please ensure you're running this in the game's channel!"
            )
            return
        slots = get_slots_for_player(rando_game.room.id, ctx.author.id)
        if not slots:
            await dm_channel.send("You're not registered to any slots!")
        else:
            message = f"""
            **Here are all of the hints assigned to
            {",".join(slots)}
            **:
            """
            await dm_channel.send(message)

            for slot in slots:
                finder_width = 0
                receiver_width = 0
                item_width = 0
                location_width = 0
                game_width = 0
                entrance_width = 0
                finder_array = [0]
                reciever_array = [0]
                item_array = [0]
                location_array = [0]
                game_array = [0]
                entrance_array = [0]

                # Moves through rows for data
                for row in rows:
                    found = (row.find_all("td")[6].text).strip()
                    if found == "✔":
                        continue

                    finder = (row.find_all("td")[0].text).strip()
                    receiver = (row.find_all("td")[1].text).strip()
                    item = (row.find_all("td")[2].text).strip()
                    location = (row.find_all("td")[3].text).strip()
                    game = (row.find_all("td")[4].text).strip()
                    entrance = (row.find_all("td")[5].text).strip()

                    if slot == finder:
                        finder_array.append(len(finder))
                        reciever_array.append(len(receiver))
                        item_array.append(len(item))
                        location_array.append(len(location))
                        game_array.append(len(game))
                        entrance_array.append(len(entrance))

                finder_array.sort(reverse=True)
                reciever_array.sort(reverse=True)
                item_array.sort(reverse=True)
                location_array.sort(reverse=True)
                game_array.sort(reverse=True)
                entrance_array.sort(reverse=True)

                finder_width = finder_array[0]
                receiver_width = reciever_array[0]
                item_width = item_array[0]
                location_width = location_array[0]
                game_width = game_array[0]
                entrance_width = entrance_array[0]

                finder = "Finder"
                receiver = "Receiver"
                item = "Item"
                location = "Location"
                game = "Game"
                entrance = "Entrance"

                # Preps check message
                checkmessage = (
                    "```"
                    + finder.ljust(finder_width)
                    + " || "
                    + receiver.ljust(receiver_width)
                    + " || "
                    + item.ljust(item_width)
                    + " || "
                    + location.ljust(location_width)
                    + " || "
                    + game.ljust(game_width)
                    + " || "
                    + entrance
                    + "\n"
                )
                for row in rows:
                    found = (row.find_all("td")[6].text).strip()
                    if found == "✔":
                        continue

                    finder = (row.find_all("td")[0].text).strip()
                    receiver = (row.find_all("td")[1].text).strip()
                    item = (row.find_all("td")[2].text).strip()
                    location = (row.find_all("td")[3].text).strip()
                    game = (row.find_all("td")[4].text).strip()
                    entrance = (row.find_all("td")[5].text).strip()

                    if slot == finder:
                        checkmessage = (
                            checkmessage
                            + finder.ljust(finder_width)
                            + " || "
                            + receiver.ljust(receiver_width)
                            + " || "
                            + item.ljust(item_width)
                            + " || "
                            + location.ljust(location_width)
                            + " || "
                            + game.ljust(game_width)
                            + " || "
                            + entrance
                            + "\n"
                        )

                if len(checkmessage) > 1500:
                    checkmessage = checkmessage + "```"
                    await dm_channel.send(checkmessage)
                    checkmessage = "```"

                # Caps off the message
                checkmessage = checkmessage + "```"
                await dm_channel.send(checkmessage)
    except Exception as e:
        bot.dispatch(
            DebugMessageEvent(app=bot, content=f"Error listing hints ```{e}```")
        )


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
