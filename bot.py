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

#config = configparser.ConfigParser()
#config.read('.env')

#DiscordToken = config['Discord Config']['token']
#ArchPort = config['Archipleago Config']['port'] 
#ArchHost = config['Archipleago Config']['server'] 
#ArchipelagoLogFiles = config['Archipleago Config']['ArchipleagoClientLogs']
#OutputFileLocation = config['Bot Config']['BotLoggingFile']


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

    if message.content.startswith('$LogPlease'):
        info = open(latest_file,"r")
        MessageContents = info.seek(0, os.SEEK_END)
        await message.channel.send(MessageContents)  

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
    with open(latest_file, 'r') as fp:
        EndOfFile = len(fp.readlines())






client.run(DiscordToken)





