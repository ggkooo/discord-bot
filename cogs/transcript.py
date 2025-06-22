from datetime import datetime
from pytz import timezone
import discord
from discord.ext import commands
import os
import uuid
import aiohttp
import zipfile
import shutil

class TranscriptView(discord.ui.View):
    def __init__(self, url):
        super().__init__()
        self.add_item(discord.ui.Button(label="Baixar Transcript", url=url))

def get_ticket_creation_date(channel):
    if channel.topic:
        parts = channel.topic.split('|')
        if len(parts) > 2 and 'Criado em:' in parts[2]:
            return parts[2].split('Criado em:')[1].strip()
    return None

def get_ticket_owner(channel):
    if channel.topic:
        parts = channel.topic.split('|')
        if len(parts) > 1 and 'User ID:' in parts[1]:
            user_id_str = parts[1].split('User ID:')[1].strip()
            if user_id_str.isdigit():
                return int(user_id_str)
    return None

class TranscriptCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    async def save_transcript(self, channel: discord.TextChannel, interaction: discord.Interaction = None):
        unique_id = uuid.uuid4()
        folder_path = os.path.join('transcripts', f"transcript-{channel.name}-{unique_id}")
        os.makedirs(folder_path, exist_ok=True)
        attachments_folder = os.path.join(folder_path, 'attachments')
        os.makedirs(attachments_folder, exist_ok=True)

        messages = []
        async with aiohttp.ClientSession() as session:
            async for msg in channel.history(limit=None, oldest_first=True):
                msg_html = f"<p><strong>{msg.author}:</strong> {msg.content}</p>"
                for attachment in msg.attachments:
                    attachment_path = os.path.join(attachments_folder, attachment.filename)
                    async with session.get(attachment.url) as resp:
                        with open(attachment_path, "wb") as f:
                            f.write(await resp.read())
                    if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        msg_html += f'<br><img src="attachments/{attachment.filename}" style="max-width:300px;">'
                    else:
                        msg_html += f'<br><a href="attachments/{attachment.filename}">{attachment.filename}</a>'
                messages.append(msg_html)

        transcript = (
            "<html><head><meta charset='utf-8'><title>Transcript</title></head><body>"
            f"<h2>Transcript de #{channel.name}</h2>"
            + "\n".join(messages) +
            "</body></html>"
        )
        html_path = os.path.join(folder_path, f"transcript-{unique_id}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(transcript)

        zip_path = f"{folder_path}.zip"
        shutil.make_archive(folder_path, 'zip', folder_path)

        channel_id = os.getenv("TRANSCRIPT_CHANNEL_ID")
        transcript_channel = discord.utils.get(interaction.guild.text_channels, id=int(channel_id))

        channel_id = os.getenv("ZIP_CHANNEL_ID")
        zip_channel = discord.utils.get(interaction.guild.text_channels, id=int(channel_id))

        sent_message = await zip_channel.send(
            file=discord.File(zip_path)
        )

        attachment_url = sent_message.attachments[0].url

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Baixar Transcript (.zip)", url=attachment_url))
        
        if transcript_channel:
            creator_id = get_ticket_owner(interaction.channel)
            creator = interaction.guild.get_member(creator_id)

            embed = discord.Embed(
                title=f"Ticket Fechado",
                description=f'✅ **Aberto por:** {creator.mention if creator else "Unknown"}\n'
                        f'⏰ **Data:** {get_ticket_creation_date(interaction.channel)}\n\n'
                        f'❌ **Fechado por:** {interaction.user.mention}\n'
                        f'⏰ **Data:** {datetime.now(timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S")}\n\n',
                color=discord.Color.purple()
            )

            embed.set_footer(text='© 2025 | Spectre Store', icon_url='https://media.discordapp.net/attachments/1354984897470533812/1354991710886953042/a_f181ebc88e6907c82c955e6c89cc14d2.gif?ex=6854119e&is=6852c01e&hm=2f57b5451965e6f64719623eb5da67f4738753091367691a68c84396aadf1993&=')

            await transcript_channel.send(
                embed=embed,
                view=view
            )

        shutil.rmtree(folder_path)
        os.remove(zip_path)

        return zip_path

async def setup(bot: commands.Bot):
    await bot.add_cog(TranscriptCog(bot))