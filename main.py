# Core Dependencies
import asyncio
import os
from pathlib import Path

import arc

# Discord Dependencies
import hikari
import miru
from sqlalchemy import Engine

from archi_bot.db import DB, create_db_and_tables

# Import variables
from archi_bot.vars import (
    ArchTrackerURL,
    DeathFileLocation,
    DiscordToken,
    ItemQueueDirectory,
    LoggingDirectory,
    OutputFileLocation,
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

# Initialize Archi Client
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
client.set_type_dependency(Engine, DB)
print("Injected Dependencies")
client.load_extensions_from("archi_bot/components")

# Make sure all of the directories exist before we start creating files
if not Path(LoggingDirectory).exists():
    Path(LoggingDirectory).mkdir(parents=True)

if not Path(ItemQueueDirectory).exists():
    Path(ItemQueueDirectory).mkdir(parents=True)

# Logfile Initialization. We need to make sure the log files exist before we start writing to them.
with Path(DeathFileLocation).open("a") as deathlog:
    deathlog.close()

with Path(OutputFileLocation).open("a") as outputfile:
    outputfile.close()


# Start the AP Client after the bot starts
@client.add_startup_hook
async def start_ap_client(ctx: arc.GatewayClient):
    create_db_and_tables()


bot.run()
