#Bridgeipelago v0.x
#A project made with love from the Zajcats

from discord.ext import tasks
import discord
import http.client
import time
import os
import glob
from dotenv import load_dotenv
import numpy as np
import random
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

#.env Config Setup + Metadata
load_dotenv()
DiscordToken = os.getenv('DiscordToken')
ArchHost = os.getenv('ArchipelagoServer')
ArchPort = os.getenv('ArchipelagoPort')
ArchipelagoLogFiles = os.getcwd() + os.getenv('ArchipelagoClientLogs')
OutputFileLocation = os.getcwd() + os.getenv('BotLoggingFile')
DeathFileLocation = os.getcwd() + os.getenv('DeathLoggingFile')
RegistrationDirectory = os.getcwd() + os.getenv('PlayerRegistrationDirectory')
ItemQueueDirectory = os.getcwd() + os.getenv('PlayerItemQueueDirectory')
JoinMessage = os.getenv('JoinMessage')

# Metadata
ArchInfo = ArchHost + ':' + ArchPort
ArchipelagoLogFiles = ArchipelagoLogFiles + "*.txt"

# Global Variable Declaration

# Archipleago Log File Assocication
list_of_files = glob.glob(ArchipelagoLogFiles)
latest_file = max(list_of_files, key=os.path.getmtime)

# Discord Bot Initialization
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(JoinMessage," - ", client.user)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # Connects the bot to the specified channel, then locks that channel in as the main communication method
    if message.content.startswith('$connect'):
        await message.channel.send('Channel connected. Carry on commander.')
        global ChannelLock
        ChannelLock = message.channel
        await SetupFileRead() 
    
    # Disconnects the bot, and stops the scheduled tasks.
    if message.content.startswith('$disconnect'):
        await message.channel.send('Channel disconnected. Battle control - Offline.')
        background_task.cancel()
        reassurance.cancel()

    # Ping! Pong!
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    # Provides debug paths
    if message.content.startswith('$ArchInfo'):
        await message.channel.send(ArchInfo)
        await message.channel.send(latest_file)
        await message.channel.send(OutputFileLocation)
        await message.channel.send(RegistrationDirectory)
        await message.channel.send(ItemQueueDirectory)

    # Provides debug log
    if message.content.startswith('$LogPlease'):
        info = open(latest_file,"r")
        MessageContents = info.seek(0, os.SEEK_END)
        await message.channel.send(MessageContents)  

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
        print(line) #Used to debug registration commands
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

    # Sometimes we all need to hear it :)
    if message.content.startswith('$ILoveYou'):
        await message.channel.send("Thank you.  You make a diffrence in this world. :)")

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

# Sets up the pointer for the logfile, then starts background processes.
async def SetupFileRead():
    with open(latest_file, 'r') as fp:
        global EndOfFile
        EndOfFile = len(fp.readlines())
        print('Total Number of lines:', EndOfFile)  
    background_task.start()
    reassurance.start()

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
    global EndOfFile
    with open(latest_file,"r") as f:
        for _ in range(EndOfFile):
           next(f)
        for line in f:

            # For item checks, the log file will output a "FileLog" string that is parced for content (Thanks P2Ready)
            if "FileLog" in line:
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
                    SendItemToQueue(name,item,sender,check)
                    
                if "found their" in entry:
                    await ChannelLock.send("```"+entry+"```")

                o = open(OutputFileLocation, "a")
                o.write(entry)
                o.close()

            # Deathlink messages are gathered and stored in the deathlog for shame purposes.
            if "DeathLink:" in line:
                entry = line.split("]: ")[1]
                await ChannelLock.send("**"+ entry + "**")
                o = open(DeathFileLocation, "a")
                o.write(entry)
                o.close()

    # Now we scan to the end of the file and store it so we know how far we've read thus far
    with open(latest_file, 'r') as fp:
        EndOfFile = len(fp.readlines())


# When the user asks, catch them up on checks they're registered for
## Yoinks their registration file, scans through it, then find the related ItemQueue file to scan through 
async def KetchupUser(DMauthor):
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
                await DMauthor.dm_channel.send("There are no items for you : /")
                continue
            k = open(ItemQueueFile, "r")
            ItemQueueLines = k.readlines()
            k.close()
            os.remove(ItemQueueFile)
            for line in ItemQueueLines:
                await DMauthor.dm_channel.send("`" + line + "`")

# Sends the received item check to the ItemQueue for the slot in question.
def SendItemToQueue(Recipient, Item, Sender, Check):
    ItemQueueFile = ItemQueueDirectory + Recipient + ".csv"
    i = open(ItemQueueFile, "a")
    ItemWrite = Recipient + "||" + Item + "||" + Sender + "||" + Check +"\n"
    i.write(ItemWrite)
    i.close()

# Counts the number of deaths written to the deathlog and outputs it in bulk to the connected discord channel
async def CountDeaths():
    d = open(DeathFileLocation,"r")
    DeathLines = d.readlines()
    d.close()
    deathdict = {}
    for deathline in DeathLines:
        DeathUser = deathline.split("||")[5]
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
    plt.savefig('DeathPlot.png', bbox_inches="tight")
    await ChannelLock.send(file=discord.File('DeathPlot.png'))

client.run(DiscordToken)





