import asyncio
import json
import sys
import uuid
from collections.abc import Callable
from threading import Thread
from typing import Any, Optional

from orjson import loads
from pydantic import TypeAdapter
from websockets.asyncio.client import ClientConnection, connect

from archi_bot.models.packets import (
    ArchiPacket,
    BouncedPacket,
    ConnectedPacket,
    DataPackagePacket,
    PrintJSONPacketBase,
    RoomInfoPacket,
)
from archi_bot.types import MessageCommand, PrintJsonType, SlotType
from archi_bot.utils import (
    write_connection_package,
    write_data_package,
    write_room_info,
)
from archi_bot.vars import chat_queue, death_queue, item_queue


class TrackerClient:
    tags: set[str] = {"Tracker", "DeathLink"}
    version: dict[str, int | str] = {
        "major": 0,
        "minor": 6,
        "build": 0,
        "class": "Version",
    }
    items_handling: SlotType = (
        SlotType.spectator
    )  # This client does not receive any items

    def __init__(
        self,
        *,
        server_uri: str,
        port: str,
        slot_name: str,
        on_death_link: Callable | None = None,
        on_item_send: Callable | None = None,
        on_chat_send: Callable | None = None,
        on_datapackage: Callable | None = None,
        verbose_logging: bool = False,
        **kwargs: Any,
    ) -> None:
        self.server_uri = server_uri
        self.port = port
        self.slot_name = slot_name
        self.on_death_link = on_death_link
        self.on_item_send = on_item_send
        self.on_chat_send = on_chat_send
        self.on_datapackage = on_datapackage
        self.verbose_logging = verbose_logging
        self.web_socket_app_kwargs = kwargs
        self.uuid: int = uuid.getnode()
        self.connection: ClientConnection
        self.socket_thread: Thread
        self.packet_adapter: TypeAdapter = TypeAdapter(ArchiPacket)
        self.room_id: Optional[str] = None

    async def start(self) -> None:
        print(
            "Attempting to open an Archipelago MultiServer websocket connection in a new thread."
        )
        self.connection = await connect(
            uri=f"{self.server_uri}:{self.port}", user_agent_header="ArchiBot 1.0"
        )

        self.socket_thread = Thread(target=asyncio.run, args=(self.run(),))
        self.socket_thread.daemon = True
        self.socket_thread.start()
        print("Started AP Client")

    def on_error(self, string, opcode) -> None:
        if self.verbose_logging:
            print(f"""
                Tracker Error:
                --------------
                self: {self}
                string: {string}
                opcode: {opcode}
                """)
        sys.exit()

    def on_close(self, string, opcode, flag) -> None:
        if self.verbose_logging:
            print(f"""
                Tracker Closed:
                ---------------
                self: {self}
                string: {string}
                opcode: {opcode}
                flag: {flag}
                """)
        sys.exit()

    async def run(self) -> None:
        print("Attempting to open an Archipelago MultiServer websocket connection.")
        self.connection = await connect(
            uri=f"{self.server_uri}:{self.port}",
            user_agent_header="ArchiBot 1.0",
            max_size=None,
        )
        print("Started AP Client")
        async for message in self.connection:
            """Handles incoming messages from the Archipelago MultiServer."""
            m = loads(message)[0]
            packet: ArchiPacket = self.packet_adapter.validate_python(m)
            cmd = packet.cmd

            if cmd == MessageCommand.ROOM_INFO:
                self.room_id = write_room_info(RoomInfoPacket.model_validate(packet))
                await self.send_connect()
                await self.get_datapackage()
            elif cmd == MessageCommand.DATA_PACKAGE:
                write_data_package(DataPackagePacket.model_validate(packet))
            elif cmd == MessageCommand.CONNECTED:
                write_connection_package(
                    ConnectedPacket.model_validate(packet), self.room_id
                )
                print("Connected to server.")
            elif cmd == MessageCommand.CONNECTION_REFUSED:
                print(
                    "Connection refused by server - check your slot name / port / whatever, and try again."
                )
                print(packet)
                await self.connection.close()
                exit()
            elif isinstance(packet, PrintJSONPacketBase):
                if packet.type == PrintJsonType.ITEM_SEND and self.on_item_send:
                    self.on_item_send(packet)
                elif packet.type == PrintJsonType.CHAT and self.on_chat_send:
                    self.on_chat_send(packet)
            elif isinstance(packet, BouncedPacket) and packet.tags:
                if "DeathLink" in packet.tags and self.on_death_link:
                    self.on_death_link(packet)

    async def send_connect(self) -> None:
        print("Connecting to Archipelago server..")
        payload = {
            "cmd": "Connect",
            "game": "",
            "password": None,
            "name": self.slot_name,
            "version": self.version,
            "tags": list(self.tags),
            "items_handling": self.items_handling,
            "uuid": self.uuid,
        }
        await self.send_message(payload)

    async def get_datapackage(self) -> None:
        print("Fetching DataPackage..")
        payload = {"cmd": "GetDataPackage"}
        await self.send_message(payload)

    async def send_message(self, message: dict) -> None:
        await self.connection.send(json.dumps([message]))

    async def stop(self) -> None:
        await self.connection.close()

    async def on_chat_send(self, args) -> None:
        chat_queue.put((self.room_id, args))

    async def on_death_link(self, args) -> None:
        death_queue.put((self.room_id, args))

    async def on_item_send(self, args) -> None:
        item_queue.put((self.room_id, args))
