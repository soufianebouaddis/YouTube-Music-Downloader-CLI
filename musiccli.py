#!/usr/bin/env python3
"""
Stylish YouTube Music Downloader CLI with Queue & Multi-threading
"""

import os
import sys
import threading
from pathlib import Path
from queue import Queue
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.prompt import Prompt
from rich import box
from rich.layout import Layout
from rich.text import Text
import yt_dlp
from datetime import datetime

console = Console()

# Global queue and download tracking
download_queue = Queue()
active_downloads = {}
completed_downloads = []
failed_downloads = []
queue_lock = threading.Lock()

def create_music_folder():
    """Create music folder if it doesn't exist"""
    music_dir = Path("music")
    music_dir.mkdir(exist_ok=True)
    return music_dir

def show_banner():
    """Display welcome banner"""
    banner = """
    ♪ YouTube Music Downloader ♪
    Multi-threaded Queue System
    """
    console.print(Panel(
        banner,
        style="bold cyan",
        box=box.DOUBLE,
        border_style="bright_magenta"
    ))

def create_status_table():
    """Create a status table showing queue and downloads"""
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Status", style="cyan", width=12)
    table.add_column("Title", style="white", width=50)
    table.add_column("Progress", style="green", width=20)
    
    # Show active downloads
    with queue_lock:
        for url, info in active_downloads.items():
            title = info.get('title', 'Fetching info...')[:47] + "..."
            progress = info.get('progress', '0%')
            table.add_row("⬇️ Downloading", title, progress)
        
        # Show queued items
        queue_size = download_queue.qsize()
        if queue_size > 0:
            table.add_row("⏳ In Queue", f"{queue_size} video(s) waiting", "-")
        
        # Show last 3 completed
        for item in completed_downloads[-3:]:
            table.add_row("✓ Completed", item[:47] + "...", "100%")
        
        # Show last 3 failed
        for item in failed_downloads[-3:]:
            table.add_row("✗ Failed", item[:47] + "...", "Error")
    
    return table

def download_worker(music_dir, worker_id):
    """Worker thread that processes downloads from queue"""
    while True:
        url = download_queue.get()
        if url is None:  # Poison pill to stop worker
            break
        
        try:
            # Add to active downloads
            with queue_lock:
                active_downloads[url] = {'title': 'Fetching info...', 'progress': '0%'}
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': str(music_dir / '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
            }
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    percent = d.get('_percent_str', '0%')
                    with queue_lock:
                        if url in active_downloads:
                            active_downloads[url]['progress'] = percent
                elif d['status'] == 'finished':
                    with queue_lock:
                        if url in active_downloads:
                            active_downloads[url]['progress'] = '100%'
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                
                # Update title
                with queue_lock:
                    if url in active_downloads:
                        active_downloads[url]['title'] = title
                
                # Download
                ydl.download([url])
            
            # Mark as completed
            with queue_lock:
                if url in active_downloads:
                    del active_downloads[url]
                completed_downloads.append(title)
            
        except Exception as e:
            error_msg = str(e)[:50]
            with queue_lock:
                if url in active_downloads:
                    title = active_downloads[url].get('title', url[:50])
                    del active_downloads[url]
                    failed_downloads.append(f"{title} - {error_msg}")
        
        finally:
            download_queue.task_done()

def main():
    """Main CLI loop"""
    console.clear()
    show_banner()
    
    # Create music directory
    music_dir = create_music_folder()
    console.print(f"[dim]Music will be saved to: {music_dir.absolute()}[/dim]")
    console.print(f"[dim]Using 3 concurrent download threads[/dim]\n")
    
    # Start worker threads
    num_workers = 3
    workers = []
    for i in range(num_workers):
        t = threading.Thread(target=download_worker, args=(music_dir, i), daemon=True)
        t.start()
        workers.append(t)
    
    # Start status display thread
    def status_display():
        with Live(create_status_table(), refresh_per_second=2, console=console) as live:
            while not stop_display.is_set():
                live.update(create_status_table())
                stop_display.wait(0.5)
    
    stop_display = threading.Event()
    status_thread = threading.Thread(target=status_display, daemon=True)
    status_thread.start()
    
    try:
        console.print("\n[yellow]Commands:[/yellow]")
        console.print("[yellow]  - Paste YouTube URL to add to queue[/yellow]")
        console.print("[yellow]  - 'q' to quit[/yellow]")
        console.print("[yellow]  - 's' to show status[/yellow]\n")
        
        while True:
            # Prompt for URL
            url = Prompt.ask("[bold cyan]Enter URL (or command)[/bold cyan]")
            
            # Check for quit command
            if url.lower() == 'q':
                console.print("\n[bold yellow]Waiting for downloads to complete...[/bold yellow]")
                download_queue.join()  # Wait for all tasks to complete
                stop_display.set()
                
                # Stop workers
                for _ in workers:
                    download_queue.put(None)
                for t in workers:
                    t.join()
                
                console.print("\n[bold magenta]👋 Goodbye![/bold magenta]\n")
                console.print(f"[green]✓ Completed: {len(completed_downloads)}[/green]")
                console.print(f"[red]✗ Failed: {len(failed_downloads)}[/red]\n")
                break
            
            # Show status command
            if url.lower() == 's':
                console.print()
                continue
            
            # Validate URL
            if not url.strip():
                console.print("[red]Please enter a valid URL[/red]")
                continue
            
            if 'youtube.com' not in url and 'youtu.be' not in url:
                console.print("[red]Please enter a valid YouTube URL[/red]")
                continue
            
            # Add to queue
            download_queue.put(url)
            console.print(f"[green]✓[/green] Added to queue (Queue size: {download_queue.qsize()})\n")
    
    except KeyboardInterrupt:
        stop_display.set()
        console.print("\n\n[bold magenta]👋 Goodbye![/bold magenta]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold magenta]👋 Goodbye![/bold magenta]\n")
        sys.exit(0)