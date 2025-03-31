import arc
import hikari

from bot_vars import DiscordBroadcastChannel, DiscordDebugChannel
from events import DebugMessageEvent, MainChannelMessageEvent

plugin = arc.GatewayPlugin("events")


@plugin.listen(DebugMessageEvent)
async def debug_channel_event_listener(
    event: DebugMessageEvent, bot: hikari.GatewayBot = arc.inject()
):
    debug_channel = await bot.rest.fetch_channel(DiscordDebugChannel)
    debug_channel.send(event.content)


@plugin.listen(MainChannelMessageEvent)
async def main_channel_event_listener(
    event: MainChannelMessageEvent, bot: hikari.GatewayBot = arc.inject()
):
    debug_channel = await bot.rest.fetch_channel(DiscordBroadcastChannel)
    debug_channel.send(event.content)


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
