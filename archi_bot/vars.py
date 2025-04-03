import os
from queue import Queue

from dotenv import load_dotenv

load_dotenv()
DiscordToken: str = os.getenv("DiscordToken")
if not DiscordToken:
    print("Error: Please ensure discord token is provided.")
    exit(0)
DiscordBroadcastChannel = int(os.getenv("DiscordBroadcastChannel"))
DiscordAlertUserID = os.getenv("DiscordAlertUserID")
ArchHost = os.getenv("ArchipelagoServer")
ArchPort = os.getenv("ArchipelagoPort")
ArchipelagoBotSlot = os.getenv("ArchipelagoBotSlot")
ArchTrackerURL = os.getenv("ArchipelagoTrackerURL")
ArchServerURL = os.getenv("ArchipelagoServerURL")
SpoilTraps = os.getenv("BotItemSpoilTraps")
ItemFilterLevel = int(os.getenv("BotItemFilterLevel"))
LoggingDirectory = os.getcwd() + os.getenv("LoggingDirectory")
RegistrationDirectory = os.getcwd() + os.getenv("PlayerRegistrationDirectory")
ItemQueueDirectory = os.getcwd() + os.getenv("PlayerItemQueueDirectory")
ArchDataDirectory = os.getcwd() + os.getenv("ArchipelagoDataDirectory")
JoinMessage = os.getenv("JoinMessage")
DebugMode = bool(os.getenv("DebugMode"))
DiscordJoinOnly = os.getenv("DiscordJoinOnly")
DiscordDebugChannel = int(os.getenv("DiscordDebugChannel"))
AutomaticSetup = os.getenv("AutomaticSetup")

# Metadata
ArchInfo = ArchHost + ":" + ArchPort
OutputFileLocation = LoggingDirectory + "BotLog.txt"
DeathFileLocation = LoggingDirectory + "DeathLog.txt"
DeathTimecodeLocation = LoggingDirectory + "DeathTimecode.txt"
ArchDataDump = ArchDataDirectory + "ArchDataDump.json"
ArchGameDump = ArchDataDirectory + "ArchGameDump.json"
ArchConnectionDump = ArchDataDirectory + "ArchConnectionDump.json"
ArchRawData = ArchDataDirectory + "ArchRawData.txt"

# Global Variable Declaration
global ActivePlayers
ActivePlayers = []
global DumpJSON
DumpJSON = []
global ConnectionPackage
ConnectionPackage = []

# Queues
global item_queue
item_queue = Queue()
global death_queue
death_queue = Queue()
global chat_queue
chat_queue = Queue()
