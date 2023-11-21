#Cardinal System Bot
import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from cogs.vps_status_cog import VPSStatus
#from cogs.calender_cog import CalendarCog
from cogs.bump import BumpCog

INITAL_EXTENSIONS = [
    "cogs.vps_status_cog",
    #"cogs.calender_cog",
    "cogs.bump"
]

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

class DiscordBot(commands.Bot):
    def __init__(self, intents: discord.Intents, help_command=None):
        super().__init__(
            intents=intents,
            help_command=help_command,
        )
    
    async def setup_hook(self):
        self.tree.copy_global_to(guild=discord.Object(id=1165948663596597279))
        await self.tree.sync(guild=discord.Object(id=1165948663596597279))
        return await super().setup_hook()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="c/", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.add_cog(VPSStatus(bot))
    await bot.add_cog(BumpCog(bot))
    #await bot.add_cog(CalendarCog(bot))
    print("Logged in!")

@bot.hybrid_command(name='reload')
@commands.is_owner()
async def _reload(ctx, cog_name: str):
    try:
        cog_path = f'Cog.{cog_name}'  
        await bot.unload_extension(cog_path)  
        await bot.load_extension(cog_path)  
        await ctx.send(f'{cog_name} をリロードしました。')
    except commands.ExtensionNotLoaded as e:
        await ctx.send(f'{cog_name} はまだロードされていません。')
    except Exception as e:
        await ctx.send(f'{cog_name} のリロード中にエラーが発生しました：{e}')

@bot.hybrid_command(name='statuspages')
@commands.is_owner()
async def _statuspages(ctx):
    await ctx.send("[ステータスページ](https://status.the-seed.games)")

if __name__ == "__main__":
    for cog in INITAL_EXTENSIONS:
        try:
            bot.load_extension(cog)
            print(f"{cog} loaded successfully!")
        except Exception as e:
            print(f"Failed to load {cog}: {e}")
    bot.run(TOKEN)
