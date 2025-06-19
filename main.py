import os
from cogs.ticket import TicketView
import discord
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()

class ModifiedBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
    
    async def load_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')

    async def setup_hook(self):
        self.add_view(TicketView())
        await self.load_cogs()
        await self.tree.sync()

bot = ModifiedBot(command_prefix='/', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

bot.run(os.getenv('DISCORD_TOKEN'))
