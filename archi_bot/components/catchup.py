import os

import arc
import hikari

from archi_bot.events import DebugMessageEvent
from archi_bot.vars import DiscordAlertUserID, ItemQueueDirectory, RegistrationDirectory

plugin = arc.GatewayPlugin("catchup")


@plugin.include
@arc.slash_command(
    "catchup", "Catch up on missed checks(since you last ran this command!)"
)
async def catchup_command(
    ctx: arc.GatewayContext, bot: hikari.GatewayBot = arc.inject()
):
    try:
        dm_channel = await ctx.author.fetch_dm_channel()
        RegistrationFile = RegistrationDirectory + str(ctx.author.id) + ".csv"
        if not os.path.isfile(RegistrationFile):
            await dm_channel.send("You've not registered for a slot : (")
        else:
            r = open(RegistrationFile, "r")
            RegistrationLines = r.readlines()
            r.close()
            for reglines in RegistrationLines:
                ItemQueueFile = ItemQueueDirectory + reglines.strip() + ".csv"
                if not os.path.isfile(ItemQueueFile):
                    await dm_channel.send(
                        "There are no items for " + reglines.strip() + " :/"
                    )
                    continue
                k = open(ItemQueueFile, "r")
                ItemQueueLines = k.readlines()
                k.close()
                os.remove(ItemQueueFile)

                YouWidth = 0
                ItemWidth = 0
                SenderWidth = 0
                YouArray = [0]
                ItemArray = [0]
                SenderArray = [0]

                for line in ItemQueueLines:
                    YouArray.append(len(line.split("||")[0]))
                    ItemArray.append(len(line.split("||")[1]))
                    SenderArray.append(len(line.split("||")[2]))

                YouArray.sort(reverse=True)
                ItemArray.sort(reverse=True)
                SenderArray.sort(reverse=True)

                YouWidth = YouArray[0]
                ItemWidth = ItemArray[0]
                SenderWidth = SenderArray[0]

                You = "You"
                Item = "Item"
                Sender = "Sender"
                Location = "Location"

                catchup_message = (
                    "```"
                    + You.ljust(YouWidth)
                    + " || "
                    + Item.ljust(ItemWidth)
                    + " || "
                    + Sender.ljust(SenderWidth)
                    + " || "
                    + Location
                    + "\n"
                )
                for line in ItemQueueLines:
                    You = line.split("||")[0].strip()
                    Item = line.split("||")[1].strip()
                    Sender = line.split("||")[2].strip()
                    Location = line.split("||")[3].strip()
                    catchup_message = (
                        catchup_message
                        + You.ljust(YouWidth)
                        + " || "
                        + Item.ljust(ItemWidth)
                        + " || "
                        + Sender.ljust(SenderWidth)
                        + " || "
                        + Location
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
                app=bot, content=f"ERROR IN CATCHUP <@{DiscordAlertUserID}>"
            )
        )


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
