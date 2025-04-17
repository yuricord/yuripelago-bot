import json
import time
from typing import TYPE_CHECKING

import arc
import hikari
from aiofiles import open
from httpx import AsyncClient

from archi_bot.events import DebugMessageEvent, MainChannelMessageEvent
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
    ItemQueueDirectory,
    OutputFileLocation,
    SpoilTraps,
    chat_queue,
    death_queue,
    item_queue,
)

if TYPE_CHECKING:
    from archi_bot.models.packets import (
        BouncedPacket,
        PJItemSendPacket,
        PrintJSONPacketBase,
    )


plugin = arc.GatewayPlugin("tasks")


@arc.utils.interval_loop(minutes=15)
@plugin.inject_dependencies
async def archi_host_checker(bot: hikari.GatewayBot = arc.inject()):
    try:
        req_sess = AsyncClient()
        room_id = ArchServerURL.split("/")[4]
        api_url = ArchServerURL.split("/room/")
        room_api = api_url[0] + "/api/room_status/" + room_id
        room_page = await req_sess.get(room_api)
        room_data = json.loads(room_page.content)
        await req_sess.aclose()

        cond = str(room_data["last_port"])
        if cond == ArchPort:
            return
        message = f"""
                Port Check for room {room_id} failed,
                Please check its assigned port!
            """
        bot.dispatch(DebugMessageEvent(app=bot, content=message))
    except Exception as e:
        bot.dispatch(
            DebugMessageEvent(
                app=bot,
                content=f"""
                    Error with Archi Host Checker:
                    ```
                    {e}
                    ```
                """,
            )
        )


@arc.utils.interval_loop(seconds=1)
@plugin.inject_dependencies
async def item_queue_processor(bot: hikari.GatewayBot = arc.inject()):
    try:
        while not item_queue.empty():
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
                async with open(OutputFileLocation, "a") as o:
                    await o.write(bot_log_message)

            elif packet.item.player != packet.receiving:
                sending_game = get_archi_game_name(packet.item.player, room_id)
                sending_player = get_archi_slot_name(packet.item.player, room_id)
                receiving_game = get_archi_game_name(packet.receiving, room_id)
                sent_item = get_archi_item(receiving_game, packet.item.item, room_id)
                item_class = packet.item.flags
                receiving_player = get_archi_slot_name(packet.receiving, room_id)
                location = get_archi_location_name(
                    sending_game,
                    packet.item.location,
                    room_id,
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
                async with open(OutputFileLocation, "a") as o:
                    await o.write(bot_log_message)

                if item_class == 4 and SpoilTraps:
                    ItemQueueFile = ItemQueueDirectory + receiving_player + ".csv"
                    async with open(ItemQueueFile, "a") as i:
                        await i.write(item_check_log_message)
                elif item_class != 4:
                    ItemQueueFile = ItemQueueDirectory + receiving_player + ".csv"
                    async with open(ItemQueueFile, "a") as i:
                        await i.write(item_check_log_message)
            else:
                message = "Unknown Item Send :("
                print(message)
                bot.dispatch(DebugMessageEvent(app=bot, content=message))

            if item_class == 4 and SpoilTraps:
                bot.dispatch(MainChannelMessageEvent(app=bot, content=message))
            elif item_class != 4 and item_filter(item_class):
                bot.dispatch(MainChannelMessageEvent(app=bot, content=message))
            else:
                # In Theory, this should only be called when the two above conditions are not met
                pass

    except Exception as e:
        await bot.dispatch(
            DebugMessageEvent(
                app=bot,
                content=f"Error In Item Queue Processor ```{e}```",
            ),
        )


@arc.utils.interval_loop(seconds=1)
@plugin.inject_dependencies
async def death_queue_processor(bot: hikari.GatewayBot = arc.inject()):
    while not death_queue.empty():
        death = death_queue.get()
        chatmessage: BouncedPacket = death[1]
        timecode = time.strftime("%Y||%m||%d||%H||%M||%S")
        death_message = f"**Deathlink received from: {chatmessage.data['source']}**"
        death_log_message = f"{timecode}||{chatmessage.data['source']}\n"
        async with open(DeathFileLocation, "a") as o:
            await o.write(death_log_message)
        bot.dispatch(MainChannelMessageEvent(app=bot, content=death_message))


@arc.utils.interval_loop(seconds=1)
@plugin.inject_dependencies
async def chat_queue_processor(bot: hikari.GatewayBot = arc.inject()):
    while not chat_queue.empty():
        chat = chat_queue.get()
        chatmessage: PrintJSONPacketBase = chat[1]
        bot.dispatch(MainChannelMessageEvent(app=bot, content=chatmessage.data[0].text))


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)

    @client.add_startup_hook
    async def start_tasks(client: arc.GatewayClient) -> None:
        print("Starting Loops")
        item_queue_processor.start()
        death_queue_processor.start()
        chat_queue_processor.start()


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    item_queue_processor.stop()
    death_queue_processor.stop()
    chat_queue_processor.stop()
    client.remove_plugin(plugin)
