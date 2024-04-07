# bridgeipelago

Discord bridge for Archipelago in python

## Running

`python3 bot.py`

`python3 CommonClient.py --nogui --connect <server>:<port> --name <slot>`


## Configs
|Key|Description|
|---|---|
|DiscordToken|Your Discord Bot's token|
|ArchipleagoServer|The URL of the Archipleago server you'd like to connect to|
|ArchipleagoPort|The port of the Archipleago server you'd like to connect to|
|ArchipleagoClientLogs|Directory of the Archipeago CommonClient's logs*|
|BotLoggingFile|File location the bot will store it's own logs|
|PlayerRegistrationDirectory|Directory of the Player Registration Mappings|
|PlayerItemQueueDirectory|Directory that stores player item queues|


**\[*] Ensure directories end in a /**

## Core Dependencies

sudo apt install python3-pip

### Bot dependencies

python3 -m pip install -U discord.py
pip install python-dotenv

### CommonClient dependencies

Running CommonClient.py will gather all required modules needed for the Archipelago client to run.
  
