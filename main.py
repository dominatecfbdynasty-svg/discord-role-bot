import fix_audioop
import sys
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import anthropic

sys.stdout = open(sys.stdout.fileno(), mode='w', buffering=1)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = int(os.getenv('GUILD_ID', '0'))
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

# Read CFB 27 knowledge files
CFB27_CONTEXT = """
You are an expert College Football 25 (CFB 27) dynasty mode coach. You have deep knowledge of:
- Recruiting strategies and pitch types
- Player development and trait progression
- Defensive and offensive schemes
- Team building and roster management
- Coach attributes and their impact
- Game strategy and playcalling

When answering questions about CFB 27, be specific, practical, and actionable. 
Reference game mechanics when relevant. Keep answers concise but informative.
"""

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

@bot.event
async def on_ready():
    print(f'✅ Bot online', flush=True)
    print(f'Claude API connected', flush=True)

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

@bot.command()
async def cfb27(ctx, *, question: str):
    """Ask a CFB 27 dynasty mode question - !cfb27 <question>"""
    
    print(f"CFB27 question from {ctx.author}: {question}", flush=True)
    
    try:
        await ctx.send("🤔 Thinking...")
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=CFB27_CONTEXT,
            messages=[
                {"role": "user", "content": question}
            ]
        )
        
        response = message.content[0].text
        print(f"Claude response: {response[:100]}", flush=True)
        
        # Split long responses into chunks (Discord 2000 char limit)
        if len(response) > 2000:
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for i, chunk in enumerate(chunks):
                await ctx.send(chunk)
        else:
            await ctx.send(response)
    
    except Exception as e:
        print(f"Error: {e}", flush=True)
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
async def help_cfb27(ctx):
    """Show CFB 27 bot commands"""
    help_text = """
**CFB 27 Dynasty Bot Commands:**

`!cfb27 <question>` - Ask about CFB 27 dynasty mode
Examples:
- `!cfb27 What's the best way to build a QB in dynasty?`
- `!cfb27 How do recruiting pitches work?`
- `!cfb27 What offensive scheme should I run?`
- `!cfb27 How do I develop young players efficiently?`
"""
    await ctx.send(help_text)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {error}")

bot.run(os.getenv('DISCORD_TOKEN'))
