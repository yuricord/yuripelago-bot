from typing import Any

import arc

from bot_vars import (
    ArchInfo,
    ArchServerURL,
    ArchTrackerURL,
    AutomaticSetup,
    DeathFileLocation,
    DeathTimecodeLocation,
    DebugMode,
    DiscordAlertUserID,
    DiscordBroadcastChannel,
    DiscordDebugChannel,
    ItemQueueDirectory,
    JoinMessage,
    OutputFileLocation,
    RegistrationDirectory,
)


def debugmode_hook(ctx: arc.Context[Any]) -> arc.HookResult:
    if DebugMode:
        return arc.HookResult()
    else:
        return arc.HookResult(abort=True)


plugin = arc.GatewayPlugin("debug")
plugin.add_hook(debugmode_hook)


@plugin.include
@arc.slash_command("archinfo", "DEBUG: Print all bot info to console.")
async def archinfo_command(ctx: arc.GatewayContext):
    print(DiscordBroadcastChannel)
    print(DiscordAlertUserID)
    print(ArchInfo)
    print(ArchTrackerURL)
    print(ArchServerURL)
    print(OutputFileLocation)
    print(DeathFileLocation)
    print(DeathTimecodeLocation)
    print(RegistrationDirectory)
    print(ItemQueueDirectory)
    print(JoinMessage)
    print(DiscordDebugChannel)
    print(AutomaticSetup)
    print(DebugMode)


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
