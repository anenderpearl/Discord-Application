import discord
from discord import app_commands
from discord.ext import commands

class MemberCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="membercount", description="Shows the number of members in this server!")
    async def membercount(self, interaction: discord.Interaction):
        await interaction.response.send_message("Member count has been sent in this channel!", ephemeral=True)
        await interaction.channel.send(f"There are {interaction.guild.member_count} members in this server!")

async def setup(bot):
    await bot.add_cog(MemberCount(bot))
