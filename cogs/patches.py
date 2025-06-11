import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PATCHES_ENABLED = os.getenv("PATCHES_ENABLED", "false").lower() == "true"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = discord.Bot(intents=intents)

class PatchesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.excluded_users = [0000]  # Replace with actual user IDs

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        if message.author.id in self.excluded_users:
            return

        if "patches" in message.content.lower():
            embed = discord.Embed(
                title="Here are the latest patches",
                description=(
                    "`Patches Created by: @yoshicrystal`\n\n"
                    "**Release page**\n"
                    "Download [All_patches.zip](https://github.com/YoshiCrystal9/FortPatcher-NX/releases/latest/download/all_patches.zip)"
                ),
                colour=0x00b0f4
            )
            await message.channel.send(embed=embed, mention_author=True)

def setup(bot):
    if PATCHES_ENABLED:
        bot.add_cog(PatchesCog(bot))
    else:
        print("PatchesCog not loaded (disabled via .env)")
