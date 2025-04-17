import arc
import hikari
from aiofiles import open

from archi_bot.events import DebugMessageEvent
from archi_bot.vars import DeathFileLocation

plugin = arc.GatewayPlugin("info")


@plugin.include
@arc.slash_command("deathcount", "Get the death count for all slots")
async def deathcount_command(
    ctx: arc.GatewayContext, bot: hikari.GatewayBot = arc.inject()
):
    try:
        async with open(DeathFileLocation) as d:
            death_lines = await d.readlines()
        death_dict = {}
        for deathline in death_lines:
            death_user = deathline.split("||")[6]
            death_user = death_user.split("\n")[0]

            if death_user not in death_dict:
                death_dict[death_user] = 1
            else:
                death_dict[death_user] = death_dict[death_user] + 1

        death_dict = dict(sorted(death_dict.items()))
        death_names = []
        death_counts = []
        message = "**Death Counter:**\n```"
        deathkeys = death_dict.keys()
        for key in deathkeys:
            death_names.append(str(key))
            death_counts.append(int(death_dict[key]))
            message = message + "\n" + str(key) + ": " + str(death_dict[key])
        message = message + "```"
        await ctx.respond(message)
    except Exception as e:
        bot.dispatch(
            DebugMessageEvent(app=bot, content=f"Error with DeathCount ```{e}```")
        )


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
