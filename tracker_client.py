import sys
import typing
import uuid
from enum import Enum
from threading import Thread

from websocket import WebSocketApp, enableTrace

from utils import write_connection_package, write_data_package


class TrackerClient:
    tags: set[str] = {"Tracker", "DeathLink"}
    version: dict[str, int | str] = {
        "major": 0,
        "minor": 6,
        "build": 0,
        "class": "Version",
    }
    items_handling: int = 0b000  # This client does not receive any items

    class MessageCommand(Enum):
        BOUNCED = "Bounced"
        PRINT_JSON = "PrintJSON"
        ROOM_INFO = "RoomInfo"
        DATA_PACKAGE = "DataPackage"
        CONNECTED = "Connected"
        CONNECTIONREFUSED = "ConnectionRefused"

    def __init__(
        self,
        *,
        server_uri: str,
        port: str,
        slot_name: str,
        on_death_link: callable = None,
        on_item_send: callable = None,
        on_chat_send: callable = None,
        on_datapackage: callable = None,
        verbose_logging: bool = False,
        **kwargs: typing.Any,
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
        self.wsapp: WebSocketApp = None
        self.socket_thread: Thread = None

    def start(self) -> None:
        print(
            "Attempting to open an Archipelago MultiServer websocket connection in a new thread."
        )
        enableTrace(self.verbose_logging)
        self.wsapp = WebSocketApp(
            f"{self.server_uri}:{self.port}",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            **self.web_socket_app_kwargs,
        )

        self.socket_thread = Thread(target=self.wsapp.run_forever)
        self.socket_thread.daemon = True
        self.socket_thread.start()

    def on_error(self, string, opcode) -> None:
        if self.verbose_logging:
            print(f"error self: {self}")
            print(f"error string: {string}")
            print(f"error opcode: {opcode}")
        websocket_queue.put("Tracker Error...")
        sys.exit()

    def on_close(self, string, opcode, flag) -> None:
        if self.verbose_logging:
            print(f"closed self: {self}")
            print(f"closed string: {string}")
            print(
                f"closed opcode: {opcode}"
            )  # 1001 used for closure initiated by the server
            print(f"closed opcode: {flag}")
        websocket_queue.put("Tracker Closed...")
        sys.exit()

    def on_message(self, wsapp: WebSocketApp, message: str) -> None:
        """Handles incoming messages from the Archipelago MultiServer."""
        args: dict = json.loads(message)[0]
        cmd = args.get("cmd")

        if cmd == self.MessageCommand.ROOM_INFO.value:
            self.send_connect()
            self.get_datapackage()
        elif cmd == self.MessageCommand.DATA_PACKAGE.value:
            write_data_package(args)
        elif cmd == self.MessageCommand.CONNECTED.value:
            write_connection_package(args)
            print("Connected to server.")
        elif cmd == self.MessageCommand.CONNECTIONREFUSED.value:
            print(
                "Connection refused by server - check your slot name / port / whatever, and try again."
            )
            print(args)
            seppuku_queue.put(args)
            exit()
        elif (
            cmd == self.MessageCommand.PRINT_JSON.value
            and args.get("type") == "ItemSend"
        ):
            if self.on_item_send:
                self.on_item_send(args)
        elif cmd == self.MessageCommand.PRINT_JSON.value and args.get("type") == "Chat":
            if self.on_chat_send:
                self.on_chat_send(args)
        elif cmd == self.MessageCommand.BOUNCED.value and "DeathLink" in args.get(
            "tags", []
        ):
            if self.on_death_link:
                self.on_death_link(args)

    def send_connect(self) -> None:
        print("Sending `Connect` packet to log in to server.")
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
        self.send_message(payload)

    def get_datapackage(self) -> None:
        print("Sending `DataPackage` packet to request data.")
        payload = {"cmd": "GetDataPackage"}
        self.send_message(payload)

    def send_message(self, message: dict) -> None:
        self.wsapp.send(json.dumps([message]))

    def stop(self) -> None:
        self.wsapp.close()
