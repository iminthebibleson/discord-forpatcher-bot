import discord
from discord.ext import commands, tasks
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import re
import requests
import datetime

load_dotenv()

WEBHOOK_ENABLED = os.getenv("WEBHOOK_ENABLED", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = "fortpatcher-8930e406fa47.json"
FOLDER_ID = "12NBp7-44cxLguccbsowm4emGhy3zq0Qd"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("drive", "v3", credentials=credentials)


def send_webhook_embed(title, description, url=None):
    embed = {
        "title": title,
        "description": description,
        "color": 0x0099FF,
    }
    if url:
        embed["url"] = url

    data = {"username": "Fortnite Version Bot", "embeds": [embed]}
    response = requests.post(WEBHOOK_URL, json=data) # type: ignore
    if response.status_code == 204:
        print("Embed sent successfully!")
    else:
        print(f"Failed to send embed. Status code: {response.status_code}")


def extract_version(file_name):
    match = re.search(
        r"Fortnite(?: for Nintendo Switch)? (\d+\.\d+(?:\.\d+)?)", file_name
    )
    return match.group(1) if match else None


def generate_download_link(file_id):
    return f"https://drive.google.com/uc?id={file_id}&export=download"


def get_latest_file(folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    results = (
        service.files()
        .list(
            q=query,
            fields="files(name, id, createdTime)",
            pageSize=1000,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        .execute()
    )
    items = results.get("files", [])
    if not items:
        return None, None, None

    latest_version = (0, 0, 0)
    latest_file = None

    for item in items:
        name = item["name"]
        if not name.lower().endswith(".nsp"):
            continue
        version_str = extract_version(name)
        if version_str:
            parts = version_str.split(".")
            while len(parts) < 3:
                parts.append("0")
            ver_tuple = tuple(map(int, parts))
            if ver_tuple > latest_version:
                latest_version = ver_tuple
                latest_file = item

    if latest_file:
        return latest_file["name"], latest_file["createdTime"], latest_file["id"]
    return None, None, None


class PostUpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_seen_version = (0, 0, 0)
        if WEBHOOK_ENABLED:
            self.check_drive.start()
        else:
            print("Webhook system is disabled via .env setting.")

    def cog_unload(self):
        self.check_drive.cancel()

    @tasks.loop(seconds=60)
    async def check_drive(self):
        name, created_time, file_id = get_latest_file(FOLDER_ID)
        if name and file_id:
            version_str = extract_version(name)
            if version_str is None:
                print(f"Warning: Could not extract version from: {name}")
                return

            parts = version_str.split(".")
            while len(parts) < 3:
                parts.append("0")
            current_version = tuple(map(int, parts))

            if current_version > self.last_seen_version:
                self.last_seen_version = current_version

                if created_time:
                    created_time_clean = created_time.rstrip("Z")
                    created_dt = datetime.datetime.fromisoformat(created_time_clean)
                    unix_timestamp = int(created_dt.timestamp())
                    created_dt_str = f"<t:{unix_timestamp}:F>"
                else:
                    created_dt_str = "Unknown"

                send_webhook_embed(
                    title="New latest NSP posted!",
                    description=f"{name}\n\nUploaded at: {created_dt_str}\n\nDownload Here: [Link Download]({generate_download_link(file_id)})",
                    url=generate_download_link(file_id),
                )
                print(f"Posted new version: {version_str}")
        else:
            print("No NSP files found in folder.")


def setup(bot):
    bot.add_cog(PostUpdateCog(bot))
