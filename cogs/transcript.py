import discord
from discord.ext import commands
import os
import uuid
import aiohttp
import zipfile
import shutil

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
        
        if transcript_channel:
            await transcript_channel.send(
                #content=f"Transcript do ticket #{channel.name}:",
                file=discord.File(zip_path)
            )

        shutil.rmtree(folder_path)
        os.remove(zip_path)

        return zip_path

async def setup(bot: commands.Bot):
    await bot.add_cog(TranscriptCog(bot))