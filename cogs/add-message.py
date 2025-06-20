import discord
from discord.ext import commands
from discord import app_commands
import json
import os

AUTO_MSGS_FILE = "auto_messages.json"

def save_auto_message(data):
    if os.path.exists(AUTO_MSGS_FILE):
        with open(AUTO_MSGS_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
    else:
        messages = []
    if messages:
        next_id = max(msg.get("id", 0) for msg in messages) + 1
    else:
        next_id = 1
    data["id"] = next_id
    messages.append(data)
    with open(AUTO_MSGS_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

class AddMessageModal(discord.ui.Modal, title="Adicionar Mensagem"):
    titulo = discord.ui.TextInput(label="Título", max_length=100)
    descricao = discord.ui.TextInput(label="Descrição", style=discord.TextStyle.paragraph)
    imagem = discord.ui.TextInput(label="URL da Imagem (opcional)", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        data = {
            "titulo": self.titulo.value,
            "descricao": self.descricao.value,
            "imagem": self.imagem.value
        }
        save_auto_message(data)
        await interaction.response.send_message("Mensagem salva no JSON!", ephemeral=True)

class AddMessageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addmessage", description="Adiciona uma nova mensagem ao JSON")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_message(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AddMessageModal())

async def setup(bot):
    await bot.add_cog(AddMessageCog(bot))