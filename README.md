# bridgeipelago

Discord bridge for Archipelago in python

## Running

`python3 bot.py`

`python3 CommonClient.py --nogui --connect <server>:<port> --name <slot>`


## Configs
|Key|Description|
|---|---|
|DiscordToken|Your Discord Bot's token|
|ArchipelagoServer|The URL of the Archipelago server you'd like to connect to|
|ArchipelagoPort|The port of the Archipelago server you'd like to connect to|
|ArchipelagoClientLogs|Directory of the Archipelago CommonClient's logs*|
|BotLoggingFile|File location the bot will store it's own logs|
|DeathLoggingFile|File location for the deathlink logs|
|PlayerRegistrationDirectory|Directory of the Player Registration Mappings*|
|PlayerItemQueueDirectory|Directory that stores player item queues*|
|JoinMessage|A custom join message (console only) for the bot|


**\[*] Ensure directories end in a /**

## Core Dependencies

sudo apt install python3-pip

### Bot dependencies

python3 -m pip install -U discord.py

pip install python-dotenv

pip install numpy

python3 -m pip install beautifulsoup4

python3 -m pip install matplotlib



### CommonClient dependencies

Running CommonClient.py will gather all required modules needed for the Archipelago client to run.

## Tools

Running /tools/check.sh will force an additon to the Archipelago log for debugging.

Edit as you see it.


## Commands

|Core Commands|Description|
|---|---|
|$connect|Connects the bot to the channel you run the command in, and starts background processes|
|$disconnect|Disconnects the bot from the channel, and stops background processes|

|Player Commands|Description|
|---|---|
|$register <slot>|Adds the slot provided to the user's registration file|
|$clearreg|Clears the user's registration file|
|$ketchmeup|DMs the user all checks in their ItemQueue file, used to catch you up on missed checks|
|$deathcount|Scans the deathlog and tallies up the current deathcount for each slot|

|Debug Commands|Description|
|---|---|
|$hello|The bot says hello!|
|$ILoveYou|We all need to hear this sometimes.|
|$LogPlease|Outputs Archipelago log length|
|$ArchInfo|General bot details for debugging .env tables|

  
