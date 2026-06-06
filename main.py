import fix_audioop
import sys
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

sys.stdout = open(sys.stdout.fileno(), mode='w', buffering=1)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = int(os.getenv('GUILD_ID', '0'))

@bot.event
async def on_ready():
    print(f'✅ Bot online', flush=True)

@bot.event
async def on_member_join(member):
    """Auto-assign Premium Member role to anyone who joins"""
    print(f"Member joined: {member.name}", flush=True)
    
    try:
        guild = member.guild
        role = discord.utils.get(guild.roles, name="Premium Member")
        
        if role:
            await member.add_roles(role)
            print(f"Premium Member role assigned to {member.name}", flush=True)
            await member.send("✅ Welcome! You've been granted Premium Member access.")
        else:
            print(f"Premium Member role not found", flush=True)
    
    except Exception as e:
        print(f"Error assigning role: {e}", flush=True)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {error}")

bot.run(os.getenv('DISCORD_TOKEN'))
