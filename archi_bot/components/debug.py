import ast
from typing import Any

import arc
import hikari
import miru

from archi_bot.tracker_client import TrackerClient
from archi_bot.vars import (
    ArchServerURL,
    ArchTrackerURL,
    DeathFileLocation,
    DebugMode,
    DiscordBroadcastChannel,
    DiscordDebugChannel,
    ItemQueueDirectory,
    OutputFileLocation,
)


def debugmode_hook(ctx: arc.Context[Any]) -> arc.HookResult:
    if DebugMode:
        return arc.HookResult()
    else:
        return arc.HookResult(abort=True)


def owner_hook(ctx: arc.Context[Any]) -> arc.HookResult:
    if ctx.author.id == 301457603693641738:
        return arc.HookResult()
    else:
        return arc.HookResult(abort=True)


class DebugPacketModal(miru.Modal, title="Send Arbitrary Packet"):
    packet = miru.TextInput(
        label="Packet Contents",
        value="{'cmd': 'INPUT', 'data': []}",
        style=hikari.TextInputStyle.PARAGRAPH,
    )

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        # You can also access the values using ctx.values,
        # Modal.values, or use ctx.get_value_by_id()
        ap_client = ctx.client.get_type_dependency(TrackerClient)
        if self.packet.value:
            packet_val = ast.literal_eval(self.packet.value)
            if isinstance(packet_val, dict):
                await ctx.respond(f"responding with packet: ```{packet_val}```")
                await ap_client.send_message(packet_val)
            else:
                await ctx.respond("Error: Packet value is not valid dict.")
        else:
            await ctx.respond("Error: No packet data specified")


plugin = arc.GatewayPlugin("debug")
plugin.add_hook(debugmode_hook)
plugin.add_hook(owner_hook)


@plugin.include
@arc.slash_command("archi_info", "DEBUG: Print all bot info to console.")
async def archi_info_command(ctx: arc.GatewayContext):
    print(DiscordBroadcastChannel)
    print(ArchTrackerURL)
    print(ArchServerURL)
    print(OutputFileLocation)
    print(DeathFileLocation)
    print(ItemQueueDirectory)
    print(DiscordDebugChannel)
    print(DebugMode)


@plugin.include
@arc.slash_command(
    "send_packet", "DEBUG: Send arbitrary packet to the Archipelago server."
)
async def send_packet_command(
    ctx: arc.GatewayContext,
    miru_client: miru.Client = arc.inject(),
) -> None:
    modal = DebugPacketModal()
    builder = modal.build_response(miru_client)
    await ctx.respond_with_builder(builder)
    miru_client.start_modal(modal)


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
