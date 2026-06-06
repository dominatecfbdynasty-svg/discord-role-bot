@bot.command()
async def verify(ctx, email: str):
    """Verify membership: !verify user@email.com"""
    
    try:
        # Check ProfilePress for this email
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
                
                # Check if member exists
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
