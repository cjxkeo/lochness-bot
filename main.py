"""
main.py — Bot entry point.

Loads all cogs from the cogs/ folder automatically and starts the bot.
To add a new cog: create cogs/yourcog.py with a `setup(bot)` function.
"""

import os
import asyncio
import discord
from discord.ext import commands

import config

# ---------------------------------------------------------------------------
# Bot setup
# ---------------------------------------------------------------------------

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

    if config.SOURCE_CHANNEL_ID == 0 or config.DESTINATION_CHANNEL_ID == 0:
        print("⚠️  WARNING: SOURCE_CHANNEL_ID or DESTINATION_CHANNEL_ID not set!")
        print("   Set them as environment variables or update config.py.")
    else:
        src  = bot.get_channel(config.SOURCE_CHANNEL_ID)
        dest = bot.get_channel(config.DESTINATION_CHANNEL_ID)
        print(f"📥 Monitoring : {src.name  if src  else f'Channel {config.SOURCE_CHANNEL_ID} NOT FOUND'}")
        print(f"📤 Destination: {dest.name if dest else f'Channel {config.DESTINATION_CHANNEL_ID} NOT FOUND'}")


@bot.event
async def on_message(message: discord.Message):
    """Bot mention reply — everything else is handled by cogs."""
    if message.author.bot:
        await bot.process_commands(message)
        return

    if bot.user.mentioned_in(message):
        await message.channel.send("Imma turn into a lochness")
        # Don't return here — fall through to process_commands so cog
        # listeners still fire even on mention messages.

    await bot.process_commands(message)


# ---------------------------------------------------------------------------
# Startup: load all cogs
# ---------------------------------------------------------------------------

async def main():
    async with bot:
        cog_dir = os.path.join(os.path.dirname(__file__), "cogs")

        for filename in sorted(os.listdir(cog_dir)):
            if filename.endswith(".py") and not filename.startswith("_"):
                ext = f"cogs.{filename[:-3]}"
                try:
                    await bot.load_extension(ext)
                    print(f"  ✅ Loaded cog: {ext}")
                except Exception as e:
                    print(f"  ❌ Failed to load cog {ext}: {e}")

        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("❌ DISCORD_TOKEN environment variable is not set!")
            raise SystemExit(1)

        print("🚀 Starting bot...")
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
