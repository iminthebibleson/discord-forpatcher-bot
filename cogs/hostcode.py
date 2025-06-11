import discord
from discord.ext import commands
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HOSTCODE_ENABLED = os.getenv("HOSTCODE_ENABLED", "false").lower() == "true"

async def send_initial_message(bot):
    channel_id = 1322304866743353415
    channel = bot.get_channel(channel_id)
    if channel is None:
        print("Channel not found.")
        return

    current_time = datetime.now()
    epoch_time = int(current_time.timestamp())
    pid = os.getpid()

    embed = discord.Embed(title="Bot is Now Online", description=f"<t:{epoch_time}:R>")
    embed.set_author(
        name="Fort Patch Helper",
        icon_url="https://cdn.discordapp.com/avatars/1382046428821459024/d58ecb4970906345269a209e481936cd.webp?size=1024"
    )
    embed.add_field(name="Host ID", value=f"```cmd\n{pid}```", inline=True)
    embed.add_field(name="Shut off Host Code", value=f"```cmd\nkill {pid}```", inline=True)
    embed.add_field(name="To Run Bot", value=f"```cmd\nnohup python fortpatcher_main.py &```", inline=False)
    embed.add_field(name="View All Live Code", value=f"```cmd\nps aux | grep python```", inline=False)

    await channel.send(embed=embed)

class HostCodeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if HOSTCODE_ENABLED:
            await send_initial_message(self.bot)
        else:
            print("HostCodeCog: Skipping initial message (disabled via .env)")

def setup(bot):
    if HOSTCODE_ENABLED:
        bot.add_cog(HostCodeCog(bot))
    else:
        print("HostCodeCog not loaded (disabled via .env)")
