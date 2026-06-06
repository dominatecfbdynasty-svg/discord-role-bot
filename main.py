import fix_audioop
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import requests

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

WORDPRESS_SITE = os.getenv('WORDPRESS_SITE', 'https://dominatecfbdynasty.com')
PROFILEPRESS_API = os.getenv('PROFILEPRESS_API')

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    print(f'🔗 Ready to verify members via ProfilePress')

@bot.command()
async def verify(ctx, email: str):
    """Verify membership: !verify user@email.com"""
    await ctx.send(f"Got email: {email}")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"❌ Error: {error}")

bot.run(os.getenv('DISCORD_TOKEN'))
