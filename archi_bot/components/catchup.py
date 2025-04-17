import os
from pathlib import Path

import arc
import hikari
from aiofiles import open

from archi_bot.events import DebugMessageEvent
from archi_bot.utils import get_rando_game
from archi_bot.utils.slots import get_slots_for_player
from archi_bot.vars import ItemQueueDirectory

plugin = arc.GatewayPlugin("catchup")


@plugin.include
@arc.slash_command(
    "catchup",
    "Catch up on missed checks since you last ran this command",
)
async def catchup_command(
    ctx: arc.GatewayContext, bot: hikari.GatewayBot = arc.inject()
) -> None:
    try:
        dm_channel = await ctx.author.fetch_dm_channel()
        rando_game = get_rando_game(ctx.channel_id)
        if rando_game == "NoSuchGame":
            await ctx.respond(
                "Please make sure you're running this in the game's assigned channel!"
            )
            return
        slots = get_slots_for_player(rando_game.room.id, ctx.author.id)
        if not slots:
            await dm_channel.send("You're not registered for any slots in this game!")
        else:
            for slot in slots:
                item_queue_file = Path(ItemQueueDirectory) / f"{slot}.csv"
                if not item_queue_file.is_file():
                    await dm_channel.send(f"There are no items for {slot}!")
                    continue
                async with open(item_queue_file) as f:
                    item_queue_lines = await f.readlines()

                item_queue_file.unlink()

                you_width = 0
                item_width = 0
                sender_width = 0
                you_array = [0]
                item_array = [0]
                sender_array = [0]

                for line in item_queue_lines:
                    you_array.append(len(line.split("||")[0]))
                    item_array.append(len(line.split("||")[1]))
                    sender_array.append(len(line.split("||")[2]))

                you_array.sort(reverse=True)
                item_array.sort(reverse=True)
                sender_array.sort(reverse=True)

                you_width = you_array[0]
                item_width = item_array[0]
                sender_width = sender_array[0]

                you = "You"
                item = "Item"
                sender = "Sender"
                location = "Location"

                catchup_message = (
                    "```"
                    + you.ljust(you_width)
                    + " || "
                    + item.ljust(item_width)
                    + " || "
                    + sender.ljust(sender_width)
                    + " || "
                    + location
                    + "\n"
                )
                for line in item_queue_lines:
                    you = line.split("||")[0].strip()
                    item = line.split("||")[1].strip()
                    sender = line.split("||")[2].strip()
                    location = line.split("||")[3].strip()
                    catchup_message = (
                        catchup_message
                        + you.ljust(you_width)
                        + " || "
                        + item.ljust(item_width)
                        + " || "
                        + sender.ljust(sender_width)
                        + " || "
                        + location
                        + "\n"
                    )

                    if len(catchup_message) > 1500:
                        catchup_message = catchup_message + "```"
                        await dm_channel.send(catchup_message)
                        catchup_message = "```"
                catchup_message = catchup_message + "```"
                await dm_channel.send(catchup_message)
    except Exception as e:
        print(e)
        bot.dispatch(
            DebugMessageEvent(
                app=bot,
                content=f"""
                Error with CatchUp:
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
