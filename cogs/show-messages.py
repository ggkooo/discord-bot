import discord
from discord.ext import commands
from discord import app_commands
import json
import os

AUTO_MSGS_FILE = "auto_messages.json"

class MessageSelect(discord.ui.Select):
    def __init__(self, messages):
        options = [
            discord.SelectOption(label=msg.get("titulo", f"Mensagem {i+1}"), value=str(i))
            for i, msg in enumerate(messages)
        ]
        super().__init__(placeholder="Escolha uma mensagem...", min_values=1, max_values=1, options=options)
        self.messages = messages

    async def callback(self, interaction: discord.Interaction):
        idx = int(self.values[0])
        data = self.messages[idx]
        embed = discord.Embed(
            title=data.get("titulo", "Sem título"),
            description=data.get("descricao", "Sem descrição"),
            color=discord.Color.purple()
        )
        if data.get("imagem"):
            embed.set_image(url=data["imagem"])

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
    def __init__(self, msg_id, titulo, descricao, imagem):
        super().__init__()
        self.msg_id = msg_id
        self.titulo = discord.ui.TextInput(label="Título", default=titulo, max_length=100)
        self.descricao = discord.ui.TextInput(label="Descrição", default=descricao, style=discord.TextStyle.paragraph)
        self.imagem = discord.ui.TextInput(label="URL da Imagem (opcional)", default=imagem, required=False)
        self.add_item(self.titulo)
        self.add_item(self.descricao)
        self.add_item(self.imagem)

    async def on_submit(self, interaction: discord.Interaction):
        with open(AUTO_MSGS_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
        for msg in messages:
            if msg.get("id") == self.msg_id:
                msg["titulo"] = self.titulo.value
                msg["descricao"] = self.descricao.value
                msg["imagem"] = self.imagem.value
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
        modal = EditMessageModal(
            msg_id=self.msg_id,
            titulo=msg.get("titulo", ""),
            descricao=msg.get("descricao", ""),
            imagem=msg.get("imagem", "")
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

    @app_commands.command(name="showmessages", description="Exibe as mensagens salvas no JSON")
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