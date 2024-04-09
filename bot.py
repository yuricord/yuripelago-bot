#Bridgeipelago v0.x
#A project made with love from the Zajcats

from discord.ext import tasks
import discord
import http.client
import time
import os
import glob
from dotenv import load_dotenv

import configparser

#.env Config Setup + Metadata
load_dotenv()
DiscordToken = os.getenv('DiscordToken')
ArchPort = os.getenv('ArchipleagoServer')
ArchHost = os.getenv('ArchipleagoPort')
ArchipelagoLogFiles = os.getenv('ArchipleagoClientLogs')
OutputFileLocation = os.getenv('BotLoggingFile')

#.env + Subdirectory Locations

RegistrationDirectory = os.getcwd() + os.getenv('PlayerRegistrationDirectory')
ItemQueueDirectory = os.getcwd() + os.getenv('PlayerItemQueueDirectory')

ArchInfo = ArchHost + ':' + ArchPort
ArchipelagoLogFiles = ArchipelagoLogFiles + "*.txt"

#Global Variable Declaration
MasterCounter=0

#Archipleago Log File Assocication
list_of_files = glob.glob(ArchipelagoLogFiles)
latest_file = max(list_of_files, key=os.path.getmtime)

#Discord Bot Initialization
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'A new fighter has joined! - {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$connect'):
        await message.channel.send('Channel connected. Carry on commander.')
        global ChannelLock
        ChannelLock = message.channel
        await SetupFileRead() 
    
    if message.content.startswith('$disconnect'):
        await message.channel.send('Channel disconnected. Battle control - Offline.')
        background_task.cancel()

    
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$ArchInfo'):
        await message.channel.send(ArchInfo)
        await message.channel.send(latest_file)
        await message.channel.send(OutputFileLocation)
        await message.channel.send(RegistrationDirectory)
        await message.channel.send(ItemQueueDirectory)

    if message.content.startswith('$LogPlease'):
        info = open(latest_file,"r")
        MessageContents = info.seek(0, os.SEEK_END)
        await message.channel.send(MessageContents)  

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

    if message.content.startswith('$clearreg'):
        Sender = str(message.author)
        RegistrationFile = RegistrationDirectory + Sender + ".csv"
        os.remove(RegistrationFile)

    if message.content.startswith('$ILoveYou'):
        await message.channel.send("I know. :)")

    if message.content.startswith('$ketchmeup'):
        if (message.author).dm_channel == "None":
            print("No DM channel")
            print(message.author.dm_channel)
            await message.author.dm_channel.send("A NEW FIGHTER APPROCHING!!")
        else:
            await message.author.create_dm()
            await KetchupUser(message.author)


async def SetupFileRead():
    with open(latest_file, 'r') as fp:
        global EndOfFile
        EndOfFile = len(fp.readlines())
        print('Total Number of lines:', EndOfFile)  
    background_task.start()


@tasks.loop(seconds=2)
async def background_task():
    global EndOfFile
    global MasterCounter
    MasterCounter=MasterCounter+2
    print(MasterCounter)
    with open(latest_file,"r") as f:
        for _ in range(EndOfFile):
           next(f)
        for line in f:
            if "FileLog" in line:
                print(line.split("]: ",4)[1])
                await ChannelLock.send(line.split("]: ",4)[1])
                o = open(OutputFileLocation, "a")
                o.write(line.split("]: ",4)[1])
                o.close()
                ParseDataEntry()
    with open(latest_file, 'r') as fp:
        EndOfFile = len(fp.readlines())

async def KetchupUser(DMauthor):
    ItemQueueFile = ItemQueueDirectory + DMauthor + ".csv"
    k = open(ItemQueueFile, "r")
    ItemQueueLines = k.readlines()
    for line in ItemQueueLines:
        await DMauthor.dm_channel.send(line)

def ParseDataEntry():
    print("To Do :)")
    SendItemToQueue("Quasky_Test","Test_Item","Test_Sender","Test_Check")

def SendItemToQueue(Recipient, Item, Sender, Check):
    ItemQueueFile = ItemQueueDirectory + Recipient + ".csv"
    i = open(ItemQueueFile, "a")
    ItemWrite = Recipient + "||" + Item + "||" + Sender + "||" + Check
    i.write(ItemWrite)
    i.close()


client.run(DiscordToken)





