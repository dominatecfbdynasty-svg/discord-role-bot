import fix_audioop
import sys
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

sys.stdout = open(sys.stdout.fileno(), mode='w', buffering=1)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

WORDPRESS_SITE = os.getenv('WORDPRESS_SITE', 'https://dominatecfbdynasty.com')
WORDPRESS_USER = os.getenv('WORDPRESS_USER', 'david@dominatecfbdynasty.com')
WORDPRESS_PASS = os.getenv('WORDPRESS_PASS')

@bot.event
async def on_ready():
    print(f'✅ Bot online', flush=True)

@bot.command()
async def verify(ctx, email: str):
    """Verify membership: !verify user@email.com"""
    
    print(f"VERIFY TRIGGERED: {email}", flush=True)
    
    try:
        url = f"{WORDPRESS_SITE}/wp-json/profilepress/v1/members"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"URL: {url}", flush=True)
        
        response = requests.get(
            url,
            params={"email": email},
            auth=HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASS),
            headers=headers,
            timeout=5
        )
        
        print(f"Status: {response.status_code}", flush=True)
        print(f"Response: {response.text[:200]}", flush=True)
        
        if response.status_code in [200, 202]:
            data = response.json()
            print(f"Parsed JSON: {data}", flush=True)
            
            is_active = False
            
            if isinstance(data, list) and len(data) > 0:
                is_active = data[0].get('is_active') or data[0].get('subscription_status') == 'active'
            elif isinstance(data, dict):
                is_active = data.get('is_active') or data.get('subscription_status') == 'active'
            
            print(f"Is Active: {is_active}", flush=True)
            
            if is_active:
                role = discord.utils.get(ctx.guild.roles, name="Premium Member")
                if role:
                    await ctx.author.add_roles(role)
                    await ctx.send(f"✅ Verified as Premium Member!")
                else:
                    await ctx.send("❌ Premium Member role not found")
            else:
                await ctx.send("❌ Not an active member")
        else:
            await ctx.send(f"❌ API error: {response.status_code}")
    
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}", flush=True)
        await ctx.send(f"❌ Error: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {error}")

bot.run(os.getenv('DISCORD_TOKEN'))
