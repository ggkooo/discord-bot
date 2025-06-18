import os
import discord
from discord.ext import commands
from discord import app_commands

class ModifiedBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = ModifiedBot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

bot.run(os.getenv('DISCORD_TOKEN'))
