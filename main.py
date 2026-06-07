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
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f'Connected to guild: {guild.name}', flush=True)
        bot_member = guild.me
        print(f'Bot member: {bot_member.name}', flush=True)
        print(f'Bot top role: {bot_member.top_role}', flush=True)
        role = discord.utils.get(guild.roles, name="Premium Member")
        print(f'Premium Member role found: {role}', flush=True)
        if role:
            print(f'Role ID: {role.id}', flush=True)
            print(f'Bot can manage role: {bot_member.top_role > role}', flush=True)
    else:
        print(f'Guild {GUILD_ID} not found', flush=True)

@bot.event
async def on_member_join(member):
    """Auto-assign Premium Member role to anyone who joins"""
    print(f'\n=== MEMBER JOINED ===', flush=True)
    print(f'Member: {member.name}#{member.discriminator}', flush=True)
    print(f'Guild: {member.guild.name}', flush=True)
    
    try:
        guild = member.guild
        print(f'Getting Premium Member role...', flush=True)
        
        role = discord.utils.get(guild.roles, name="Premium Member")
        print(f'Role found: {role}', flush=True)
        
        if role:
            print(f'Role exists, attempting to add...', flush=True)
            await member.add_roles(role)
            print(f'✅ Role added successfully', flush=True)
            
            await member.send("✅ Welcome! You've been granted Premium Member access.")
        else:
            print(f'❌ Premium Member role not found in guild', flush=True)
            print(f'Available roles: {[r.name for r in guild.roles]}', flush=True)
    
    except Exception as e:
        print(f'❌ Error: {type(e).__name__}: {e}', flush=True)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {error}")

bot.run(os.getenv('DISCORD_TOKEN'))
