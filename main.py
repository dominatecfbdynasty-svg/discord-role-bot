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
    
    try:
        headers = {'Authorization': f'Bearer {PROFILEPRESS_API}'}
        
        response = requests.get(
            f"{WORDPRESS_SITE}/wp-json/profilepress/v1/members",
            params={"email": email},
            headers=headers,
            timeout=5
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code in [200, 202]:
            try:
                data = response.json()
                print(f"Parsed data: {data}")
                
                if isinstance(data, dict):
                    is_active = data.get('is_active') or data.get('subscription_status') == 'active'
                elif isinstance(data, list) and len(data) > 0:
                    is_active = data[0].get('is_active') or data[0].get('subscription_status') == 'active'
                else:
                    is_active = False
                
                if is_active:
                    role = discord.utils.get(ctx.guild.roles, name="Premium Member")
                    if role:
                        await ctx.author.add_roles(role)
                        await ctx.send(f"✅ {ctx.author.mention} verified as Premium Member!")
                    else:
                        await ctx.send("❌ Premium Member role not found in server")
                else:
                    await ctx.send("❌ Your subscription is not active")
            except Exception as e:
                print(f"JSON parse error: {e}")
                await ctx.send(f"❌ Verification error: Could not parse response")
        else:
            await ctx.send(f"❌ Verification error: {response.status_code}")
    
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send(f"❌ Verification failed. Try again or contact support.")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"❌ Error: {error}")

bot.run(os.getenv('DISCORD_TOKEN'))
