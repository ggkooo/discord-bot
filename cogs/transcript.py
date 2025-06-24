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

        transcript_header = (
            "<!DOCTYPE html>"
            "<html lang='pt-BR'>"
            "<head>"
            "    <meta charset='UTF-8'>"
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            f"    <title>Transcript de #{channel.name}</title>"
            "    <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>"
            "    <style>"
            "        body { background-color: #36393f; color: #dcddde; padding: 20px; }"
            "        .message { display: flex; margin-bottom: 15px; }"
            "        .avatar { width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; }"
            "        .username { font-weight: bold; color: #ffffff; }"
            "        .timestamp { font-size: 0.8em; color: #b9bbbe; margin-left: 10px; }"
            "        .content { margin-top: 5px; }"
            "        .embed { border-left: 4px solid; padding: 10px; margin-top: 10px; border-radius: 5px; background-color: #2f3136; }"
            "        .embed-title { font-weight: bold; margin-bottom: 5px; color: white; }"
            "        .embed-description { color: #dcddde; }"
            "        .attachment img { max-width: 300px; border-radius: 5px; margin-top: 10px; }"
            "        .attachment a { color: #00b0f4; }"
            "    </style>"
            "</head>"
            "<body>"
            f"<h2>Transcript de #{channel.name}</h2>"
        )

        async with aiohttp.ClientSession() as session:
            async for msg in channel.history(limit=None, oldest_first=True):
                user_avatar = msg.author.avatar.url if msg.author.avatar else "https://via.placeholder.com/40"
                username = msg.author.display_name
                timestamp = msg.created_at.strftime('%d/%m/%Y %H:%M')
                content = msg.content.replace('\n', '<br>')

                # Baixar anexos
                attachments_html = ""
                for attachment in msg.attachments:
                    attachment_path = os.path.join(attachments_folder, attachment.filename)
                    async with session.get(attachment.url) as resp:
                        with open(attachment_path, "wb") as f:
                            f.write(await resp.read())
                    if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        attachments_html += f'<div class="attachment"><img src="attachments/{attachment.filename}" alt="Image"></div>'
                    else:
                        attachments_html += f'<div class="attachment"><a href="attachments/{attachment.filename}">{attachment.filename}</a></div>'

                # Embeds
                embeds_html = ""
                for embed in msg.embeds:
                    color = f"#{embed.color.value:06x}" if embed.color else "#5865F2"
                    title = embed.title or ""
                    description = embed.description or ""

                    embeds_html += (
                        f"<div class='embed' style='border-color: {color};'>"
                        f"  <div class='embed-title'>{title}</div>"
                        f"  <div class='embed-description'>{description}</div>"
                        "</div>"
                    )

                msg_html = (
                    "<div class='message'>"
                    f"  <img class='avatar' src='{user_avatar}' alt='Avatar'>"
                    "  <div>"
                    f"    <span class='username'>{username}</span>"
                    f"    <span class='timestamp'>{timestamp}</span>"
                    f"    <div class='content'>{content}</div>"
                    f"    {attachments_html}"
                    f"    {embeds_html}"
                    "  </div>"
                    "</div>"
                )

                messages.append(msg_html)

        transcript_html = transcript_header + "\n".join(messages) + "</body></html>"

        html_path = os.path.join(folder_path, f"transcript-{unique_id}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(transcript_html)

        zip_path = f"{folder_path}.zip"
        shutil.make_archive(folder_path, 'zip', folder_path)

        # Enviar o ZIP no canal de ZIPS
        channel_id = os.getenv("ZIP_CHANNEL_ID")
        zip_channel = discord.utils.get(interaction.guild.text_channels, id=int(channel_id))

        sent_message = await zip_channel.send(file=discord.File(zip_path))
        attachment_url = sent_message.attachments[0].url

        # Enviar embed de encerramento
        transcript_channel_id = os.getenv("TRANSCRIPT_CHANNEL_ID")
        transcript_channel = discord.utils.get(interaction.guild.text_channels, id=int(transcript_channel_id))

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
            embed.set_footer(
                text='© 2025 | Spectre Store',
                icon_url='https://media.discordapp.net/attachments/1354984897470533812/1354991710886953042/a_f181ebc88e6907c82c955e6c89cc14d2.gif'
            )

            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Baixar Transcript (.zip)", url=attachment_url))

            await transcript_channel.send(embed=embed, view=view)

        # Limpeza
        shutil.rmtree(folder_path)
        os.remove(zip_path)

        return zip_path


async def setup(bot: commands.Bot):
    await bot.add_cog(TranscriptCog(bot))