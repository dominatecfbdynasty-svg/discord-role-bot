import fix_audioop
import sys
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Force unbuffered output
sys.stdout = open(sys.stdout.fileno(), mode='w', buffering=1)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot online', flush=True)

@bot.command()
async def verify(ctx, email: str):
    """Test command"""
    print(f"VERIFY TRIGGERED: {email}", flush=True)
    await ctx.send(f"Email: {email}")

bot.run(os.getenv('DISCORD_TOKEN'))
