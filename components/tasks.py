import json
import time

import arc
import hikari
import requests

from bot_vars import (
    ArchPort,
    ArchServerURL,
    DeathFileLocation,
    DiscordAlertUserID,
    ItemQueueDirectory,
    OutputFileLocation,
    SpoilTraps,
    chat_queue,
    death_queue,
    item_queue,
)
from events import DebugMessageEvent, MainChannelMessageEvent
from utils import cancel_process, lookup_game, lookup_item, lookup_location, lookup_slot

plugin = arc.GatewayPlugin("tasks")


@arc.utils.interval_loop(seconds=900)
async def archi_host_checker(bot: hikari.GatewayBot = arc.inject()):
    try:
        ArchRoomID = ArchServerURL.split("/")
        ArchAPIUEL = ArchServerURL.split("/room/")
        RoomAPI = ArchAPIUEL[0] + "/api/room_status/" + ArchRoomID[4]
        RoomPage = requests.get(RoomAPI)
        RoomData = json.loads(RoomPage.content)

        cond = str(RoomData["last_port"])
        if cond == ArchPort:
            return
        else:
            print("Port Check Failed")
            print(RoomData["last_port"])
            print(ArchPort)
            message = (
                f"Port Check Failed - Restart tracker process <@{DiscordAlertUserID}>"
            )
            bot.dispatch(DebugMessageEvent(content=message))
    except:
        bot.dispatch(
            DebugMessageEvent(
                content="ERROR IN CHECKARCHHOST <@" + DiscordAlertUserID + ">"
            )
        )


@arc.utils.interval_loop(seconds=1)
async def item_queue_processor(bot: hikari.GatewayBot = arc.inject()):
    try:
        if item_queue.empty():
            return
        else:
            timecode = time.strftime("%Y||%m||%d||%H||%M||%S")
            item_message = item_queue.get()

            # if message has "found their" it's a self check, output and dont log
            query = item_message["data"][1]["text"]
            if query == " found their ":
                sending_game = str(lookup_game(item_message["data"][0]["text"]))
                sending_player = str(lookup_slot(item_message["data"][0]["text"]))
                sent_item = str(
                    lookup_item(sending_game, item_message["data"][2]["text"])
                )
                item_class = str(item_message["data"][2]["flags"])
                location = str(
                    lookup_location(sending_game, item_message["data"][4]["text"])
                )

                message = f"""
                    ```
                    {sending_player} found their {sent_item}
                    Check: {location}
                    ```
                """
                item_check_log_message = (
                    f"{sending_player}||{sent_item}||{sending_player}||{location}\n"
                )
                bot_log_message = f"{timecode}||{item_check_log_message}"
                o = open(OutputFileLocation, "a")
                o.write(bot_log_message)
                o.close()

            elif query == " sent ":
                sending_player = str(lookup_slot(item_message["data"][0]["text"]))
                sending_game = str(lookup_game(item_message["data"][0]["text"]))
                recieving_game = str(lookup_game(item_message["data"][4]["text"]))
                sent_item = str(
                    lookup_item(recieving_game, item_message["data"][2]["text"])
                )
                item_class = str(item_message["data"][2]["flags"])
                recieving_player = str(lookup_slot(item_message["data"][4]["text"]))
                location = str(
                    lookup_location(sending_game, item_message["data"][6]["text"])
                )

                message = f"""
                    ```
                    {sending_player} sent {sent_item} to {recieving_player}
                    Check: {location}
                    ```
                """
                item_check_log_message = (
                    f"{recieving_player}||{sent_item}||{sending_player}||{location}\n"
                )
                bot_log_message = f"{timecode}||{item_check_log_message}"
                o = open(OutputFileLocation, "a")
                o.write(bot_log_message)
                o.close()

                if int(item_class) == 4 and SpoilTraps == "true":
                    ItemQueueFile = ItemQueueDirectory + recieving_player + ".csv"
                    i = open(ItemQueueFile, "a")
                    i.write(item_check_log_message)
                    i.close()
                elif int(item_class) != 4:
                    ItemQueueFile = ItemQueueDirectory + recieving_player + ".csv"
                    i = open(ItemQueueFile, "a")
                    i.write(item_check_log_message)
                    i.close()
            else:
                message = "Unknown Item Send :("
                print(message)
                bot.dispatch(DebugMessageEvent(content=message))

            if int(item_class) == 4 and SpoilTraps == "true":
                bot.dispatch(MainChannelMessageEvent(content=message))
            elif int(item_class) != 4 and ItemFilter(int(item_class)):
                bot.dispatch(MainChannelMessageEvent(content=message))
            else:
                # In Theory, this should only be called when the two above conditions are not met
                # So we call this dummy function to escape the async call.
                await cancel_process()

    except Exception as e:
        print(e)
        await bot.dispatch(DebugMessageEvent(content="Error In Item Queue Processor"))


@arc.utils.interval_loop(seconds=1)
async def death_queue_processor(bot: hikari.GatewayBot = arc.inject()):
    if death_queue.empty():
        return
    else:
        chatmessage = death_queue.get()
        timecode = time.strftime("%Y||%m||%d||%H||%M||%S")
        DeathMessage = (
            "**Deathlink received from: " + chatmessage["data"]["source"] + "**"
        )
        DeathLogMessage = timecode + "||" + chatmessage["data"]["source"] + "\n"
        o = open(DeathFileLocation, "a")
        o.write(DeathLogMessage)
        o.close()
        bot.dispatch(MainChannelMessageEvent(content=DeathMessage))


@arc.utils.interval_loop(seconds=1)
async def chat_queue_processor(bot: hikari.GatewayBot = arc.inject()):
    if chat_queue.empty():
        return
    else:
        chatmessage = chat_queue.get()
        bot.dispatch(MainChannelMessageEvent(content=chatmessage["data"][0]["text"]))


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
    archi_host_checker.start()
    item_queue_processor.start()
    death_queue_processor.start()
    chat_queue_processor.start()


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    archi_host_checker.stop()
    item_queue_processor.stop()
    death_queue_processor.stop()
    chat_queue_processor.stop()
    client.remove_plugin(plugin)
