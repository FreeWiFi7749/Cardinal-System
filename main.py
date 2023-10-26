#Cardinal System Bot

import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

INITAL_EXTENSIONS = [
    "cogs.vps_status_cog",
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
    print("Logged in!")

if __name__ == "__main__":
    for cog in INITAL_EXTENSIONS:
        bot.load_extension(cog)
    bot.run(TOKEN)
