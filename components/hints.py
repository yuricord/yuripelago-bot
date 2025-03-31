import arc
import hikari
import hikari.messages
import requests
import os
from bs4 import BeautifulSoup

from bot_vars import RegistrationDirectory, ArchTrackerURL
from events import DebugMessageEvent, MainChannelMessageEvent

plugin = arc.GatewayPlugin("hints")


@plugin.include
@arc.slash_command("hints", "Sends you all your hints.")
async def hints_command(ctx: arc.GatewayContext, bot: hikari.GatewayBot = arc.inject()):
    await ctx.defer(flags=hikari.messages.MessageFlag.LOADING)
    try:
        dm_channel = await ctx.author.fetch_dm_channel()

        page = requests.get(ArchTrackerURL)
        soup = BeautifulSoup(page.content, "html.parser")

        # Yoinks table rows from the checks table
        tables = soup.find("table", id="hints-table")
        if not tables:

        for slots in tables.find_all("tbody"):
            rows = slots.find_all("tr")

        RegistrationFile = RegistrationDirectory + str(ctx.author.id) + ".csv"
        if not os.path.isfile(RegistrationFile):
            await dm_channel.send("You're not registered to any slots!")
        else:
            r = open(RegistrationFile, "r")
            RegistrationLines = r.readlines()
            r.close()
            for reglines in RegistrationLines:
                message = (
                    "**Here are all of the hints assigned to "
                    + reglines.strip()
                    + ":**"
                )
                await dm_channel.send(message)

                FinderWidth = 0
                ReceiverWidth = 0
                ItemWidth = 0
                LocationWidth = 0
                GameWidth = 0
                EntranceWidth = 0
                FinderArray = [0]
                ReceiverArray = [0]
                ItemArray = [0]
                LocationArray = [0]
                GameArray = [0]
                EntranceArray = [0]

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

                    if reglines.strip() == finder:
                        FinderArray.append(len(finder))
                        ReceiverArray.append(len(receiver))
                        ItemArray.append(len(item))
                        LocationArray.append(len(location))
                        GameArray.append(len(game))
                        EntranceArray.append(len(entrance))

                FinderArray.sort(reverse=True)
                ReceiverArray.sort(reverse=True)
                ItemArray.sort(reverse=True)
                LocationArray.sort(reverse=True)
                GameArray.sort(reverse=True)
                EntranceArray.sort(reverse=True)

                FinderWidth = FinderArray[0]
                ReceiverWidth = ReceiverArray[0]
                ItemWidth = ItemArray[0]
                LocationWidth = LocationArray[0]
                GameWidth = GameArray[0]
                EntranceWidth = EntranceArray[0]

                finder = "Finder"
                receiver = "Receiver"
                item = "Item"
                location = "Location"
                game = "Game"
                entrance = "Entrance"

                # Preps check message
                checkmessage = (
                    "```"
                    + finder.ljust(FinderWidth)
                    + " || "
                    + receiver.ljust(ReceiverWidth)
                    + " || "
                    + item.ljust(ItemWidth)
                    + " || "
                    + location.ljust(LocationWidth)
                    + " || "
                    + game.ljust(GameWidth)
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

                    if reglines.strip() == finder:
                        checkmessage = (
                            checkmessage
                            + finder.ljust(FinderWidth)
                            + " || "
                            + receiver.ljust(ReceiverWidth)
                            + " || "
                            + item.ljust(ItemWidth)
                            + " || "
                            + location.ljust(LocationWidth)
                            + " || "
                            + game.ljust(GameWidth)
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
        print(e)
        bot.dispatch(DebugMessageEvent(
            content="ERROR IN HINTLIST <@" + DiscordAlertUserID + ">"
        ))


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
