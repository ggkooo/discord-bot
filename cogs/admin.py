from datetime import datetime
import os
import discord
from discord import app_commands
from discord.ext import commands
from pytz import timezone

LOG_CHANNEL_MEMBER_JOIN = int(os.getenv('JOIN_CHANNEL_ID', '0'))
LOG_CHANNEL_MEMBER_LEAVE = int(os.getenv('LEAVE_CHANNEL_ID', '0'))
LOG_CHANNEL_MESSAGE = int(os.getenv('ANTI_CHANNEL_ID', '0'))

BAN_REASONS = [
    "Desrespeito",
    "Flood/Spam",
    "Conteúdo impróprio",
    "Outro"
]

class BanReasonSelect(discord.ui.Select):
    def __init__(self, member: discord.Member):
        options = [discord.SelectOption(label=reason, value=reason) for reason in BAN_REASONS]
        super().__init__(placeholder="Selecione o motivo do banimento...", min_values=1, max_values=1, options=options)
        self.member = member

    async def callback(self, interaction: discord.Interaction):
        reason = self.values[0]
        await self.member.ban(reason=reason)
        embed = discord.Embed(
            title='Banido',
            description=f'{self.member.mention} foi banido do servidor.\nMotivo: **{reason}**',
            color=0xBF1622
        )
        embed.set_author(
            name=self.member.display_name,
            icon_url=self.member.avatar.url if self.member.avatar else discord.Embed.Empty
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class BanReasonView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=60)
        self.add_item(BanReasonSelect(member))

class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name='clear', description='A clear command')
    @app_commands.checks.has_permissions(administrator=True)
    async def clear(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge()
        await interaction.followup.send(f"{len(deleted)} mensagens foram apagadas.", ephemeral=True)

    @app_commands.command(name='ban', description='Bane um usuário pelo ID e seleciona o motivo')
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user_id: str):
        member = interaction.guild.get_member(int(user_id))
        if not member:
            await interaction.response.send_message("Usuário não encontrado no servidor.", ephemeral=True)
            return
        await interaction.response.send_message(
            f"Selecione o motivo do banimento para {member.mention}:", 
            view=BanReasonView(member), 
            ephemeral=True
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        now = datetime.now(timezone('America/Sao_Paulo'))
        member_created = member.created_at.astimezone(timezone('America/Sao_Paulo'))
        days_since_creation = (now - member_created).days

        embed = discord.Embed(
            title='Membro entrou',
            description=f'{member.mention} | {member.name}\n**Criação:** {days_since_creation} dias atrás',
            color=0x1FFB2F
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.avatar.url if member.avatar else discord.Embed.Empty
        )
        channel = member.guild.get_channel(LOG_CHANNEL_MEMBER_JOIN)
        if channel:
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title='Membro saiu',
            description=f'{member.mention} | {member.name}',
            color=0xF91607  # Vermelho
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.avatar.url if member.avatar else discord.Embed.Empty
        )
        channel = member.guild.get_channel(LOG_CHANNEL_MEMBER_LEAVE)
        if channel:
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        channel = before.guild.get_channel(LOG_CHANNEL_MESSAGE)
        if channel:
            embed = discord.Embed(
                title='Menssagem editada',
                description=(
                    f'**Antes:** ```{before.content}```\n'
                    f'**Depois:** ```{after.content}```\n\n'
                    f'**Message ID:** {before.id}\n'
                    f'**Canal:** {before.channel.mention}\n'
                    f'**User ID:** {before.author.id}'
                ),
                color=0xFB9800
            )
            embed.set_author(
                name=before.author.display_name,
                icon_url=before.author.avatar.url if before.author.avatar else discord.Embed.Empty
            )
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        channel = message.guild.get_channel(LOG_CHANNEL_MESSAGE)
        if channel:
            embed = discord.Embed(
                title='Menssagem deletada',
                description=(
                    f'**Conteúdo:** ```{message.content}```\n\n'
                    f'**Message ID:** {message.id}\n'
                    f'**Canal:** {message.channel.mention}\n'
                    f'**User ID:** {message.author.id}'
                ),
                color=0xF91607
            )
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.avatar.url if message.author.avatar else discord.Embed.Empty
            )
            embed.set_footer(text='')
            await channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
