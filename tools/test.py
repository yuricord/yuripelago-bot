
import json

with open('games.json', 'r') as f:
    LoadedJSON = json.load(f)

with open('ConnectionPackage.json', 'r') as f:
    ConnectionPackage = json.load(f)

def itemcheck(game,id):
    for key in LoadedJSON[game]['item_name_to_id']:
        if LoadedJSON[game]['item_name_to_id'][key] == id:
            return key
        
def locationcheck(game,id):
    for key in LoadedJSON[game]['location_name_to_id']:
        if LoadedJSON[game]['location_name_to_id'][key] == id:
            return key

def slotname(slot):
    for key in ConnectionPackage['slot_info']:
        if key == slot:
            return ConnectionPackage['slot_info'][key]['name']

def slotgame(slot):
    for key in ConnectionPackage['slot_info']:
        if key == slot:
            return ConnectionPackage['slot_info'][key]['game']


print(slotname('4'), "sent", itemcheck(slotgame('1'),66001), "to", slotname('1'), "it was located at [", locationcheck(slotgame('4'), 67555),"]")
