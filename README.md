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
|ArchipelagoTrackerURL|URL of the tracker you'd like to query|
|ArchipelagoServerURL|URL of the server you'd like to query|
|ArchipelagoClientLogs|Directory of the Archipelago CommonClient's logs*|
|BotLoggingFile|File location the bot will store it's own logs|
|DeathLoggingFile|File location for the deathlink logs|
|DeathTimecodeFile|File location for the deathlink timecode buffer|
|PlayerRegistrationDirectory|Directory of the Player Registration Mappings*|
|PlayerItemQueueDirectory|Directory that stores player item queues*|
|JoinMessage|A custom join message (console only) for the bot|
|DebugMode|Enables extra debug chat/bot options^|


**\[*] Ensure directories end in a /**

**\[^] DebugMode can expose unintended system information. Use with care.**

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
|$DEBUGlink|Connects a special debug channel that will report errors|
|$disconnect|Disconnects the bot from the channel, and stops background processes|

|Player Commands|Description|
|---|---|
|$register <slot>|Adds the slot provided to the user's registration file|
|$clearreg|Clears the user's registration file|
|$ketchmeup|DMs the user all checks in their ItemQueue file, used to catch you up on missed checks|
|$deathcount|Scans the deathlog and tallies up the current deathcount for each slot|
|$checkcount|Fetches the current Arch server's progress in simple txt format|

|Debug Commands|Description|
|---|---|
|$ILoveYou|We all need to hear this sometimes.|
|$hello|The bot says hello!|
|$ArchInfo|General bot details for debugging .env tables^|
|$LogPlease|Outputs Archipelago log length^|
|$BEE|Bzzzzzzzzzzzzzzzzzzzz^|

**\[^] DebugMode only commands**
**\[^] DebugMode can expose unintended system information. Use with care.**


  
