import fix_audioop
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

WORDPRESS_SITE = os.getenv('WORDPRESS_SITE', 'https://dominatecfbdynasty.com')
WORDPRESS_USER = os.getenv('WORDPRESS_USER', 'david@dominatecfbdynasty.com')
WORDPRESS_PASS = os.getenv('WORDPRESS_PASS')

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')

@bot.command()
async def verify(ctx, email: str):
    """Verify membership: !verify user@email.com"""
    
    try:
        url = f"{WORDPRESS_SITE}/wp-json/profilepress/v1/members"
        
        response = requests.get(
            url,
            params={"email": email},
            auth=HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASS),
            timeout=5
        )
        
        print(f"Status: {response.status_code}")
        print(f"Full Response Text:")
        print(response.text)
        
        await ctx.send(f"Checking...")
    
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send(f"Error: {e}")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {error}")

bot.run(os.getenv('DISCORD_TOKEN'))
