import json
import time

import arc
import hikari
import requests

from archi_bot.events import DebugMessageEvent, MainChannelMessageEvent
from archi_bot.models.packets import (
    BouncedPacket,
    PJItemSendPacket,
    PrintJSONPacketBase,
)
from archi_bot.utils import (
    get_archi_game_name,
    get_archi_item,
    get_archi_location_name,
    get_archi_slot_name,
    item_filter,
)
from archi_bot.vars import (
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

plugin = arc.GatewayPlugin("tasks")


@arc.utils.interval_loop(minutes=15)
@plugin.inject_dependencies
async def archi_host_checker(bot: hikari.GatewayBot = arc.inject()):
    try:
        ArchRoomID = ArchServerURL.split("/")
        ArchAPIURL = ArchServerURL.split("/room/")
        RoomAPI = ArchAPIURL[0] + "/api/room_status/" + ArchRoomID[4]
        RoomPage = requests.get(RoomAPI)
        RoomData = json.loads(RoomPage.content)

        cond = str(RoomData["last_port"])
        if cond == ArchPort:
            return
        else:
            message = (
                f"Port Check Failed - Restart tracker process <@{DiscordAlertUserID}>"
            )
            bot.dispatch(DebugMessageEvent(app=bot, content=message))
    except:
        bot.dispatch(
            DebugMessageEvent(
                app=bot, content=f"ERROR IN CHECKARCHHOST <@{DiscordAlertUserID}>"
            )
        )


@arc.utils.interval_loop(seconds=1)
@plugin.inject_dependencies
async def item_queue_processor(bot: hikari.GatewayBot = arc.inject()):
    try:
        if item_queue.empty():
            return
        else:
            timecode = time.strftime("%Y||%m||%d||%H||%M||%S")
            item = item_queue.get()
            packet: PJItemSendPacket = item[1]
            room_id = item[0]
            print(f"Got item: {packet}")

            # if message has "found their" it's a self check, output and don't log
            if packet.item.player == packet.receiving:
                sending_game = get_archi_game_name(packet.item.player, room_id)
                sending_player = get_archi_slot_name(packet.item.player, room_id)
                sent_item = get_archi_item(sending_game, packet.item.item, room_id)
                item_class = str(packet.item.flags)
                location = get_archi_location_name(
                    sending_game, packet.item.location, room_id
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

            elif packet.item.player != packet.receiving:
                sending_game = get_archi_game_name(packet.item.player, room_id)
                sending_player = get_archi_slot_name(packet.item.player, room_id)
                receiving_game = get_archi_game_name(packet.receiving, room_id)
                sent_item = get_archi_item(receiving_game, packet.item.item, room_id)
                item_class = packet.item.flags
                receiving_player = get_archi_slot_name(packet.receiving, room_id)
                location = get_archi_location_name(
                    sending_game, packet.item.location, room_id
                )

                message = f"""
                    ```
                    {sending_player} sent {sent_item} to {receiving_player}
                    Check: {location}
                    ```
                """
                item_check_log_message = (
                    f"{receiving_player}||{sent_item}||{sending_player}||{location}\n"
                )
                bot_log_message = f"{timecode}||{item_check_log_message}"
                o = open(OutputFileLocation, "a")
                o.write(bot_log_message)
                o.close()

                if int(item_class) == 4 and SpoilTraps == "true":
                    ItemQueueFile = ItemQueueDirectory + receiving_player + ".csv"
                    i = open(ItemQueueFile, "a")
                    i.write(item_check_log_message)
                    i.close()
                elif int(item_class) != 4:
                    ItemQueueFile = ItemQueueDirectory + receiving_player + ".csv"
                    i = open(ItemQueueFile, "a")
                    i.write(item_check_log_message)
                    i.close()
            else:
                message = "Unknown Item Send :("
                print(message)
                bot.dispatch(DebugMessageEvent(app=bot, content=message))

            if item_class == 4 and SpoilTraps == "true":
                bot.dispatch(MainChannelMessageEvent(app=bot, content=message))
            elif item_class != 4 and item_filter(item_class):
                bot.dispatch(MainChannelMessageEvent(app=bot, content=message))
            else:
                # In Theory, this should only be called when the two above conditions are not met
                pass

    except Exception as e:
        print(e)
        await bot.dispatch(
            DebugMessageEvent(app=bot, content="Error In Item Queue Processor")
        )


@arc.utils.interval_loop(seconds=1)
@plugin.inject_dependencies
async def death_queue_processor(bot: hikari.GatewayBot = arc.inject()):
    if death_queue.empty():
        return
    else:
        death = death_queue.get()
        chatmessage: BouncedPacket = death[1]
        timecode = time.strftime("%Y||%m||%d||%H||%M||%S")
        DeathMessage = f"**Deathlink received from: {chatmessage.data['source']}**"
        DeathLogMessage = f"{timecode}||{chatmessage.data['source']}\n"
        o = open(DeathFileLocation, "a")
        o.write(DeathLogMessage)
        o.close()
        bot.dispatch(MainChannelMessageEvent(app=bot, content=DeathMessage))


@arc.utils.interval_loop(seconds=1)
@plugin.inject_dependencies
async def chat_queue_processor(bot: hikari.GatewayBot = arc.inject()):
    if chat_queue.empty():
        return
    else:
        chat = chat_queue.get()
        chatmessage: PrintJSONPacketBase = chat[1]
        bot.dispatch(MainChannelMessageEvent(app=bot, content=chatmessage.data[0].text))


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)

    @client.add_startup_hook
    async def start_tasks(client: arc.GatewayClient) -> None:
        print("Starting Loops")
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
