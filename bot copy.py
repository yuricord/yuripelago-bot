#Bridgeipelago v0.x
#A project made with love from the Zajcats

#Core Dependencies
from discord.ext import tasks
import discord
import http.client

import time


from dotenv import load_dotenv
import numpy as np
import random
import json

#Scrape Dependencies
import requests
from bs4 import BeautifulSoup

#Graphing Dependencies
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

#.env Config Setup + Metadata
load_dotenv()
DiscordToken = os.getenv('DiscordToken')
DiscordBroadcastChannel = int(os.getenv('DiscordBroadcastChannel'))
DiscordAlertUserID = os.getenv('DiscordAlertUserID')
ArchHost = os.getenv('ArchipelagoServer')
ArchPort = os.getenv('ArchipelagoPort')
ArchLogFiles = os.getcwd() + os.getenv('ArchipelagoClientLogs')
ArchTrackerURL = os.getenv('ArchipelagoTrackerURL')
ArchServerURL = os.getenv('ArchipelagoServerURL')
LoggingDirectory = os.getcwd() + os.getenv('LoggingDirectory')
RegistrationDirectory = os.getcwd() + os.getenv('PlayerRegistrationDirectory')
ItemQueueDirectory = os.getcwd() + os.getenv('PlayerItemQueueDirectory')
JoinMessage = os.getenv('JoinMessage')
DebugMode = os.getenv('DebugMode')
DiscordDebugChannel = int(os.getenv('DiscordDebugChannel'))
AutomaticSetup = os.getenv('AutomaticSetup')

# Metadata
ArchInfo = ArchHost + ':' + ArchPort
OutputFileLocation = LoggingDirectory + 'BotLog.txt'
DeathFileLocation = LoggingDirectory + 'DeathLog.txt'
DeathTimecodeLocation = LoggingDirectory + 'DeathTimecode.txt'
DeathPlotLocation = LoggingDirectory + 'DeathPlot.png'
CheckPlotLocation = LoggingDirectory + 'CheckPlot.png'


# Global Variable Declaration
ActivePlayers = []

## Active Player Population
page = requests.get(ArchTrackerURL)
soup = BeautifulSoup(page.content, "html.parser")
tables = soup.find("table",id="checks-table")
for slots in tables.find_all('tbody'):
    rows = slots.find_all('tr')
for row in rows:
    ActivePlayers.append((row.find_all('td')[1].text).strip())

# Archipleago Log File Assocication
ArchLogFiles = ArchLogFiles + "*.txt"
list_of_files = glob.glob(ArchLogFiles)
latest_file = max(list_of_files, key=os.path.getmtime)

# Discord Bot Initialization
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

#Logfile Initialization. We need to make sure the log files exist before we start writing to them.
l = open(DeathFileLocation, "a")
l.close()

l = open(OutputFileLocation, "a")
l.close()

l = open(DeathTimecodeLocation, "a")
l.close()




@client.event
async def on_message(message):
    try:
        if message.author == client.user:
            return
        
        #Universal special character replacment.
        message.content = message.content.replace("’","'")

        DebugMode = os.getenv('DebugMode')
        if(DebugMode == "true"):
            print(message.content, " - ", message.author, " - ", message.channel)

        #=== CORE COMMANDS ===#
        # Starts background processes
        if message.content.startswith('$connect'):
            await SetupFileRead()

        # Stops background processes
        if message.content.startswith('$disconnect'):
            await message.channel.send('Channel disconnected. Battle control - Offline.')
            background_task.cancel()
            reassurance.cancel()

        #=== PLAYER COMMANDS ===#


        # Runs the deathcounter message process
        if message.content.startswith('$deathcount'):
            await CountDeaths()

        if message.content.startswith('$checkcount'):
            await CheckCount()

        if message.content.startswith('$checkgraph'):
            await CheckGraph()

        #=== SPECIAL COMMANDS ===#
        # Sometimes we all need to hear it :)
        if message.content.startswith('$ILoveYou'):
            await message.channel.send("Thank you.  You make a difference in this world. :)")

        # Ping! Pong!
        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

        # Provides debug paths
        if message.content.startswith('$ArchInfo'):
            DebugMode = os.getenv('DebugMode')
            if(DebugMode == "true"):
                print(DiscordBroadcastChannel)
                print(DiscordAlertUserID)
                print(ArchInfo)
                print(ArchTrackerURL)
                print(ArchServerURL)
                print(ArchLogFiles)
                print(latest_file)
                print(OutputFileLocation)
                print(DeathFileLocation)
                print(DeathTimecodeLocation)
                print(RegistrationDirectory)
                print(ItemQueueDirectory)
                print(JoinMessage)
                print(DiscordDebugChannel)
                print(AutomaticSetup)
                print(DebugMode)
                print(ChannelLock)
                print(DebugLock)
            else:
                await message.channel.send("Debug Mode is disabled.")

    except:
        await DebugLock.send('ERROR IN CORE_MESSAGE_READ')






# Main background loop
## Scans the log file every two seconds and processes recceived item checks
@tasks.loop(seconds=2)
async def background_task():
    try:
        global EndOfFile
        with open(latest_file,"r") as f:
            for _ in range(EndOfFile):
               next(f)
            for line in f:

                #If the line doesn't begin with a [ then skip it! It's just a trace or something we don't need/care about
                if not line[0] == "[":
                    continue

                #Gathers The timestamp for logging
                timecodecore = line.split("]: ")[0]
                timecodecore = timecodecore.split("at ")[1]
                #Breaks time away from date
                timecodedate = timecodecore.split(" ")[0]
                timecodetime = timecodecore.split(" ")[1]

                #Breaks apart datestamp
                timecode_year = timecodedate.split("-")[0]
                timecode_month = timecodedate.split("-")[1]
                timecode_day = timecodedate.split("-")[2]

                #Breaks apart timestamp
                timecodetime = timecodetime.split(",")[0]
                timecode_hours = timecodetime.split(":")[0]
                timecode_min = timecodetime.split(":")[1]
                timecode_sec = timecodetime.split(":")[2]

                #Buids the timecode
                timecode = timecode_day +"||"+ timecode_month +"||"+ timecode_year +"||"+ timecode_hours +"||"+ timecode_min +"||"+ timecode_sec

                # For item checks, the log file will output a "FileLog" string that is parced for content (Thanks P2Ready)
                if "FileLog" in line:

                    #Splits the check from the Timecode string
                    entry = line.split("]: ")[1]
                    print(entry)

                    #Let's massage that there string
                    ### This already needs a rework, but it works if strings behave nicely ###
                    if "sent" in entry:
                        sender = entry.split(" sent ")[0]
                        entry = entry.split(" sent ")[1] # issue if sender name has "sent" substring
                        check_temp = entry.split(" (")[-1] # issue if check name has " ("
                        check = check_temp.split(")")[0]
                        name_temp = entry.split(" to ")[-1] # issue if check has word "to"
                        name = name_temp.split(" (")[0]
                        item = entry.split(" to ")[0]
                        await ChannelLock.send(
                            "```Recipient: " + name +
                            "\nItem: " + item +
                            "\nSender: " + sender +
                            "\nCheck: " + check + "```"
                            )
                        #Sends sent item to the item queue
                        await SendItemToQueue(name,item,sender,check)

                        #Sends ItemCheck to log
                        ItemCheck = name  +"||"+ sender +"||"+ item +"||"+ check
                        LogOutput = timecode +"||"+ ItemCheck +"\n"
                        o = open(OutputFileLocation, "a")
                        o.write(LogOutput)
                        o.close()

                    if "found their" in entry:
                        await ChannelLock.send("```"+entry+"```")
                        #Sends self-check to log
                        LogOutput = timecode +"||"+ entry
                        o = open(OutputFileLocation, "a")
                        o.write(LogOutput)
                        o.close()


                # Deathlink messages are gathered and stored in the deathlog for shame purposes.
                if "DeathLink:" in line:
                    d = open(DeathTimecodeLocation, "r")
                    DLtimecode = d.read()
                    d.close()

                    if DLtimecode == timecode:
                        print("skipping death!")
                        await DebugLock.send('skipping double death!')
                    else:
                        deathentry = line.split("]: ")[1]
                        await ChannelLock.send("**"+ deathentry + "**")

                        for slot in ActivePlayers:
                            if slot in deathentry:
                                deathentry = slot + "\n"

                        #temp Deathlog for Terraria
                        if "Mami Papi don't fite" in line or "Scycral Arch2" in line or "Muscle Mommy" in line or "Mami Papi" in line:
                            deathentry = "from IRL Fishing\n"

                        #write deathlink to log
                        DeathLogOutput = timecode +"||"+ deathentry
                        o = open(DeathFileLocation, "a")
                        o.write(DeathLogOutput)
                        o.close()

                        d = open(DeathTimecodeLocation, "w")
                        d.write(timecode)
                        d.close()

        # Now we scan to the end of the file and store it so we know how far we've read thus far
        with open(latest_file, 'r') as fp:
            EndOfFile = len(fp.readlines())
    except Exception as e:
        dbmessage = "```ERROR IN BACKGROUND_TASK\n" + str(e) + "```"
        await DebugLock.send(dbmessage)






# Sends the received item check to the ItemQueue for the slot in question.
async def SendItemToQueue(Recipient, Item, Sender, Check):
    try:
        ItemQueueFile = ItemQueueDirectory + Recipient + ".csv"
        i = open(ItemQueueFile, "a")
        ItemWrite = Recipient + "||" + Item + "||" + Sender + "||" + Check +"\n"
        i.write(ItemWrite)
        i.close()
    except:
        await DebugLock.send('ERROR IN SENDITEMTOQUEUE')

# Counts the number of deaths written to the deathlog and outputs it in bulk to the connected discord channel






client.run(DiscordToken)





