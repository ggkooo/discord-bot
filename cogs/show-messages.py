import discord
from discord.ext import commands
from discord import app_commands
import json
import os

AUTO_MSGS_FILE = "auto_messages.json"

class MessageSelect(discord.ui.Select):
    def __init__(self, messages):
        options = [
            discord.SelectOption(label=msg.get("title", f"Mensagem {i+1}"), value=str(i))
            for i, msg in enumerate(messages)
        ]
        super().__init__(placeholder="Escolha uma mensagem...", min_values=1, max_values=1, options=options)
        self.messages = messages

    async def callback(self, interaction: discord.Interaction):
        idx = int(self.values[0])
        data = self.messages[idx]
        embed = discord.Embed(
            title=data.get("title", "Sem título"),
            description=data.get("description", "Sem descrição"),
            color=discord.Color.purple()
        )
        if data.get("image"):
            embed.set_image(url=data["image"])
        embed.add_field(name="Preço", value=f"```{data.get('price', '0')}```", inline=False)
        embed.set_footer(text='© 2025 | Spectre Store', icon_url='https://media.discordapp.net/attachments/1354984897470533812/1354991710886953042/a_f181ebc88e6907c82c955e6c89cc14d2.gif?ex=6854119e&is=6852c01e&hm=2f57b5451965e6f64719623eb5da67f4738753091367691a68c84396aadf1993&=')

        view = MessageButtonsView(data)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class MessageSelectView(discord.ui.View):
    def __init__(self, messages):
        super().__init__(timeout=60)
        self.add_item(MessageSelect(messages))

class MessageButtonsView(discord.ui.View):
    def __init__(self, data):
        super().__init__(timeout=60)
        self.data = data
        self.add_item(EditButton(data["id"]))
        self.add_item(DeleteButton(data["id"]))

class EditMessageModal(discord.ui.Modal, title="Editar Mensagem"):
    def __init__(self, msg_id, title, description, price, image, channel_id):
        super().__init__()
        self.msg_id = msg_id
        self.input_title = discord.ui.TextInput(label="Título", default=title, max_length=100)
        self.input_description = discord.ui.TextInput(label="Descrição", default=description, style=discord.TextStyle.paragraph)
        self.input_price = discord.ui.TextInput(label="Preço",default=price , required=True, style=discord.TextStyle.paragraph)
        self.input_image = discord.ui.TextInput(label="URL da Imagem (opcional)", default=image, required=False)
        self.input_channel_id = discord.ui.TextInput(
            label="ID do Canal para enviar a mensagem",
            default=str(channel_id) if channel_id else "",
            required=True
        )
        self.add_item(self.input_title)
        self.add_item(self.input_description)
        self.add_item(self.input_price)
        self.add_item(self.input_image)
        self.add_item(self.input_channel_id)

    async def on_submit(self, interaction: discord.Interaction):
        with open(AUTO_MSGS_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
        for msg in messages:
            if msg.get("id") == self.msg_id:
                msg["title"] = self.input_title.value
                msg["description"] = self.input_description.value
                msg["price"] = self.input_price.value
                msg["image"] = self.input_image.value
                msg["channel_id"] = int(self.input_channel_id.value)
                break
        with open(AUTO_MSGS_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)
        await interaction.response.send_message("Mensagem editada com sucesso!", ephemeral=True)

class EditButton(discord.ui.Button):
    def __init__(self, msg_id):
        super().__init__(label="Editar", style=discord.ButtonStyle.primary, custom_id=f"edit_{msg_id}")
        self.msg_id = msg_id

    async def callback(self, interaction: discord.Interaction):
        with open(AUTO_MSGS_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)

        msg = next((m for m in messages if m.get("id") == self.msg_id), None)

        if not msg:
            await interaction.response.send_message("Mensagem não encontrada.", ephemeral=True)
            return
        
        channel_id = msg.get("channel_id")
        channel_id_str = str(channel_id) if channel_id and str(channel_id).isdigit() else ""
        
        modal = EditMessageModal(
            msg_id=self.msg_id,
            title=msg.get("title", ""),
            description=msg.get("description", ""),
            price=msg.get("price", ""),
            image=msg.get("image", ""),
            channel_id=channel_id_str
        )
        
        await interaction.response.send_modal(modal)

class DeleteButton(discord.ui.Button):
    def __init__(self, msg_id):
        super().__init__(label="Deletar", style=discord.ButtonStyle.danger, custom_id=f"delete_{msg_id}")
        self.msg_id = msg_id

    async def callback(self, interaction: discord.Interaction):
        with open(AUTO_MSGS_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
        messages = [msg for msg in messages if msg.get("id") != self.msg_id]
        with open(AUTO_MSGS_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)
        await interaction.response.send_message(f"Mensagem com id {self.msg_id} deletada!", ephemeral=True)

class ShowMessagesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="show_messages", description="Show saved messages")
    @app_commands.checks.has_permissions(administrator=True)
    async def show_messages(self, interaction: discord.Interaction):
        if not os.path.exists(AUTO_MSGS_FILE):
            await interaction.response.send_message("Nenhuma mensagem salva ainda.", ephemeral=True)
            return

        with open(AUTO_MSGS_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)

        if not messages:
            await interaction.response.send_message("Nenhuma mensagem salva ainda.", ephemeral=True)
            return

        view = MessageSelectView(messages)
        await interaction.response.send_message("Selecione uma mensagem para ver detalhes:", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ShowMessagesCog(bot))