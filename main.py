import fix_audioop
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot online')

@bot.command()
async def verify(ctx, email: str):
    """Test command"""
    print(f"VERIFY COMMAND TRIGGERED WITH: {email}")
    await ctx.send(f"Email received: {email}")

bot.run(os.getenv('DISCORD_TOKEN'))
