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
    
    print(f"\n=== VERIFY STARTED ===")
    print(f"Email: {email}")
    
    try:
        headers = {'Authorization': f'Bearer {PROFILEPRESS_API}'}
        url = f"{WORDPRESS_SITE}/wp-json/profilepress/v1/members"
        
        response = requests.get(
            url,
            params={"email": email},
            headers=headers,
            timeout=5
        )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Length: {len(response.text)}")
        print(f"Raw Response: '{response.text}'")
        print(f"Response Headers: {dict(response.headers)}")
        
        await ctx.send(f"Status: {response.status_code}, Content Length: {len(response.text)}")
    
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send(f"Error: {e}")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {error}")

bot.run(os.getenv('DISCORD_TOKEN'))
