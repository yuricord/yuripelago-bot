import os
from pathlib import Path
from queue import Queue

from dotenv import load_dotenv

load_dotenv()
DiscordToken: str = os.getenv("DiscordToken")
if not DiscordToken:
    print("Error: Please ensure discord token is provided.")
    exit(0)
DiscordBroadcastChannel = int(os.getenv("DiscordBroadcastChannel"))
ArchHost = os.getenv("ArchipelagoServer")
ArchPort = os.getenv("ArchipelagoPort")
ArchipelagoBotSlot = os.getenv("ArchipelagoBotSlot")
ArchTrackerURL = os.getenv("ArchipelagoTrackerURL")
ArchServerURL = os.getenv("ArchipelagoServerURL")
SpoilTraps = bool(os.getenv("BotItemSpoilTraps"))
ItemFilterLevel = int(os.getenv("BotItemFilterLevel"))
LoggingDirectory = Path.cwd() / os.getenv("LoggingDirectory")
ItemQueueDirectory = Path.cwd() / os.getenv("PlayerItemQueueDirectory")
DebugMode = bool(os.getenv("DebugMode"))
DiscordDebugChannel = int(os.getenv("DiscordDebugChannel"))

# Metadata
OutputFileLocation = LoggingDirectory / "BotLog.txt"
DeathFileLocation = LoggingDirectory / "DeathLog.txt"

# Queues
global item_queue
item_queue = Queue()
global death_queue
death_queue = Queue()
global chat_queue
chat_queue = Queue()
