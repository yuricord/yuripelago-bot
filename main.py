# Core Dependencies
import json
import os
import time
from multiprocessing import Process

import arc

# Discord Dependencies
import hikari
import requests
from bs4 import BeautifulSoup

# Import variables
from bot_vars import (
    ActivePlayers,
    ArchConnectionDump,
    ArchDataDirectory,
    ArchGameDump,
    ArchHost,
    ArchipelagoBotSlot,
    ArchPort,
    ArchTrackerURL,
    DeathFileLocation,
    DeathTimecodeLocation,
    DiscordJoinOnly,
    DiscordToken,
    ItemQueueDirectory,
    LoggingDirectory,
    OutputFileLocation,
    RegistrationDirectory,
    chat_queue,
    death_queue,
    item_queue,
    seppuku_queue,
    websocket_queue,
)
from tracker_client import TrackerClient

if not DiscordToken:
    print("Error: Please provide a token in your config file!")
    exit(0)
if not ArchTrackerURL:
    print("Error: Please provide an archipelago tracker URL in your config file!")
    exit(0)

## Active Player Population
if DiscordJoinOnly == "false":
    page = requests.get(ArchTrackerURL)
    soup = BeautifulSoup(page.content, "html.parser")
    tables = soup.find("table", id="checks-table")
    for slots in tables.find_all("tbody"):
        rows = slots.find_all("tr")
    for row in rows:
        ActivePlayers.append((row.find_all("td")[1].text).strip())

# Discord Bot Initialization
bot = hikari.GatewayBot(DiscordToken)
client = arc.GatewayClient(bot)
client.load_extensions_from("components")
client.set_type_dependency(hikari.GatewayBot, bot)

# Make sure all of the directories exist before we start creating files
if not os.path.exists(ArchDataDirectory):
    os.makedirs(ArchDataDirectory)

if not os.path.exists(LoggingDirectory):
    os.makedirs(LoggingDirectory)

if not os.path.exists(RegistrationDirectory):
    os.makedirs(RegistrationDirectory)

if not os.path.exists(ItemQueueDirectory):
    os.makedirs(ItemQueueDirectory)

# Logfile Initialization. We need to make sure the log files exist before we start writing to them.
l = open(DeathFileLocation, "a")
l.close()

l = open(OutputFileLocation, "a")
l.close()

l = open(DeathTimecodeLocation, "a")
l.close()


## ARCHIPELAGO TRACKER CLIENT + CORE FUNCTION
def Discord():
    bot.run()


## Threaded async functions
if DiscordJoinOnly == "false":
    # Start the tracker client
    ap_client = TrackerClient(
        server_uri=ArchHost,
        port=ArchPort,
        slot_name=ArchipelagoBotSlot,
        verbose_logging=False,
        on_chat_send=lambda args: chat_queue.put(args),
        on_death_link=lambda args: death_queue.put(args),
        on_item_send=lambda args: item_queue.put(args),
    )
    ap_client.start()

    time.sleep(5)

    if seppuku_queue.empty():
        print("Loading Arch Data...")
    else:
        print("Seppuku Initiated - Goodbye Friend")
        exit(1)

    # Wait for game dump to be created by tracker client
    while not os.path.exists(ArchGameDump):
        print("waiting for ArchGameDump to be created on when data package is received")
        time.sleep(2)

    with open(ArchGameDump, "r") as f:
        DumpJSON = json.load(f)

    # Wait for connection dump to be created by tracker client
    while not os.path.exists(ArchConnectionDump):
        print("waiting for ArchConnectionDump to be created on room connection")
        time.sleep(2)

    with open(ArchConnectionDump, "r") as f:
        ConnectionPackage = json.load(f)

    time.sleep(3)

# The run method is blocking, so it will keep the program running
DiscordThread = Process(target=Discord)
DiscordThread.start()

## Gotta keep the bot running!
while True:
    if not websocket_queue.empty():
        while not websocket_queue.empty():
            SQMessage = websocket_queue.get()
            print(SQMessage)
        print("Restarting tracker client...")
        ap_client.start()
        time.sleep(10)

    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print("   Closing Bot Thread - Have a good day :)")
        exit(1)
