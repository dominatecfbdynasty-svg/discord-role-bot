import fix_audioop  # Must be first!
import discord
from discord.ext import commands
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.invites = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store invite tracking
invite_roles = {}
invite_cache = {}

async def update_cache(guild):
    """Update cached invite uses"""
    if guild.id not in invite_cache:
        invite_cache[guild.id] = {}
    
    try:
        invites = await guild.invites()
        for invite in invites:
            invite_cache[guild.id][invite.code] = invite.uses or 0
    except:
        pass

def get_used_invite(guild, invites):
    """Find which invite was just used"""
    if guild.id not in invite_cache:
        return None
    
    for invite in invites:
        old_uses = invite_cache[guild.id].get(invite.code, 0)
        new_uses = invite.uses or 0
        
        if new_uses > old_uses:
            return invite
    
    return None

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    print(f'🔗 Ready to assign roles via invite links')

@bot.command()
@commands.has_permissions(administrator=True)
async def createlink(ctx, *, role_name: str):
    """Create an invite link that auto-assigns a role"""
    
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)
    
    if not role:
        await ctx.send(f"❌ Role **{role_name}** not found")
        return
    
    try:
        invite = await ctx.channel.create_invite(max_uses=0, unique=False)
    except discord.Forbidden:
        await ctx.send("❌ Bot doesn't have permission to create invites")
        return
    
    invite_roles[invite.code] = role.id
    await update_cache(guild)
    
    embed = discord.Embed(
        title="✅ Invite Link Created",
        description=f"Users who join via this link will get **{role_name}**",
        color=discord.Color.green()
    )
    embed.add_field(name="Link", value=invite.url, inline=False)
    embed.add_field(name="Role", value=role_name, inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def listlinks(ctx):
    """Show all active role links"""
    
    if not invite_roles:
        await ctx.send("❌ No role links created yet")
        return
    
    guild = ctx.guild
    invites = await guild.invites()
    
    embed = discord.Embed(title="Active Role Invite Links", color=discord.Color.blue())
    
    for invite in invites:
        if invite.code in invite_roles:
            role_id = invite_roles[invite.code]
            role = guild.get_role(role_id)
            
            if role:
                embed.add_field(name=role.name, value=f"{invite.url}\nUses: {invite.uses or 0}", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def deletelink(ctx, code: str):
    """Delete a role link"""
    
    try:
        invite = await bot.fetch_invite(code)
        await invite.delete()
        
        if code in invite_roles:
            del invite_roles[code]
        
        await ctx.send(f"✅ Deleted invite link")
    except discord.NotFound:
        await ctx.send(f"❌ Invite link not found")
    except discord.Forbidden:
        await ctx.send("❌ Bot doesn't have permission")

@bot.event
async def on_member_join(member):
    """When member joins, assign role based on invite"""
    
    guild = member.guild
    
    try:
        invites_now = await guild.invites()
        used_invite = get_used_invite(guild, invites_now)
        
        if used_invite and used_invite.code in invite_roles:
            role_id = invite_roles[used_invite.code]
            role = guild.get_role(role_id)
            
            if role:
                await member.add_roles(role)
                print(f"✅ Assigned {role.name} to {member}")
        
        await update_cache(guild)
    except Exception as e:
        print(f"Error: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need admin permissions")
    else:
        await ctx.send(f"❌ Error: {error}")

bot.run(os.getenv('DISCORD_TOKEN'))
