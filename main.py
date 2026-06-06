import fix_audioop
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import requests
import json

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
    print(f"WordPress Site: {WORDPRESS_SITE}")
    
    try:
        headers = {'Authorization': f'Bearer {PROFILEPRESS_API}'}
        url = f"{WORDPRESS_SITE}/wp-json/profilepress/v1/members"
        
        print(f"Making request to: {url}")
        
        response = requests.get(
            url,
            params={"email": email},
            headers=headers,
            timeout=5
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 202]:
            data = response.json()
            print(f"Parsed JSON: {data}")
            
            # Check if member is active
            is_active = False
            
            if isinstance(data, dict):
                is_active = data.get('is_active') or data.get('subscription_status') == 'active'
            elif isinstance(data, list) and len(data) > 0:
                is_active = data[0].get('is_active') or data[0].get('subscription_status') == 'active'
            
            print(f"Is Active: {is_active}")
            
            if is_active:
                role = discord.utils.get(ctx.guild.roles, name="Premium Member")
                if role:
                    await ctx.author.add_roles(role)
                    await ctx.send(f"✅ {ctx.author.mention} verified as Premium Member!")
                else:
                    await ctx.send("❌ Premium Member role not found")
            else:
                await ctx.send("❌ Email not found or subscription not active")
        else:
            await ctx.send(f"❌ API error: {response.status_code}")
    
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        await ctx.send(f"❌ Error: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"❌ Error: {error}")

bot.run(os.getenv('DISCORD_TOKEN'))
