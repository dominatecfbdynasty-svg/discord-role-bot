@bot.event
async def on_member_join(member):
    """Auto-assign Insider role and send welcome message"""
    print(f"Member joined: {member.name}", flush=True)
    
    try:
        guild = member.guild
        role = discord.utils.get(guild.roles, name="Insider")
        
        if role:
            await member.add_roles(role)
            print(f"Insider role assigned to {member.name}", flush=True)
        
        # Send welcome message to insiders-talk channel
        welcome_channel = discord.utils.get(guild.channels, name="insiders-talk")
        if welcome_channel:
            embed = discord.Embed(
                title="🎉 New Insider!",
                description=f"Welcome {member.mention} to the Dominate CFB Dynasty premium Discord.",
                color=discord.Color.green()
            )
            await welcome_channel.send(embed=embed)
    
    except Exception as e:
        print(f"Error: {e}", flush=True)
