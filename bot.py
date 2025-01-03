#Bridgeipelago v0.x
#A project made with love from the Zajcats

#Core Dependencies
from discord.ext import tasks
import discord
import http.client
import time
import os
import glob
from dotenv import load_dotenv
import numpy as np
import random

#Scrape Dependencies
import requests
from bs4 import BeautifulSoup

#Graphing Dependencies
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator


#.env Config Setup + Metadata
load_dotenv()
DiscordToken = os.getenv('DiscordToken')
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

# Metadata
ArchInfo = ArchHost + ':' + ArchPort
OutputFileLocation = LoggingDirectory + 'BotLog.txt'
DeathFileLocation = LoggingDirectory + 'DeathLog.txt'
DeathTimecodeLocation = LoggingDirectory + 'DeathTimecode.txt'
DeathPlotLocation = LoggingDirectory + 'DeathPlot.png'


# Global Variable Declaration

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
async def on_ready():
    print(JoinMessage," - ", client.user)

@client.event
async def on_message(message):
    try:
        if message.author == client.user:
            return

        #=== CORE COMMANDS ===#
        # Connects the bot to the specified channel, then locks that channel in as the main communication method
        if message.content.startswith('$connect'):
            await message.channel.send('Channel connected. Carry on commander.')
            global ChannelLock
            ChannelLock = message.channel
            await SetupFileRead() 

        if message.content.startswith('$DEBUGlink'):
            await message.channel.send('Linked debug channel')
            global DebugLock
            DebugLock = message.channel

        # Disconnects the bot, and stops the scheduled tasks.
        if message.content.startswith('$disconnect'):
            await message.channel.send('Channel disconnected. Battle control - Offline.')
            background_task.cancel()
            reassurance.cancel()
            #KeepAlive.cancel()

        #=== PLAYER COMMANDS ===#
        # Registers user for a alot in Archipelago
        if message.content.startswith('$register'):
            ArchSlot = message.content
            ArchSlot = ArchSlot.replace("$register ","")
            Sender = str(message.author)
            RegistrationFile = RegistrationDirectory + Sender + ".csv"
            RegistrationContent = ArchSlot + "\n"

            # Generate the Registration File if it doesn't exist
            o = open(RegistrationFile, "a")
            o.close()

            # Get contents of the registration file and save it to 'line'
            o = open(RegistrationFile, "r")
            line = o.read()
            #print(line) #Used to debug registration commands
            o.close()

            # Check the registration file for ArchSlot, if they are not registered; do so. If they already are; tell them.
            if not ArchSlot in line:
                await message.channel.send("Registering " + Sender + " for slot " + ArchSlot)
                o = open(RegistrationFile, "a")
                o.write(RegistrationContent)
                o.close()
            else:
                await message.channel.send("You're already registered for that slot.")

        # Clears registration file for user
        if message.content.startswith('$clearreg'):
            Sender = str(message.author)
            RegistrationFile = RegistrationDirectory + Sender + ".csv"
            os.remove(RegistrationFile)

        # Opens a discord DM with the user, and fires off the Katchmeup process
        if message.content.startswith('$ketchmeup'):
            if (message.author).dm_channel == "None":
                print("No DM channel")
                print(message.author.dm_channel)
                await message.author.dm_channel.send("A NEW FIGHTER APPROCHING!!")
            else:
                await message.author.create_dm()
                await KetchupUser(message.author)

        # Runs the deathcounter message process
        if message.content.startswith('$deathcount'):
            await CountDeaths()

        if message.content.startswith('$checkcount'):
            await CheckCount()

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
                await message.channel.send(ArchInfo)
                await message.channel.send(ArchTrackerURL)
                await message.channel.send(ArchServerURL)
                await message.channel.send(ArchLogFiles)
                await message.channel.send(latest_file)
                await message.channel.send(OutputFileLocation)
                await message.channel.send(DeathFileLocation)
                await message.channel.send(DeathTimecodeLocation)
                await message.channel.send(RegistrationDirectory)
                await message.channel.send(ItemQueueDirectory)
                await message.channel.send(JoinMessage)
                await message.channel.send(DebugMode)
                await message.channel.send(DebugLock)
            else:
                await message.channel.send("Debug Mode is disabled.")

        # Provides debug log
        if message.content.startswith('$LogPlease'):
            DebugMode = os.getenv('DebugMode')
            if(DebugMode == "true"):
                info = open(latest_file,"r")
                MessageContents = info.seek(0, os.SEEK_END)
                await message.channel.send(MessageContents)  
            else:
                await message.channel.send("Debug Mode is disabled.")
        
        #Bees
        if message.content.startswith('$BEE'):
            DebugMode = os.getenv('DebugMode')
            if(DebugMode == "true"):
                await BEE()
    except:
        await DebugLock.send('ERROR IN CORE_MESSAGE_READ')

# Sets up the pointer for the logfile, then starts background processes.
async def SetupFileRead():
    try:
        with open(latest_file, 'r') as fp:
            global EndOfFile
            EndOfFile = len(fp.readlines())
            print('Total Number of lines:', EndOfFile)  
        background_task.start()
        reassurance.start()
        #KeepAlive.start()
    except:
        await DebugLock.send('ERROR IN SETUPFILEREAD')

@tasks.loop(seconds=5400)
async def KeepAlive():
    serverpage = requests.get(ArchServerURL)
    print("PING PONG Server")


# Because Quasky is paranoid, reassures you that the bot is running.
@tasks.loop(seconds=np.random.randint(60,300))
async def reassurance():
    quotes = [
    "I'm being a good boy over here!",
    "Don't worry dad, I'm still workin' away!",
    "I'M WORKING, GOSH",
    "The birds planted a bomb in the forest...",
    "I still hear the voices...they never leave.",
    "Yep, still working!",
    "God died in 1737, we've been on our own ever since.",
    "I've got this! Working away!",
    "*Bzzzt* WORKING *Bzzzt*"
    ]
    print(random.choice(quotes))


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

                        #temp Deathlog for Terraria
                        if "Mami Papi don't fite" in line or "Scycral Arch2" in line or "Muscle Mommy" in line or "Mami Papi" in line:
                            deathentry = "from IRL Fishing\n"

                        #write deathlink to log
                        deathentry = deathentry.split("from ")[1]
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
    except:
        await DebugLock.send('ERROR IN BG_TASK')

# When the user asks, catch them up on checks they're registered for
## Yoinks their registration file, scans through it, then find the related ItemQueue file to scan through 
async def KetchupUser(DMauthor):
    try:
        RegistrationFile = RegistrationDirectory + DMauthor.name + ".csv"
        if not os.path.isfile(RegistrationFile):
            await DMauthor.dm_channel.send("You've not registered for a slot : (")
        else:
            r = open(RegistrationFile,"r")
            RegistrationLines = r.readlines()
            r.close()
            for reglines in RegistrationLines:
                ItemQueueFile = ItemQueueDirectory + reglines.strip() + ".csv"
                if not os.path.isfile(ItemQueueFile):
                    await DMauthor.dm_channel.send("There are no items for " + reglines.strip() + " :/")
                    continue
                k = open(ItemQueueFile, "r")
                ItemQueueLines = k.readlines()
                k.close()
                os.remove(ItemQueueFile)

                ketchupmessage = "```You || Item || Sender || Location \n"
                for line in ItemQueueLines:
                    ketchupmessage = ketchupmessage + line
                    if len(ketchupmessage) > 1500:
                        ketchupmessage = ketchupmessage + "```"
                        await DMauthor.dm_channel.send(ketchupmessage)
                        ketchupmessage = "```"


                ketchupmessage = ketchupmessage + "```"
                await DMauthor.dm_channel.send(ketchupmessage)
    except:
        await DebugLock.send('ERROR IN KETCHMEUP')

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
async def CountDeaths():
    try:
        d = open(DeathFileLocation,"r")
        DeathLines = d.readlines()
        d.close()
        deathdict = {}
        for deathline in DeathLines:
            DeathUser = deathline.split("||")[6]
            DeathUser = DeathUser.split("\n")[0]

            if not DeathUser in deathdict:
                deathdict[DeathUser] = 1
            else:
                deathdict[DeathUser] = deathdict[DeathUser] + 1

        deathdict = {key: value for key, value in sorted(deathdict.items())}
        deathnames = []
        deathcounts = []
        message = "**Death Counter:**\n```"
        deathkeys = deathdict.keys()
        for key in deathkeys:
            deathnames.append(str(key))
            deathcounts.append(int(deathdict[key]))
            message = message + "\n" + str(key) + ": " + str(deathdict[key])
        message = message + '```'
        await ChannelLock.send(message)

        ### PLOTTING CODE ###
        with plt.xkcd():

            # Change length of plot long axis based on player count
            if len(deathnames) >= 20:
                long_axis=32
            elif len(deathnames) >= 5:
                long_axis=16
            else:
                long_axis=8

            # Initialize Plot
            fig = plt.figure(figsize=(long_axis,8))
            ax = fig.add_subplot(111)

            # Index the players in order
            player_index = np.arange(0,len(deathnames),1)

            # Plot count vs. player index
            plot = ax.bar(player_index,deathcounts,color='darkorange')

            # Change "index" label to corresponding player name
            ax.set_xticks(player_index)
            ax.set_xticklabels(deathnames,fontsize=20,rotation=-45,ha='left',rotation_mode="anchor")

            # Set y-axis limits to make sure the biggest bar has space for label above it
            ax.set_ylim(0,max(deathcounts)*1.1)

            # Set y-axis to have integer labels, since this is integer data
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.tick_params(axis='y', labelsize=20)

            # Add labels above bars
            ax.bar_label(plot,fontsize=20) 

            # Plot Title
            ax.set_title('Death Counts',fontsize=28)

        # Save image and send - any existing plot will be overwritten
        plt.savefig(DeathPlotLocation, bbox_inches="tight")
        await ChannelLock.send(file=discord.File(DeathPlotLocation))
    except:
        await DebugLock.send('ERROR DEATHCOUNT')
    
async def CheckCount():
    try:
        page = requests.get(ArchTrackerURL)
        soup = BeautifulSoup(page.content, "html.parser")

        #Yoinks table rows from the checks table
        tables = soup.find("table",id="checks-table")
        for slots in tables.find_all('tbody'):
            rows = slots.find_all('tr')

        #Preps check message
        checkmessage = "```Slot || Game || Status || Checks || % \n"

        #Moves through rows for data
        for row in rows:
            slot = (row.find_all('td')[1].text).strip()
            game = (row.find_all('td')[2].text).strip()
            status = (row.find_all('td')[3].text).strip()
            checks = (row.find_all('td')[4].text).strip()
            percent = (row.find_all('td')[5].text).strip()
            checkmessage = checkmessage + slot + " || " + game + " || " + status + " || " + checks + " || " + percent + "\n"

        #Finishes the check message
        checkmessage = checkmessage + "```"
        await ChannelLock.send(checkmessage)
    except:
        await DebugLock.send('ERROR IN CHECKCOUNT')


async def BEE():
    message = "```NARRATOR:(Black screen with text; The sound of buzzing bees can be heard)According to all known laws of aviation,:there is no way a beeshould be able to fly. :Its wings are too small to getits fat little body off the ground. :The bee, of course, flies anyway :because bees dont carewhat humans think is impossible.BARRY BENSON:(Barry is picking out a shirt)Yellow, black. Yellow, black.Yellow, black. Yellow, black. :Ooh, black and yellow!Lets shake it up a little.JANET BENSON:Barry! Breakfast is ready!BARRY:Coming! :Hang on a second.(Barry uses his antenna like a phone) :Hello?ADAM FLAYMAN:(Through phone)- Barry?BARRY:- Adam?ADAM:- Can you believe this is happening?BARRY:- I cant. Ill pick you up.(Barry flies down the stairs) :MARTIN BENSON:Looking sharp.JANET:Use the stairs. Your fatherpaid good money for those.BARRY:Sorry. Im excited.MARTIN:Heres the graduate.Were very proud of you, son. :A perfect report card, all Bs.JANET:Very proud.(Rubs Barrys hair)BARRY=Ma! I got a thing going here.JANET:- You got lint on your fuzz.BARRY:- Ow! Thats me!JANET:- Wave to us! Well be in row 118,000.- Bye!(Barry flies out the door)JANET:Barry, I told you,stop flying in the house!(Barry drives through the hive,and is waved at by Adam who is reading anewspaper)BARRY==- Hey, Adam.ADAM:- Hey, Barry.(Adam gets in Barrys car) :- Is that fuzz gel?BARRY:- A little. Special day, graduation.ADAM:Never thought Id make it.(Barry pulls away from the house and continues driving)BARRY:Three days grade school,three days high school...ADAM:Those were awkward.BARRY:Three days college. Im glad I tooka day and hitchhiked around the hive.ADAM==You did come back different.(Barry and Adam pass by Artie, who is jogging)ARTIE:- Hi, Barry!BARRY:- Artie, growing a mustache? Looks good.ADAM:- Hear about Frankie?BARRY:- Yeah.ADAM==- You going to the funeral?BARRY:- No, Im not going to his funeral. :Everybody knows,sting someone, you die. :Dont waste it on a squirrel.Such a hothead.1000000000000000000000000```"
    await ChannelLock.send(message)
    


client.run(DiscordToken)





