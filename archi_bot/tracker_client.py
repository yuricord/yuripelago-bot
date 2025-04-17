import asyncio
import json
import sys
import uuid
from collections.abc import Callable
from threading import Thread
from typing import Any

from orjson import loads
from pydantic import TypeAdapter
from sqlmodel import Session
from websockets.asyncio.client import ClientConnection, connect

from archi_bot.db import DB, RetrievedPacketQueue
from archi_bot.models.packets import (
    ArchiPacket,
    BouncedPacket,
    ConnectedPacket,
    ConnectionRefusedPacket,
    DataPackagePacket,
    PJChatPacket,
    PJItemSendPacket,
    PrintJSONPacketBase,
    RetrievedPacket,
    RoomInfoPacket,
)
from archi_bot.types import SlotType
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
        port: int,
        slot_name: str,
        on_death_link: Callable | None = None,
        on_item_send: Callable | None = None,
        on_chat_send: Callable | None = None,
        on_datapackage: Callable | None = None,
        on_retrieved: Callable | None = None,
        verbose_logging: bool = False,
        room_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.server_uri = server_uri
        self.port = port
        self.slot_name = slot_name
        self.on_death_link = on_death_link
        self.on_item_send = on_item_send
        self.on_chat_send = on_chat_send
        self.on_retrieved = on_retrieved
        self.on_datapackage = on_datapackage
        self.verbose_logging = verbose_logging
        self.web_socket_app_kwargs = kwargs
        self.uuid: int = uuid.getnode()
        self.connection: ClientConnection
        self.socket_thread: Thread
        self.packet_adapter: TypeAdapter = TypeAdapter(ArchiPacket)
        self.room_id: str | None = room_id

    async def start(self) -> None:
        print("Attempting to open an Archipelago websocket connection.")
        await asyncio.gather(self.run())
        print("Started AP Client")
        return

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
            print("Got Packet")
            packet: ArchiPacket = self.packet_adapter.validate_python(m)

            if isinstance(packet, RoomInfoPacket):
                if self.room_id:
                    write_room_info(RoomInfoPacket.model_validate(packet), self.room_id)
                else:
                    self.room_id = write_room_info(
                        RoomInfoPacket.model_validate(packet), None
                    )
                await self.send_connect()
                await self.get_datapackage()
                await asyncio.sleep(0)
            elif isinstance(packet, DataPackagePacket):
                write_data_package(DataPackagePacket.model_validate(packet))
                await asyncio.sleep(0)
            elif isinstance(packet, ConnectedPacket):
                # We know we will have the room_id by this point,
                # Because we would have to write the RoomInfo packet by now
                # Therefore, there should never be a case where `self.room_id == None`
                write_connection_package(
                    ConnectedPacket.model_validate(packet),
                    self.room_id,  # type:ignore
                )
                print("Connected to server.")
                await asyncio.sleep(0)
            elif isinstance(packet, ConnectionRefusedPacket):
                print(
                    "Connection refused by server - check your slot name / port / whatever, and try again."
                )
                print(packet)
                await self.connection.close()
                await asyncio.sleep(0)
            elif isinstance(packet, PrintJSONPacketBase):
                if isinstance(packet, PJItemSendPacket) and self.on_item_send:
                    await self.on_item_send(packet)
                elif isinstance(packet, PJChatPacket) and self.on_chat_send:
                    await self.on_chat_send(packet)
            elif isinstance(packet, BouncedPacket) and packet.tags:
                if "DeathLink" in packet.tags and self.on_death_link:
                    await self.on_death_link(packet)
            elif isinstance(packet, RetrievedPacket):
                await self.on_retrieved(packet)

            await asyncio.sleep(0)

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
            "slot_data": False,
        }
        await self.send_message(payload)

    async def get_datapackage(self) -> None:
        print("Fetching DataPackage..")
        payload = {"cmd": "GetDataPackage"}
        await self.send_message(payload)

    async def send_message(self, message: dict) -> None:
        await self.connection.send(json.dumps([message]))
        await asyncio.sleep(0)

    async def stop(self) -> None:
        await self.connection.close()
        await asyncio.sleep(0)

    async def on_chat_send(self, packet: PJChatPacket) -> None:
        chat_queue.put((self.room_id, packet))
        await asyncio.sleep(0)

    async def on_death_link(self, packet: BouncedPacket) -> None:
        death_queue.put((self.room_id, packet))
        await asyncio.sleep(0)

    async def on_item_send(self, packet: PJItemSendPacket) -> None:
        item_queue.put((self.room_id, packet))
        await asyncio.sleep(0)

    async def on_retrieved(self, packet: RetrievedPacket) -> None:
        packet_key = packet.keys.pop("botKey", None)
        with Session(DB) as sess:
            to_add = RetrievedPacketQueue(id=packet_key, data=packet.keys)
            sess.add(to_add)
            sess.commit()
        await asyncio.sleep(0)

    async def get_hints(self, slots: list[tuple[int, int]]) -> str:
        key = str(uuid.uuid4())
        set_payload = {
            "cmd": "Set",
            "key": "botKey",
            "operations": [{"operation": "replace", "value": key}],
        }
        await self.send_message(set_payload)
        payload = {
            "cmd": "Get",
            "keys": [f"_read_hints_{s[0]}_{s[1]}" for s in slots] + ["botKey"],
        }
        await self.send_message(payload)
        return key
