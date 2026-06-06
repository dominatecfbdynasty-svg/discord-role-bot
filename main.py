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
    print(f'🔗 Ready to verify members')

@bot.command()
async def verify(ctx, email: str):
    """Verify membership: !verify user@email.com"""
    
    print(f"\n=== VERIFY ===")
    print(f"Email: {email}")
    
    try:
        # Check ProfilePress members via WordPress REST API
        url = f"{WORDPRESS_SITE}/wp-json/profilepress/v1/members"
        
        response = requests.get(
            url,
            params={"email": email},
            auth=HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASS),
            timeout=5
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Data: {data}")
            
            is_active = False
            if isinstance(data, list) and len(data) > 0:
                is_active = data[0].get('is_active') or data[0].get('subscription_status') == 'active'
            elif isinstance(data, dict):
                is_active = data.get('is_active') or data.get('subscription_status') == 'active'
            
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
            await ctx.send(f"❌ Error: {response.status_code}")
    
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send(f"❌ Error: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {error}")

bot.run(os.getenv('DISCORD_TOKEN'))
