import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import timedelta

AUTO_MSGS_FILE = "auto_messages.json"
SEND_LOOP_ACTIVE = {}  # guild_id: bool

class SendAllModal(discord.ui.Modal, title="Enviar Todas as Mensagens"):
    tempo = discord.ui.TextInput(label="Tempo (em segundos) entre mensagens", default="0", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Enviando mensagens em loop! Use o botão vermelho para parar.", ephemeral=True)
        
        with open(AUTO_MSGS_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
            
        tempo = int(self.tempo.value)
        guild_id = interaction.guild.id
        SEND_LOOP_ACTIVE[guild_id] = True
        last_message_ids = {}

        while SEND_LOOP_ACTIVE.get(guild_id, False):
            for msg in messages:
                channel_id = msg.get("channel_id")

                if not channel_id:
                    continue

                channel = interaction.guild.get_channel(int(channel_id))

                if channel:
                    last_id = last_message_ids.get(channel_id)

                    if last_id:
                        try:
                            old_msg = await channel.fetch_message(last_id)
                            await old_msg.delete()
                        except Exception:
                            pass

                    embed = discord.Embed(
                        title=msg.get("title", "Sem título"),
                        description=msg.get("description", "Sem descrição"),
                        color=discord.Color.purple()
                    )
                    
                    embed.set_footer(
                        text='© 2025 | Spectre Store',
                        icon_url='https://media.discordapp.net/attachments/1354984897470533812/1354991710886953042/a_f181ebc88e6907c82c955e6c89cc14d2.gif?ex=6854119e&is=6852c01e&hm=2f57b5451965e6f64719623eb5da67f4738753091367691a68c84396aadf1993&='
                    )

                    if msg.get("image"):
                        embed.set_image(url=msg["image"])

                    if msg.get("price"):
                        embed.add_field(name="Preço", value=f"```{msg.get('price', '0')}```", inline=False)

                    sent_msg = await channel.send(embed=embed)
                    last_message_ids[channel_id] = sent_msg.id

            if tempo > 0:
                await discord.utils.sleep_until(discord.utils.utcnow() + timedelta(seconds=tempo))

class StopAllButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Parar Todos Envios", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        SEND_LOOP_ACTIVE[guild_id] = False
        await interaction.response.send_message("Envio de mensagens parado!", ephemeral=True)

class SendAllButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Enviar Todas Mensagens", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SendAllModal())

class SendMessageButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(SendAllButton())
        self.add_item(StopAllButton())

class SendMessageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="send_messages", description="Menu to send and stop sending messages")
    @app_commands.checks.has_permissions(administrator=True)
    async def send_messages(self, interaction: discord.Interaction):
        await interaction.response.send_message("Escolha uma opção:", view=SendMessageButtons(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(SendMessageCog(bot))