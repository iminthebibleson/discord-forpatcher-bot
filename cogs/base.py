import discord
from discord.ext import commands
import re
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = discord.Bot(intents=intents)

class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.excluded_users = [0000, ]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        if message.author.id in self.excluded_users:
            return

        if "base" in message.content.lower():
            embed = discord.Embed(title="Here is the base NSP",
                      description=f"`Download [Fortnite_Base.nsp](https://cdn.discordapp.com/attachments/1235973247728881704/1242915823933329528/Fortnite_Base.nsp?ex=6849d310&is=68488190&hm=150d388ca99e8fdcb414b5851d3616f7dd6d00ec52afaeeb1a95f4bc0ea81bc0&)",
                      colour=0x00b0f4)
            await message.channel.send(embed=embed, mention_author=True)

def setup(bot):
    bot.add_cog(MessageHandler(bot))
