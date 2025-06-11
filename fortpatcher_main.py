import discord
import os
from dotenv import load_dotenv
import traceback

load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True
intents.voice_states = True  
bot = discord.Bot(intents=intents)

cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs')
for filename in os.listdir(cogs_dir):
    if filename.endswith('.py'):
        try:
            bot.load_extension(f'cogs.{filename[:-3]}')
        except Exception as e:
            traceback.print_exc()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

bot.run(os.getenv('TOKEN')) # run the bot with the token