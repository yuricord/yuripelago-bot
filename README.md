# bridgeipelago

Discord bridge for Archipelago in python

## Preparing the Archipelago game

When generating the Archipelago game, make sure the bridgeipelago.yaml is included in the game to ensure the bot has a lot to listen in on.

If you'd like to add-in this bot to an existing game (or not have a dedicated slot for the bot) change ArchipelagoBotSlot in the .env to a valid slot-name.

## Bot Setup

Copy .env.template to .env

Fill out the .env for your use. The Discord and Archipelago sections are required to be filled out.

You're free to leave the Advanced Config section as-is unless you know what you're doing.

Install the bot dependencies listed below.

You'll need a discord bot API token for the bot. You can find setup for a token here: https://discordpy.readthedocs.io/en/stable/discord.html


## Running the Bot

Open up your terminal and run:

`python3 bridgeipelago.py`

You'll see the bot connect in your Discord channel and join the Archipelago game.

## Configs
|Key|Description|
|---|---|
|**Discord Config**||
|DiscordToken|Your Discord Bot's token|
|DiscordBroadcastChannel|Discord Channel ID for live-check purposes|
|DiscordAlertUserID|Discord User/Group ID for yelling about issues%|
|DiscordDebugChannel|Discord channel ID for debug purposes|
|**Archipelago Config**||
|ArchipelagoServer|The URL of the Archipelago server you'd like to connect to|
|ArchipelagoPort|The port of the Archipelago server you'd like to connect to|
|ArchipelagoBotSlot|The name of the slot you'd like the bot to use when connecting to archipelago|
|ArchipelagoTrackerURL|URL of the tracker you'd like to query|
|ArchipelagoServerURL|URL of the server you'd like to query|
|**Advanced Config**||
|LoggingDirectory|Directory of the bot's own logs*|
|PlayerRegistrationDirectory|Directory of the Player Registration Mappings*|
|PlayerItemQueueDirectory|Directory that stores player item queues*|
|ArchipelagoDataDirectory|Directory for the Archipelago data packages*|
|JoinMessage|A custom join message (console only) for the bot|
|AutomaticSetup|Automaticly starts background processes when bot is turned on|
|DebugMode|Enables extra debug chat/bot options^|

**\[%] For group IDs, ensure the '&' character is at the beggining of the ID** 

**\[*] Ensure directories end in a /**

**\[*] These should be four diffrent directories, all these logs in the same place will break the bot.**

**\[^] DebugMode can expose unintended system information. Use with care.**

## Core Dependencies

**TODO: redo this or make it automatic, dependenceies outside of a python-vir are a nightmare**

sudo apt install python3-pip

### Bot dependencies

python3 -m pip install -U discord.py

pip install python-dotenv

pip install numpy

python3 -m pip install beautifulsoup4

python3 -m pip install matplotlib

## Commands

|Core Commands|Description|
|---|---|
|$connect|Manually starts background processes*|
|$disconnect|Manually stops background processes|

**\[*] This should only be used when AutomaticSetup is set to 'false'**

|Player Commands|Description|
|---|---|
|$register \<slot>|Adds the slot provided to the user's registration file
|$clearreg|Clears the user's registration file|
|$ketchmeup|DMs the user all checks in their ItemQueue file, used to catch you up on missed checks|
|$groupcheck \<slot>|DMs the user all checks in the slot's ItemQueue file, used to catch up on group games
|$hints|DMs the hinted items for a player's registered slots|
|$deathcount|Scans the deathlog and tallies up the current deathcount for each slot|
|$checkcount|Fetches the current Arch server's progress in simple txt format|
|$checkgraph|Plots the current Arch progress in a picture|

|Debug Commands|Description|
|---|---|
|$iloveyou|We all need to hear this sometimes.|
|$hello|The bot says hello!|
|$ArchInfo|\[CONSOLE] General bot details for debugging .env tables^|

**\[^] DebugMode only commands**

**\[^] DebugMode can expose unintended system information. Use with care.**


  
