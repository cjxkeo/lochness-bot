"""
utils.py — Shared helper functions used across multiple cogs.
Import what you need: from utils import extract_urls, is_blacklisted_file
"""

import re
import os
import asyncio
import tempfile
import aiohttp
import discord
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from config import MVSEP_BLACKLIST


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def extract_urls(text: str) -> list[str]:
    """Return all URLs found in a string."""
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(pattern, text)


# ---------------------------------------------------------------------------
# MVSEP helpers
# ---------------------------------------------------------------------------

def is_blacklisted_file(filename: str) -> tuple[bool, str | None]:
    """Return (True, matched_song) if the filename contains a blacklisted song name."""
    filename_lower = filename.lower()
    for song in MVSEP_BLACKLIST:
        if song in filename_lower:
            return True, song
    return False, None


# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------

async def _build_yt_dlp_cmd(url: str, output_template: str, audio: bool) -> list[str]:
    """Build a yt-dlp command list for audio or video download."""
    if audio:
        cmd = [
            'yt-dlp',
            '-x',
            '--audio-format', 'mp3',
            '--audio-quality', '0',
            '--max-filesize', '25M',
            '--no-playlist',
            '--quiet',
            '--no-warnings',
            '-o', output_template,
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--socket-timeout', '30',
        ]
    else:
        cmd = [
            'yt-dlp',
            '-f', 'best[filesize<=25M]/best',
            '--max-filesize', '25M',
            '--no-playlist',
            '--quiet',
            '--no-warnings',
            '-o', output_template,
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--socket-timeout', '30',
        ]

    # Reddit-specific tweaks
    if 'reddit.com' in url or 'redd.it' in url:
        cmd.extend(['--add-header', 'Referer:https://www.reddit.com/'])
        username = os.getenv('REDDIT_USERNAME')
        password = os.getenv('REDDIT_PASSWORD')
        if username and password:
            cmd.extend(['--username', username, '--password', password])
        cookies = os.getenv('REDDIT_COOKIES_FILE')
        if cookies and os.path.exists(cookies):
            cmd.extend(['--cookies', cookies])

    cmd.append(url)
    return cmd


async def _run_yt_dlp(cmd: list[str]) -> tuple[int, str]:
    """Run a yt-dlp command and return (returncode, stderr)."""
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    error = stderr.decode('utf-8', errors='ignore') if stderr else ''
    return process.returncode, error


async def download_and_post_pillowcase(url: str, channel: discord.TextChannel) -> tuple[bool, str]:
    """Scrape a Pillowcase page and post the file to *channel*."""
    msg = await channel.send("📥 Scraping Pillowcase page...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await msg.edit(content=f"❌ Could not load Pillowcase page. Status: {resp.status}")
                    return False, f"HTTP {resp.status}"
                html = await resp.text()

        soup = BeautifulSoup(html, 'html.parser')
        a = soup.find('a', {'class': 'download-button'}) or soup.find('a', href=True, string="Download")
        if not a or not a.has_attr('href'):
            await msg.edit(content="❌ Could not find the download link on the Pillowcase page.")
            return False, "No download button"

        dl_url = a['href'] if a['href'].startswith('http') else f"https://pillowcase.link{a['href']}"

        await msg.edit(content="📥 Downloading file from Pillowcase...")
        async with aiohttp.ClientSession() as session:
            async with session.get(dl_url) as resp:
                if resp.status != 200:
                    await msg.edit(content=f"❌ Failed to download file. Status: {resp.status}")
                    return False, f"HTTP {resp.status}"
                content = await resp.read()
                if len(content) > 25 * 1024 * 1024:
                    await msg.edit(content="❌ File too large for Discord (25 MB limit)")
                    return False, "File too large"
                filename = dl_url.split("/")[-1] or "pillowcase.bin"
                await channel.send(file=discord.File(fp=bytearray(content), filename=filename))

        await msg.delete()
        return True, "Success"
    except Exception as e:
        await msg.edit(content=f"❌ Pillowcase error: {e}")
        return False, str(e)


async def download_and_post_krakenfile(url: str, channel: discord.TextChannel) -> tuple[bool, str]:
    """Scrape a KrakenFiles page and post the file to *channel*."""
    msg = await channel.send("📥 Scraping KrakenFiles page...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await msg.edit(content=f"❌ Could not load KrakenFiles page. Status: {resp.status}")
                    return False, f"HTTP {resp.status}"
                html = await resp.text()

        soup = BeautifulSoup(html, 'html.parser')
        a = soup.find('a', {'id': 'downloadbtn'})
        if not a or not a.has_attr('href'):
            await msg.edit(content="❌ Could not find the download link on KrakenFiles page. (Login or timer may be required)")
            return False, "No download button"

        dl_url = a['href']
        await msg.edit(content="📥 Downloading file from KrakenFiles...")
        async with aiohttp.ClientSession() as session:
            async with session.get(dl_url) as resp:
                if resp.status != 200:
                    await msg.edit(content=f"❌ Failed to download file. Status: {resp.status}")
                    return False, f"HTTP {resp.status}"
                content = await resp.read()
                if len(content) > 25 * 1024 * 1024:
                    await msg.edit(content="❌ File too large for Discord (25 MB limit)")
                    return False, "File too large"
                filename = dl_url.split("/")[-1] or "krakenfiles.bin"
                await channel.send(file=discord.File(fp=bytearray(content), filename=filename))

        await msg.delete()
        return True, "Success"
    except Exception as e:
        await msg.edit(content=f"❌ KrakenFiles error: {e}")
        return False, str(e)


async def download_and_post_audio(url: str, channel: discord.TextChannel) -> tuple[bool, str]:
    """Download audio via yt-dlp (or custom scrapers) and post to *channel*."""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL format"
    except Exception:
        return False, "Invalid URL format"

    if "krakenfiles.com" in url:
        return await download_and_post_krakenfile(url, channel)
    if any(d in url for d in ["pillowcase.link", "pillowcase.su", "pillows.su"]):
        return await download_and_post_pillowcase(url, channel)

    msg = await channel.send(f"📥 Downloading audio from: {url}")
    temp_dir = tempfile.mkdtemp()
    temp_path = None

    try:
        await msg.edit(content="📥 Extracting audio...")
        output_template = os.path.join(temp_dir, 'audio.%(ext)s')
        cmd = await _build_yt_dlp_cmd(url, output_template, audio=True)
        code, err = await _run_yt_dlp(cmd)

        if code != 0:
            await msg.edit(content=f"❌ Download failed: {err[:200]}")
            return False, f"yt-dlp error: {err[:200]}"

        files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
        if not files:
            await msg.edit(content="❌ No file was downloaded.")
            return False, "No file downloaded"

        temp_path = os.path.join(temp_dir, files[0])
        file_size = os.path.getsize(temp_path)

        if file_size == 0:
            await msg.edit(content="❌ Downloaded file is empty.")
            return False, "Empty file"
        if file_size > 25 * 1024 * 1024:
            await msg.edit(content="❌ File is too large! Must be under 25 MB.")
            return False, "File too large"

        ext = os.path.splitext(temp_path)[1][1:] or 'mp3'
        await msg.edit(content=f"📤 Uploading audio... ({file_size / 1024:.1f} KB)")

        with open(temp_path, "rb") as f:
            await channel.send(file=discord.File(f, filename=f'audio.{ext}'))

        await msg.delete()
        return True, "Success"

    except FileNotFoundError:
        await msg.edit(content="❌ yt-dlp is not installed! Run: pip install yt-dlp")
        return False, "yt-dlp not found"
    except Exception as e:
        await msg.edit(content=f"❌ Error: {str(e)[:200]}")
        return False, str(e)
    finally:
        _cleanup_temp(temp_dir)


async def download_and_post_video(url: str, channel: discord.TextChannel) -> tuple[bool, str]:
    """Download video via yt-dlp and post to *channel*."""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL format"
    except Exception:
        return False, "Invalid URL format"

    msg = await channel.send(f"📥 Downloading video from: {url}")
    temp_dir = tempfile.mkdtemp()
    temp_path = None

    try:
        await msg.edit(content="📥 Downloading video...")
        output_template = os.path.join(temp_dir, 'video.%(ext)s')
        cmd = await _build_yt_dlp_cmd(url, output_template, audio=False)
        code, err = await _run_yt_dlp(cmd)

        if code != 0:
            await msg.edit(content=f"❌ Download failed: {err[:200]}")
            return False, f"yt-dlp error: {err[:200]}"

        files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
        if not files:
            await msg.edit(content="❌ No file was downloaded.")
            return False, "No file downloaded"

        temp_path = os.path.join(temp_dir, files[0])
        file_size = os.path.getsize(temp_path)

        if file_size == 0:
            await msg.edit(content="❌ Downloaded file is empty.")
            return False, "Empty file"
        if file_size > 25 * 1024 * 1024:
            await msg.edit(content="❌ File is too large! Must be under 25 MB.")
            return False, "File too large"

        ext = os.path.splitext(temp_path)[1][1:] or 'mp4'
        await msg.edit(content=f"📤 Uploading video... ({file_size / 1024:.1f} KB)")

        with open(temp_path, "rb") as f:
            await channel.send(file=discord.File(f, filename=f'video.{ext}'))

        await msg.delete()
        return True, "Success"

    except FileNotFoundError:
        await msg.edit(content="❌ yt-dlp is not installed! Run: pip install yt-dlp")
        return False, "yt-dlp not found"
    except Exception as e:
        await msg.edit(content=f"❌ Error: {str(e)[:200]}")
        return False, str(e)
    finally:
        _cleanup_temp(temp_dir)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _cleanup_temp(temp_dir: str):
    """Delete all files inside temp_dir then the directory itself."""
    if not temp_dir or not os.path.exists(temp_dir):
        return
    try:
        for f in os.listdir(temp_dir):
            try:
                os.unlink(os.path.join(temp_dir, f))
            except Exception:
                pass
        os.rmdir(temp_dir)
    except Exception:
        pass
