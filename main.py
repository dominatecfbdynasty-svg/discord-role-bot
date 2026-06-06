import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

# Intents
intents = discord.Intents.default()
intents.members = True
intents.invites = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store invite tracking
class InviteTracker:
    def __init__(self):
        self.invite_cache = {}  # guild_id -> {code: uses}
        self.invite_roles = {}   # code -> role_id
    
    async def update_cache(self, guild):
        """Update cached invite uses"""
        if guild.id not in self.invite_cache:
            self.invite_cache[guild.id] = {}
        
        invites = await guild.invites()
        for invite in invites:
            self.invite_cache[guild.id][invite.code] = invite.uses or 0
    
    def get_used_invite(self, guild, invites):
        """Find which invite was just used"""
        if guild.id not in self.invite_cache:
            return None
        
        for invite in invites:
            old_uses = self.invite_cache[guild.id].get(invite.code, 0)
            new_uses = invite.uses or 0
            
            # If uses increased, this invite was used
            if new_uses > old_uses:
                return invite
        
        return None

tracker = InviteTracker()

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    print(f'🔗 Ready to assign roles via invite links')

@bot.command()
@commands.has_permissions(administrator=True)
async def createlink(ctx, *, role_name: str):
    """
    Create an invite link that auto-assigns a role when someone joins
    
    Usage: !createlink Premium Member
    """
    
    guild = ctx.guild
    
    # Find role
    role = discord.utils.get(guild.roles, name=role_name)
    
    if not role:
        await ctx.send(f"❌ Role **{role_name}** not found. Check role name spelling.")
        return
    
    # Create invite
    try:
        invite = await ctx.channel.create_invite(
            max_uses=0,  # unlimited
            unique=False,
            reason=f"Role invite for {role_name}"
        )
    except discord.Forbidden:
        await ctx.send("❌ Bot doesn't have permission to create invites")
        return
    
    # Store mapping
    tracker.invite_roles[invite.code] = role.id
    
    # Update cache so we can track when this invite is used
    await tracker.update_cache(guild)
    
    # Send response
    embed = discord.Embed(
        title="✅ Invite Link Created",
        description=f"Users who join via this link will get the **{role_name}** role",
        color=discord.Color.green()
    )
    embed.add_field(name="Invite Link", value=f"[Click here]({invite.url})\n`{invite.url}`", inline=False)
    embed.add_field(name="Role", value=role_name, inline=False)
    embed.add_field(name="Copies", value="Unlimited", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def listlinks(ctx):
    """Show all active role links"""
    
    if not tracker.invite_roles:
        await ctx.send("❌ No role links created yet")
        return
    
    guild = ctx.guild
    invites = await guild.invites()
    
    embed = discord.Embed(
        title="Active Role Invite Links",
        color=discord.Color.blue()
    )
    
    for invite in invites:
        if invite.code in tracker.invite_roles:
            role_id = tracker.invite_roles[invite.code]
            role = guild.get_role(role_id)
            
            if role:
                embed.add_field(
                    name=f"{role.name}",
                    value=f"[{invite.url}]({invite.url})\nUses: {invite.uses or 0}",
                    inline=False
                )
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def deletelink(ctx, code: str):
    """Delete a role link by invite code"""
    
    try:
        invite = await bot.fetch_invite(code)
        await invite.delete()
        
        if code in tracker.invite_roles:
            del tracker.invite_roles[code]
        
        await ctx.send(f"✅ Deleted invite link `{code}`")
    except discord.NotFound:
        await ctx.send(f"❌ Invite link `{code}` not found")
    except discord.Forbidden:
        await ctx.send("❌ Bot doesn't have permission to delete invites")

@bot.event
async def on_member_join(member):
    """When member joins, check which invite was used and assign role"""
    
    guild = member.guild
    
    try:
        # Get current invites
        invites_now = await guild.invites()
        
        # Find which invite was used
        used_invite = tracker.get_used_invite(guild, invites_now)
        
        if used_invite and used_invite.code in tracker.invite_roles:
            # Get the role to assign
            role_id = tracker.invite_roles[used_invite.code]
            role = guild.get_role(role_id)
            
            if role:
                await member.add_roles(role)
                print(f"✅ Assigned {role.name} to {member}")
                
                # Optional: Send DM to user
                try:
                    embed = discord.Embed(
                        title="✅ Role Assigned",
                        description=f"Welcome! You've been assigned the **{role.name}** role.",
                        color=discord.Color.green()
                    )
                    await member.send(embed=embed)
                except:
                    pass  # User has DMs disabled
        
        # Update cache for next join
        await tracker.update_cache(guild)
        
    except Exception as e:
        print(f"Error assigning role: {e}")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need administrator permissions to use this command")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing argument. Usage: `!createlink Role Name`")
    else:
        await ctx.send(f"❌ Error: {error}")

# Run bot
bot.run(os.getenv('DISCORD_TOKEN'))
