import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
from datetime import datetime, timedelta
import json
import os

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store user tracking data
TRACKED_USERS_FILE = "tracked_users.json"
CHECK_INTERVAL = 30  # Check every 30 seconds
ROBLOX_API_BASE = "https://users.roblox.com"
ROBLOX_PRESENCE_API = "https://presence.roblox.com"

tracked_users = {}
last_status = {}

def load_tracked_users():
    """Load tracked users from file"""
    global tracked_users
    if os.path.exists(TRACKED_USERS_FILE):
        try:
            with open(TRACKED_USERS_FILE, 'r') as f:
                tracked_users = json.load(f)
        except:
            tracked_users = {}
    return tracked_users

def save_tracked_users():
    """Save tracked users to file"""
    with open(TRACKED_USERS_FILE, 'w') as f:
        json.dump(tracked_users, f, indent=2)

@bot.event
async def on_ready():
    print(f"✓ Bot logged in as {bot.user}")
    print(f"✓ Monitoring {len(tracked_users)} Roblox users")
    monitor_task.start()

@tasks.loop(seconds=CHECK_INTERVAL)
async def monitor_task():
    """Check status of all tracked Roblox users"""
    if not tracked_users:
        return
    
    async with aiohttp.ClientSession() as session:
        for roblox_username, discord_channel_id in tracked_users.items():
            try:
                # Get user ID from username
                user_id = await get_roblox_user_id(session, roblox_username)
                if not user_id:
                    continue
                
                # Get user presence
                is_online = await check_roblox_user_online(session, user_id)
                
                # Check if status changed
                if roblox_username not in last_status:
                    last_status[roblox_username] = is_online
                elif last_status[roblox_username] != is_online:
                    last_status[roblox_username] = is_online
                    
                    # Send notification
                    channel = bot.get_channel(int(discord_channel_id))
                    if channel:
                        if is_online:
                            embed = discord.Embed(
                                title="🟢 User Online!",
                                description=f"**{roblox_username}** just came online!",
                                color=discord.Color.green(),
                                timestamp=datetime.now()
                            )
                            embed.add_field(name="Status", value="Active on Roblox", inline=False)
                            embed.set_footer(text="Roblox Status Monitor")
                            
                            await channel.send(embed=embed)
                            print(f"[{datetime.now()}] ✓ {roblox_username} came online!")
                        else:
                            embed = discord.Embed(
                                title="🔴 User Offline",
                                description=f"**{roblox_username}** just went offline",
                                color=discord.Color.red(),
                                timestamp=datetime.now()
                            )
                            embed.set_footer(text="Roblox Status Monitor")
                            
                            await channel.send(embed=embed)
                            print(f"[{datetime.now()}] ✗ {roblox_username} went offline!")
                            
            except Exception as e:
                print(f"Error checking {roblox_username}: {e}")

async def get_roblox_user_id(session, username):
    """Get Roblox user ID from username"""
    try:
        async with session.post(
            f"{ROBLOX_API_BASE}/v1/usernames/users",
            json={"usernames": [username], "excludeBannedUsers": False}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("data"):
                    return data["data"][0].get("id")
    except Exception as e:
        print(f"Error getting user ID: {e}")
    return None

async def check_roblox_user_online(session, user_id):
    """Check if a Roblox user is currently online"""
    try:
        async with session.get(
            f"{ROBLOX_PRESENCE_API}/v1/presence/users",
            params={"userIds": [user_id]}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("userPresences"):
                    presence = data["userPresences"][0]
                    user_presence_type = presence.get("userPresenceType", 0)
                    # 0 = Offline, 1 = Online, 2 = InGame, 3 = InStudio
                    return user_presence_type > 0
    except Exception as e:
        print(f"Error checking user online status: {e}")
    return False

@bot.command(name="snipe", help="Start tracking a Roblox user")
async def snipe(ctx, roblox_username: str):
    """Track a Roblox user and get notifications when they come online"""
    # Verify the user exists
    async with aiohttp.ClientSession() as session:
        user_id = await get_roblox_user_id(session, roblox_username)
    
    if not user_id:
        await ctx.send(f"❌ Roblox user **{roblox_username}** not found!")
        return
    
    # Add to tracked users
    tracked_users[roblox_username] = ctx.channel.id
    save_tracked_users()
    
    embed = discord.Embed(
        title="✓ Now Sniping",
        description=f"Tracking **{roblox_username}**",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    embed.add_field(name="Notifications", value=f"You'll be notified in {ctx.channel.mention}", inline=False)
    embed.add_field(name="User ID", value=str(user_id), inline=True)
    embed.set_footer(text="Roblox Status Monitor")
    
    await ctx.send(embed=embed)
    print(f"[{datetime.now()}] 👁️ Now tracking: {roblox_username}")

@bot.command(name="unsnipe", help="Stop tracking a Roblox user")
async def unsnipe(ctx, roblox_username: str):
    """Stop tracking a Roblox user"""
    if roblox_username in tracked_users:
        del tracked_users[roblox_username]
        if roblox_username in last_status:
            del last_status[roblox_username]
        save_tracked_users()
        
        await ctx.send(f"✓ Stopped tracking **{roblox_username}**")
        print(f"[{datetime.now()}] 👁️ Stopped tracking: {roblox_username}")
    else:
        await ctx.send(f"❌ **{roblox_username}** is not being tracked")

@bot.command(name="sniping", help="List all tracked users")
async def sniping(ctx):
    """List all currently tracked Roblox users"""
    if not tracked_users:
        await ctx.send("❌ No users are currently being tracked")
        return
    
    embed = discord.Embed(
        title="👁️ Sniping List",
        description=f"Currently tracking {len(tracked_users)} user(s)",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    for username, channel_id in tracked_users.items():
        status = "🟢 Online" if last_status.get(username) else "🔴 Offline"
        embed.add_field(name=username, value=f"{status}", inline=False)
    
    embed.set_footer(text="Roblox Status Monitor")
    await ctx.send(embed=embed)

@bot.command(name="status", help="Check a user's current status")
async def status(ctx, roblox_username: str):
    """Check the current online status of a Roblox user"""
    async with aiohttp.ClientSession() as session:
        user_id = await get_roblox_user_id(session, roblox_username)
        if not user_id:
            await ctx.send(f"❌ Roblox user **{roblox_username}** not found!")
            return
        
        is_online = await check_roblox_user_online(session, user_id)
    
    if is_online:
        embed = discord.Embed(
            title="🟢 User Online",
            description=f"**{roblox_username}** is currently online",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
    else:
        embed = discord.Embed(
            title="🔴 User Offline",
            description=f"**{roblox_username}** is currently offline",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
    
    embed.set_footer(text="Roblox Status Monitor")
    await ctx.send(embed=embed)

@bot.command(name="help_sniper", help="Show sniper commands")
async def help_sniper(ctx):
    """Show all available sniper commands"""
    embed = discord.Embed(
        title="👁️ Roblox Sniper Commands",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="!snipe <username>",
        value="Start tracking a Roblox user",
        inline=False
    )
    embed.add_field(
        name="!unsnipe <username>",
        value="Stop tracking a Roblox user",
        inline=False
    )
    embed.add_field(
        name="!sniping",
        value="List all tracked users",
        inline=False
    )
    embed.add_field(
        name="!status <username>",
        value="Check a user's current status",
        inline=False
    )
    embed.add_field(
        name="!help_sniper",
        value="Show this help message",
        inline=False
    )
    
    embed.set_footer(text="Roblox Status Monitor")
    await ctx.send(embed=embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument: {error.param.name}")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Use `!help_sniper` for available commands")
    else:
        await ctx.send(f"❌ Error: {str(error)}")

if __name__ == "__main__":
    # Load tracked users from file
    load_tracked_users()
    
    # Get bot token from environment variable
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN environment variable not set!")
        exit(1)
    
    bot.run(TOKEN)
