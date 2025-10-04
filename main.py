import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import platform
import logging
import asyncio

logging.getLogger('discord').setLevel(logging.CRITICAL)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PERSONAL_STATUS_MESSAGE = os.getenv("PERSONALSTATUSMESSAGE", "")
ADMIN_ROLE_ID = int(os.getenv("ADMINROLE") or 0)
MOD_ROLE_ID = int(os.getenv("MODROLE") or 0)

class ConsoleColor:
    GREEN = ''
    RED = ''
    RESET = ''

    @staticmethod
    def enable():
        if platform.system() == "Windows":
            os.system('')
        ConsoleColor.GREEN = '\033[92m'
        ConsoleColor.RED = '\033[91m'
        ConsoleColor.RESET = '\033[0m'

ConsoleColor.enable()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def role_check_decorator(folder_type: str):
    async def predicate(interaction: discord.Interaction):
        if not interaction.guild:
            return True
        user_roles = [role.id for role in interaction.user.roles]
        if folder_type == "admin":
            if ADMIN_ROLE_ID not in user_roles:
                await interaction.response.send_message(
                    "You do not have permission to use this command.", ephemeral=True
                )
                raise app_commands.CheckFailure()
        elif folder_type == "mod":
            if MOD_ROLE_ID not in user_roles and ADMIN_ROLE_ID not in user_roles:
                await interaction.response.send_message(
                    "You do not have permission to use this command.", ephemeral=True
                )
                raise app_commands.CheckFailure()
        return True
    return app_commands.check(predicate)

async def load_all_commands_async(folder):
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                path = os.path.join(root, file)
                module_path = path.replace(os.sep, '.')[:-3]
                try:
                    spec = __import__(module_path, fromlist=['setup'])
                    setup_func = getattr(spec, 'setup', None)
                    if setup_func is None:
                        continue

                    async def wrapped_setup(bot, setup_func=setup_func, module_path=module_path):
                        cog_instance = None
                        original_add_cog = bot.add_cog
                        async def temp_add_cog(cog):
                            nonlocal cog_instance
                            cog_instance = cog
                            await original_add_cog(cog)
                            for cmd in cog.get_app_commands():
                                if ".admin." in module_path:
                                    role_check_decorator("admin")(cmd)
                                elif ".mod." in module_path:
                                    role_check_decorator("mod")(cmd)
                        bot.add_cog = temp_add_cog
                        try:
                            await setup_func(bot)
                        finally:
                            bot.add_cog = original_add_cog

                    await wrapped_setup(bot)

                except Exception as e:
                    print(f"Failed to load {module_path}: {e}")

def print_role_statuses():
    if MOD_ROLE_ID > 0:
        print(f"{ConsoleColor.GREEN}Mod role is connected!{ConsoleColor.RESET}")
    else:
        print(f"{ConsoleColor.RED}Mod role is invalid!{ConsoleColor.RESET}")
    if ADMIN_ROLE_ID > 0:
        print(f"{ConsoleColor.GREEN}Admin role is connected!{ConsoleColor.RESET}")
    else:
        print(f"{ConsoleColor.RED}Admin role is invalid!{ConsoleColor.RESET}")

def print_personal_status():
    if PERSONAL_STATUS_MESSAGE:
        print(f"{ConsoleColor.GREEN}Personal Status is set to: {PERSONAL_STATUS_MESSAGE}{ConsoleColor.RESET}")
    else:
        print(f"{ConsoleColor.GREEN}Personal status is set to nothing.{ConsoleColor.RESET}")

@bot.event
async def on_ready():
    await load_all_commands_async('commands')
    await bot.tree.sync()
    if PERSONAL_STATUS_MESSAGE:
        custom_status = discord.CustomActivity(name=PERSONAL_STATUS_MESSAGE)
    else:
        custom_status = None
    await bot.change_presence(activity=custom_status)
    print(f"{ConsoleColor.GREEN}Bot is now online!{ConsoleColor.RESET}")
    print_role_statuses()
    print_personal_status()

async def run_bot():
    if not TOKEN:
        print(f"{ConsoleColor.RED}Uh oh! The bot did not connect! Try changing the bot token in .env!{ConsoleColor.RESET}")
        input("Press any key to continue . . .")
        return
    try:
        await bot.start(TOKEN)
    except discord.LoginFailure:
        print(f"{ConsoleColor.RED}Uh oh! The bot did not connect! Try changing the bot token in .env!{ConsoleColor.RESET}")
        input("Press any key to continue . . .")
    except Exception as e:
        print(f"{ConsoleColor.RED}Uh oh! The bot encountered an error: {e}{ConsoleColor.RESET}")
        input("Press any key to continue . . .")
    finally:
        await bot.close()

asyncio.run(run_bot())