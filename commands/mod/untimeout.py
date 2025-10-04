import discord
from discord import app_commands
from discord.ext import commands

class Untimeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="untimeout", description="Remove a timeout from a member.")
    @app_commands.describe(
        user="The member to remove the timeout from"
    )
    async def untimeout(self, interaction: discord.Interaction, user: discord.Member):
        if not user.timed_out_until or user.timed_out_until <= discord.utils.utcnow():
            await interaction.response.send_message(f"{user.mention} is not currently timed out.", ephemeral=True)
            return

        try:
            await user.timeout(None)
            try:
                await user.send(f"You have had your timeout removed from {interaction.guild.name}!")
            except discord.Forbidden:
                pass
            await interaction.response.send_message(f"Successfully removed timeout from {user.mention}!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Untimeout(bot))
