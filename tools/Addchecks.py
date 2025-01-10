import os
import glob
from dotenv import load_dotenv

rootpath = (os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")).split("/tools/.env")[0]
load_dotenv(dotenv_path=rootpath+"/.env")

ArchLogFiles = rootpath + os.getenv('ArchipelagoClientLogs')
LoggingDirectory = rootpath + os.getenv('LoggingDirectory')
RegistrationDirectory = rootpath + os.getenv('PlayerRegistrationDirectory')
ItemQueueDirectory = rootpath + os.getenv('PlayerItemQueueDirectory')

print(ArchLogFiles)
print(LoggingDirectory)
print(RegistrationDirectory)
print(ItemQueueDirectory)

ArchLogFiles = ArchLogFiles + "*.txt"
list_of_files = glob.glob(ArchLogFiles)
latest_file = max(list_of_files, key=os.path.getmtime)

print(latest_file)

ArchClientData = os.getcwd() + "/Refrence-Data/"

a = open(ArchClientData + "TestData_ArchClientData.Demo", "r")
acd = a.readlines()
a.close()

b = open(latest_file, "a")
for lines in acd:
    b.write(lines)
    print(lines)
b.close()

print("Done")

