import asyncio
from datetime import datetime
from pytz import timezone
import os
import discord
from discord import app_commands
from discord.ext import commands

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='🛒 Comprar', style=discord.ButtonStyle.gray, custom_id='buy_ticket')
    async def buy_ticket_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        manager = TicketManager(interaction, "Compra")
        await manager.create_ticket_channel()

    @discord.ui.button(label='🛠️ Suporte', style=discord.ButtonStyle.gray, custom_id='support_ticket')
    async def support_ticket_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        manager = TicketManager(interaction, "Suporte")
        await manager.create_ticket_channel()

    @discord.ui.button(label='🎥 Media Creator', style=discord.ButtonStyle.gray, custom_id='mc_ticket')
    async def mc_ticket_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        manager = TicketManager(interaction, "Media Creator")
        await manager.create_ticket_channel()

class TicketViewOpened(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='❌ Fechar', style=discord.ButtonStyle.gray, custom_id='close_ticket')
    async def close_ticket_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        transcript_cog = interaction.client.get_cog("TranscriptCog")
        if transcript_cog:
            await transcript_cog.save_transcript(interaction.channel, interaction)
            msg = await interaction.response.send_message("Transcript salvo. Seu ticket será deletado em 5 segundos.", ephemeral=True)
            # Aguarda o envio da mensagem e edita a cada segundo
            followup = await interaction.original_response()
            for i in range(4, 0, -1):
                await asyncio.sleep(1)
                await followup.edit(content=f"Transcript salvo. Seu ticket será deletado em {i} segundos.")
            await asyncio.sleep(1)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("Erro ao salvar transcript: cog não encontrada.", ephemeral=True)

    @discord.ui.button(label='🕐 Lembrar', style=discord.ButtonStyle.gray, custom_id='remember_ticket')
    async def reopen_ticket_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Botão de lembrar usuario pressionado.", ephemeral=True)

class TicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name='ticket', description='Create ticket embed')
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title='🎫 Ticket | Spectre Store',
            description='Caso tenha dúvidas, algum problema com produtos ou deseja concretizar uma compra, abra um Ticket!',
            color=discord.Color.purple()
        )

        embed.set_image(url='https://media.discordapp.net/attachments/1354984897470533812/1385031706679181382/a_b3c434f165c5cd01f3cfe385f85f07ca.gif?ex=685496cb&is=6853454b&hm=0f7777c5f1236c46f1e865f0f64bd5b66e264836640952e9c86226266a81c028&=')
        embed.set_footer(text='© 2025 | Spectre Store', icon_url='https://media.discordapp.net/attachments/1354984897470533812/1354991710886953042/a_f181ebc88e6907c82c955e6c89cc14d2.gif?ex=6854119e&is=6852c01e&hm=2f57b5451965e6f64719623eb5da67f4738753091367691a68c84396aadf1993&=')

        view = TicketView()

        await interaction.response.send_message(embed=embed, ephemeral=False, view=view)

class TicketManager:
    def __init__(self, interaction: discord.Interaction, ticket_type: str):
        self.interaction = interaction
        self.guild = interaction.guild
        self.user = interaction.user
        self.ticket_type = ticket_type
        self.creation_time = datetime.now(timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')

    async def create_ticket_channel(self):
        category = discord.utils.get(self.guild.categories, name=f"🎫 {self.ticket_type}")
        if category is None:
            category = await self.guild.create_category(f"🎫 {self.ticket_type}")

        admin_id = os.getenv("ADMIN_ROLE_ID")
        support_id = os.getenv("SUPPORT_ROLE_ID")

        admin = self.guild.get_role(int(admin_id)) if admin_id else None
        support = self.guild.get_role(int(support_id)) if support_id else None

        overwrites = {
            self.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            self.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            admin: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True),
            support: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)
        }

        channel_name = f"{self.ticket_type}-{self.user.name}".replace(" ", "-").lower()

        existing = discord.utils.get(category.text_channels, name=channel_name)

        if existing:
            await self.interaction.response.send_message(f"⚠️ Você já possui um ticket aberto: {existing.mention}", ephemeral=True)
            return

        channel = await self.guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"Ticket de {self.user.display_name} | User ID: {self.user.id} | Criado em: {self.creation_time} | Tipo: {self.ticket_type}"
        )

        await self.interaction.response.send_message(
            f"✅ Seu ticket foi criado: {channel.mention}", ephemeral=True
        )

        embed = discord.Embed(
            title=f"🎫 Ticket | Spectre Store",
            description=f"Olá {self.user.mention}, seja bem-vindo ao seu ticket de **{self.ticket_type.lower()}**! Nossa equipe irá lhe atender em alguns instantes.",
            color=discord.Color.purple()
        )

        embed.set_footer(text='© 2025 | Spectre Store', icon_url='https://media.discordapp.net/attachments/1354984897470533812/1354991710886953042/a_f181ebc88e6907c82c955e6c89cc14d2.gif?ex=6854119e&is=6852c01e&hm=2f57b5451965e6f64719623eb5da67f4738753091367691a68c84396aadf1993&=')

        view = TicketViewOpened()

        await channel.send(f"{admin.mention} {support.mention} {self.user.mention}", embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))
