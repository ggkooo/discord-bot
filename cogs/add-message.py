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
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

        self.input_title = discord.ui.TextInput(label="Título", max_length=100)
        self.input_description = discord.ui.TextInput(label="Descrição", style=discord.TextStyle.paragraph)
        self.input_price = discord.ui.TextInput(label="Preço", required=True, style=discord.TextStyle.paragraph)
        self.input_image = discord.ui.TextInput(label="URL da Imagem", required=True)
        self.input_channel_id = discord.ui.TextInput(label="ID do Canal para enviar a mensagem", required=True)

        self.add_item(self.input_title)
        self.add_item(self.input_description)
        self.add_item(self.input_price)
        self.add_item(self.input_image)
        self.add_item(self.input_channel_id)

    async def on_submit(self, interaction: discord.Interaction):
        data = {
            "title": self.input_title.value,
            "description": self.input_description.value,
            "price": self.input_price.value,
            "image": self.input_image.value,
            "channel_id": int(self.input_channel_id.value)
        }
        save_auto_message(data)
        await interaction.response.send_message("Mensagem salva no JSON!", ephemeral=True)

class AddMessageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add_message", description="Adding a new message to the auto messages list")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_message(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AddMessageModal(interaction))

async def setup(bot):
    await bot.add_cog(AddMessageCog(bot))