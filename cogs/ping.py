import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PING_ENABLED = os.getenv("PING_ENABLED", "false").lower() == "true"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = discord.Bot(intents=intents)

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        if message.content.lower().startswith("ping"):
            await message.reply("pong!", mention_author=True)

def setup(bot):
    if PING_ENABLED:
        bot.add_cog(PingCog(bot))
    else:
        print("PingCog not loaded (disabled via .env)")
