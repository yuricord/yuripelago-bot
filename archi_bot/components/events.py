import arc
import hikari

from archi_bot.events import DebugMessageEvent, MainChannelMessageEvent
from archi_bot.vars import DiscordBroadcastChannel, DiscordDebugChannel

plugin = arc.GatewayPlugin("events")


@plugin.listen(DebugMessageEvent)
@plugin.inject_dependencies
async def debug_channel_event_listener(
    event: DebugMessageEvent, bot: hikari.GatewayBot = arc.inject()
):
    channel = await bot.rest.fetch_channel(DiscordDebugChannel)
    await channel.send(event.content)


@plugin.listen(MainChannelMessageEvent)
@plugin.inject_dependencies
async def main_channel_event_listener(
    event: MainChannelMessageEvent, bot: hikari.GatewayBot = arc.inject()
):
    channel = await bot.rest.fetch_channel(DiscordBroadcastChannel)
    await channel.send(event.content)


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
