# YouTube Music Downloader (CLI)

A beautiful, fast, and efficient command-line tool to download music from YouTube with queue management and multi-threaded downloads.

Features

- 🎨 Stylish CLI interface with colorful, real-time updates
- ⚡ Multi-threaded downloads (default: up to 3 concurrent downloads)
- 📋 Queue system — add multiple URLs while downloads run
- 📊 Live progress tracking and queue status
- 🎧 High-quality audio — downloads best available audio and converts to MP3 (192 kbps)
- 📁 Organized storage — saves music to the `music/` folder by default
- 🛡️ Robust error handling — failed downloads are reported, workers keep processing the queue

Quick start
---------------

Prerequisites

- Python 3.8 or higher
- FFmpeg (used for audio conversion)

Install FFmpeg

- macOS (Homebrew):

```bash
brew install ffmpeg
```

- Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ffmpeg
```

- Windows (chocolatey):

```powershell
choco install ffmpeg
```

Installation
----------------

Clone the repository:

```bash
git clone https://github.com/soufianebouaddis/YouTube-Music-Downloader-CLI.git
cd YouTube-Music-Downloader-CLI
```

Create and activate a Python virtual environment, install dependencies, and run the app. There's a helper script included called `setupAndRun.sh`.

macOS / Linux (zsh / bash):

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install yt-dlp rich
python3 musiccli.py
```

Or run the provided helper script:

```bash
./setupAndRun.sh
```

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\activate
pip install yt-dlp rich
python musiccli.py
```

What it does
-------------

- Downloads the best available audio stream from YouTube videos using `yt-dlp`.
- Converts audio to MP3 (192 kbps) using FFmpeg.
- Saves files into the `music/` folder (creates it if missing) with the video title as filename.
- Uses a thread-safe queue and up to 3 simultaneous worker threads for concurrent downloads.
- Provides a colorful, real-time status table via `rich` that shows currently downloading items, queue length, and completed items.

Usage
------

When running `musiccli.py`:

- Paste a YouTube URL and press Enter to add it to the queue.
- Press `s` and Enter to show the current status table (downloaders, queued items, completed).
- Press `q` and Enter to quit the CLI — active downloads will finish before the program exits.

Example session

1. Start the program (`python3 musiccli.py`).
2. Paste a URL and press Enter. That item appears in the queue immediately.
3. While downloads run, paste more URLs to queue them.

Files & storage
-----------------

- Default downloads directory: `./music/` (inside repository root). You can move or change this in the source if you want a different path.
- File names are derived from the video title returned by YouTube/yt-dlp. Be aware of filesystem restrictions on characters.

Troubleshooting
-----------------

- If downloads fail with an error about `yt-dlp`, make sure `yt-dlp` is installed in the same Python environment: `pip install yt-dlp`.
- If audio conversion fails, verify FFmpeg is installed and available on PATH (`ffmpeg -version`).
- If filenames contain illegal characters, the program attempts to sanitize them, but you may need to manually rename files in rare cases.