import discord
from discord.ext import commands
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = "fortpatcher-8930e406fa47.json"
FOLDER_ID = "12NBp7-44cxLguccbsowm4emGhy3zq0Qd"

class UpdaterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.excluded_users = [0000]  # Replace 0000 with actual user IDs

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        self.service = build("drive", "v3", credentials=credentials)

    def extract_version(self, file_name):
        match = re.search(r"Fortnite(?: for Nintendo Switch)? (\d+\.\d+(?:\.\d+)?)", file_name)
        if match:
            return match.group(1)
        return None

    def get_latest_file(self):
        query = f"'{FOLDER_ID}' in parents and trashed = false"
        results = self.service.files().list(
            q=query,
            fields="files(name, id)",
            pageSize=1000,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()

        items = results.get("files", [])
        if not items:
            return None, None

        latest_version = (0, 0, 0)
        latest_file = None

        for item in items:
            name = item["name"]
            if not name.lower().endswith(".nsp"):
                continue
            version_str = self.extract_version(name)
            if version_str:
                parts = version_str.split(".")
                while len(parts) < 3:
                    parts.append("0")
                ver_tuple = tuple(int(p) for p in parts)
                if ver_tuple > latest_version:
                    latest_version = ver_tuple
                    latest_file = item

        if latest_file:
            return latest_file["name"], latest_file["id"]
        return None, None

    def generate_download_link(self, file_id):
        return f"https://drive.google.com/uc?id={file_id}&export=download"

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.author.id in self.excluded_users:
            return

        if "update" in message.content.lower():
            latest_name, latest_id = self.get_latest_file()
            if not latest_name or not latest_id:
                await message.channel.send("Could not find the latest NSP file.")
                return

            link = self.generate_download_link(latest_id)
            embed = discord.Embed(
                title="Here is the latest NSP file!",
                description=f"**{latest_name}**\n\n[Click to Download]({link})",
                colour=0x00b0f4,
            )
            await message.channel.send(embed=embed)

def setup(bot):
    if os.getenv("UPDATER_ENABLED", "false").lower() == "true":
        bot.add_cog(UpdaterCog(bot))
