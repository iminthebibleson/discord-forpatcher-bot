import re
import os
from dotenv import load_dotenv
from discord.ext import commands, tasks
from google.oauth2 import service_account
from googleapiclient.discovery import build
import discord

# Load environment variables
load_dotenv()
STATUS_ENABLED = os.getenv("STATUS_ENABLED", "false").lower() == "true"

class StatusCog(commands.Cog):
    def __init__(self, bot, service_account_file, folder_id):
        self.bot = bot
        self.folder_id = folder_id

        SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES
        )
        self.service = build("drive", "v3", credentials=credentials)

        self.latest_version = (0, 0, 0)
        self.latest_file_name = None

        self.check_version_loop.start()

    def cog_unload(self):
        self.check_version_loop.cancel()

    def extract_version(self, file_name):
        match = re.search(
            r"Fortnite(?: for Nintendo Switch)? (\d+\.\d+(?:\.\d+)?)", file_name
        )
        if match:
            return match.group(1)
        return None

    def get_latest_file_version(self):
        query = f"'{self.folder_id}' in parents and trashed = false"
        results = (
            self.service.files()
            .list(
                q=query,
                fields="files(name, id)",
                pageSize=1000,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )

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
            return latest_file["name"], latest_version
        else:
            return None, None

    @tasks.loop(minutes=1)
    async def check_version_loop(self):
        latest_name, latest_version = self.get_latest_file_version()
        if latest_name and latest_version:
            if latest_version != self.latest_version:
                self.latest_version = latest_version
                self.latest_file_name = latest_name
                version_str = ".".join(str(x) for x in latest_version)
                activity = discord.Game(name=f"File Version: {version_str}")
                await self.bot.change_presence(
                    status=discord.Status.online, activity=activity
                )
        else:
            print("[StatusCog] Could not fetch latest version")

    @check_version_loop.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

def setup(bot):
    if STATUS_ENABLED:
        service_account_file = './fortpatcher-8930e406fa47.json'
        folder_id = '12NBp7-44cxLguccbsowm4emGhy3zq0Qd'
        bot.add_cog(StatusCog(bot, service_account_file, folder_id))
    else:
        print("StatusCog not loaded (disabled via .env)")
