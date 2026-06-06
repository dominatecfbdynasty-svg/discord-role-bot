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
PROFILEPRESS_API = os.getenv('PROFILEPRESS_API')

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    print(f'🔗 Ready to verify members via ProfilePress')

@bot.command()
async def verify(ctx, email: str):
    """Verify membership: !verify user@email.com"""
    
    try:
        # Query ProfilePress members
        response = requests.get(
            f"{WORDPRESS_SITE}/wp-json/profilepress/v1/members",
            params={"email": email},
            headers={'Authorization': f'Bearer {PROFILEPRESS_API}'},
            timeout=5
        )
        
        if response.status_code == 200:
            members = response.json()
            
            # Check if member exists and is active
            if isinstance(members, list) and len(members) > 0:
                member = members[0]
                if member.get('subscription_status') == 'active' or member.get('is_active'):
                    role = discord.utils.get(ctx.guild.roles, name="Premium Member")
                    if role:
                        await ctx.author.add_roles(role)
                        await ctx.send(f"✅ {ctx.author.mention} verified as Premium Member!")
                    else:
                        await ctx.send("❌ Premium Member role not found in server")
                else:
                    await ctx.send("❌ Your subscription is not active")
            else:
                await ctx.send("❌ Email not found in our system")
        else:
            await ctx.send(f"❌ Verification error: {response.status_code}")
    
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send(f"❌ Verification failed. Try again or contact support.")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"❌ Error: {error}")

bot.run(os.getenv('DISCORD_TOKEN'))
