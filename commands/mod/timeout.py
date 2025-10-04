import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
import re

def parse_duration_string(duration: str) -> timedelta | None:
    total = timedelta()
    pattern = re.compile(r"(\d+)([dhm])", re.IGNORECASE)
    matches = pattern.findall(duration)
    if not matches:
        return None
    for value, unit in matches:
        value = int(value)
        unit = unit.lower()
        if unit == "d":
            total += timedelta(days=value)
        elif unit == "h":
            total += timedelta(hours=value)
        elif unit == "m":
            total += timedelta(minutes=value)
    return total if total.total_seconds() > 0 else None

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="timeout", description="Temporarily timeout a member.")
    @app_commands.describe(
        user="The member to timeout",
        duration="Duration (e.g., 1d 10h 5m)",
        reason="Reason for the timeout"
    )
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str):
        if user.timed_out_until and user.timed_out_until > discord.utils.utcnow():
            await interaction.response.send_message(f"{user.mention} is already timed out.", ephemeral=True)
            return

        td = parse_duration_string(duration)
        if not td:
            await interaction.response.send_message("Invalid duration! Use format like 1d 10h 5m.", ephemeral=True)
            return

        try:
            try:
                await user.send(
                    f"Uh oh! You have been timed out from {interaction.guild.name} for {duration}! "
                    f"The reason behind this is {reason}."
                )
            except discord.Forbidden:
                pass

            await user.timeout(td, reason=reason)
            await interaction.response.send_message(f"Timed out {user.mention} for {duration} successfully!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(f"You cannot time out {user.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Timeout(bot))