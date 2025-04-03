# Core Dependencies
import asyncio
import json
import os
import time

import arc

# Discord Dependencies
import hikari
import miru
import requests
from bs4 import BeautifulSoup
from sqlalchemy import Engine

from archi_bot.db import DB, create_db_and_tables
from archi_bot.tracker_client import TrackerClient

# Import variables
from archi_bot.vars import (
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
)

if not DiscordToken:
    print("Error: Please provide a token in your config file!")
    exit(0)
if not ArchTrackerURL:
    print("Error: Please provide an archipelago tracker URL in your config file!")
    exit(0)

# Enable UVLoop
if os.name != "nt":
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

## Active Player Population
if DiscordJoinOnly == "False":
    page = requests.get(ArchTrackerURL)
    soup = BeautifulSoup(page.content, "html.parser")
    tables = soup.find("table", id="checks-table")
    for slots in tables.find_all("tbody"):
        rows = slots.find_all("tr")
    for row in rows:
        ActivePlayers.append((row.find_all("td")[1].text).strip())

# Initialize Archi Client
ap_client = TrackerClient(
    server_uri=ArchHost,
    port=ArchPort,
    slot_name=ArchipelagoBotSlot,
    verbose_logging=False,
    on_chat_send=lambda args: chat_queue.put(args),
    on_death_link=lambda args: death_queue.put(args),
    on_item_send=lambda args: item_queue.put(args),
)
# Discord Bot Initialization
bot = hikari.GatewayBot(DiscordToken)
client = arc.GatewayClient(
    bot,
    invocation_contexts=[hikari.ApplicationContextType.GUILD],
    integration_types=[hikari.ApplicationIntegrationType.GUILD_INSTALL],
)
miru_client = miru.Client.from_arc(client)
client.set_type_dependency(hikari.GatewayBot, bot)
client.set_type_dependency(miru.Client, miru_client)
client.set_type_dependency(TrackerClient, ap_client)
client.set_type_dependency(Engine, DB)
print("Injected Dependencies")
client.load_extensions_from("archi_bot/components")

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
with open(DeathFileLocation, "a") as deathlog:
    deathlog.close()

with open(OutputFileLocation, "a") as outputfile:
    outputfile.close()

with open(DeathTimecodeLocation, "a") as deathtimecodes:
    deathtimecodes.close()


# Start the AP Client after the bot starts
@client.add_startup_hook
async def start_ap_client(ctx: arc.GatewayClient):
    client.create_task(ap_client.run())
    create_db_and_tables()
    if DiscordJoinOnly == "False":
        time.sleep(5)
        print("Loading Arch Data...")

        # Wait for game dump to be created by tracker client
        while not os.path.exists(ArchGameDump):
            print(
                "waiting for ArchGameDump to be created on when data package is received"
            )
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


bot.run()
