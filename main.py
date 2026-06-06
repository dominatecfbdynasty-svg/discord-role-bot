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
    
    print(f"\n=== VERIFY COMMAND STARTED ===")
    print(f"Email: {email}")
    print(f"WordPress Site: {WORDPRESS_SITE}")
    print(f"API Key exists: {bool(PROFILEPRESS_API)}")
    
    try:
        print(f"Making request to ProfilePress...")
        
        headers = {'Authorization': f'Bearer {PROFILEPRESS_API}'}
        print(f"Headers: {headers}")
        
        url = f"{WORDPRESS_SITE}/wp-json/profilepress/v1/members"
        print(f"URL: {url}")
        
        response = requests.get(
            url,
            params={"email": email},
            headers=headers,
            timeout=5
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response text: {response.text[:500]}")
        
        await ctx.send(f"Debug: Status {response.status_code}")
        
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        await ctx.send(f"❌ Network error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        await ctx.send(f"❌ Error: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"❌ Error: {error}")

bot.run(os.getenv('DISCORD_TOKEN'))
