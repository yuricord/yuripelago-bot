import json

from bot_vars import (
    ArchConnectionDump,
    ArchDataDump,
    ArchGameDump,
    ConnectionPackage,
    DumpJSON,
    ItemFilterLevel,
)


def write_data_package(data):
    with open(ArchDataDump, "w") as f:
        json.dump(data, f)

    with open(ArchDataDump, "r") as f:
        LoadedJSON = json.load(f)

    Games = LoadedJSON["data"]["games"]

    with open(ArchGameDump, "w") as f:
        json.dump(Games, f)


def write_connection_package(data):
    with open(ArchConnectionDump, "w") as f:
        json.dump(data, f)


def lookup_item(game, id):
    for key in DumpJSON[game]["item_name_to_id"]:
        if str(DumpJSON[game]["item_name_to_id"][key]) == str(id):
            return str(key)
    return str("NULL")


def lookup_location(game, id):
    for key in DumpJSON[game]["location_name_to_id"]:
        if str(DumpJSON[game]["location_name_to_id"][key]) == str(id):
            return str(key)
    return str("NULL")


def lookup_slot(slot):
    for key in ConnectionPackage["slot_info"]:
        if key == slot:
            return str(ConnectionPackage["slot_info"][key]["name"])
    return str("NULL")


def lookup_game(slot):
    for key in ConnectionPackage["slot_info"]:
        if key == slot:
            return str(ConnectionPackage["slot_info"][key]["game"])
    return str("NULL")


def item_filter(itemclass):
    if ItemFilterLevel == 2:
        if itemclass == 1:
            return True
        else:
            return False
    elif ItemFilterLevel == 1:
        if itemclass == 1 or itemclass == 2:
            return True
        else:
            return False
    elif ItemFilterLevel == 0:
        return True
    else:
        return True


async def cancel_process():
    return 69420
