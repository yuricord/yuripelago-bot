"""
Custom hikari-arc autocomplete functions for archi_bot
"""

import arc

from archi_bot.utils import get_rando_game, get_slots_for_room
from archi_bot.utils.slots import get_slots_for_player


async def autocomplete_slot_names(
    data: arc.AutocompleteData[arc.GatewayClient, str],
) -> list[str]:
    """Autocomplete all slot names in current game."""
    rando_game = get_rando_game(data.channel_id)
    if rando_game == "NoSuchGame":
        return []
    initial_slots = get_slots_for_room(rando_game.room.id)
    if not initial_slots:
        return []
    if data.focused_value:
        slots = [s.name for s in initial_slots if data.focused_value in s.name]
    else:
        slots = [s.name for s in initial_slots]
    return slots


async def autocomplete_registered_slot_names(
    data: arc.AutocompleteData[arc.GatewayClient, str],
) -> list[str]:
    """Autocomplete a user's registered slots in the current game."""
    rando_game = get_rando_game(data.channel_id)
    if rando_game == "NoSuchGame":
        return []
    initial_slots = get_slots_for_player(rando_game.room.id, data.user.id)
    if not initial_slots:
        return []
    if not data.focused_value:
        return list(initial_slots)
    else:
        return [s for s in initial_slots if data.focused_value in s]
