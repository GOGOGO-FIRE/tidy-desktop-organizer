import typer
import os
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime

app = typer.Typer()
console = Console()

# -- CONFIGURATION: FIle Categories ---
FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".ppt", ".xlsx", ".xls", ".csv", ".md"],
    "Videos": [".mp4", ".mkv", ".flv", ".avi", ".mov", ".wmv"],
    "Music": [".mp3", ".wav", ".aac", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Programs": [".exe", ".msi", ".dmg", ".pkg", ".deb"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".json"]
}

def get_unique_filename(destination_folder, filename):
    """
    Prevent overwriting files. If 'photo.jpg' exists, returns 'photo_1.jpg'.
    """
    base, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    while os.path.exists(os.path.join(destination_folder, new_filename)):
        new_filename = f"{base}_{counter}{extension}"
        counter += 1

    return new_filename

@app.command()
def organize(folder_path: str):
    """
    Clean up a messy folder by sorting files into categories.
    Usage: python tidy-desktop.py organize "C:/Users/You/Downloads"
    """
    # Validate Path
    if not os.path.exists(folder_path):
        console.print(f"[bold red]❌ Error: Path '{folder_path}' does not exist![/bold red]")
        return

    # Statistics
    stats = {cat: 0 for cat in FILE_CATEGORIES}
    stats["Others"] = 0
    moved_count = 0

    console.print(Panel(f"[bold cyan]🧹 TIDY-DESKTOP IS RUNNING...[/bold cyan]\nTarget: {folder_path}", title="File Organizer"))

    with console.status("[bold yellow]Scanning and moving files...[/bold yellow]", spinner="bouncingBar"):
        
        # Scan all files in the directory
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Skip folders (we only organize files)
            if os.path.isdir(file_path):
                continue
            
            # Skip the script itself if it's in the folder
            if filename == os.path.basename(__file__):
                continue

            file_ext = os.path.splitext(filename)[1].lower()
            destination_category = "Others" # Default category

            # Determine category based on extension
            for category, extensions in FILE_CATEGORIES.items():
                if file_ext in extensions:
                    destination_category = category
                    break
            
            # Create Category Folder (e.g., "Downloads/Images")
            dest_folder_path = os.path.join(folder_path, destination_category)
            os.makedirs(dest_folder_path, exist_ok=True)

            # Handle Duplicate Names
            safe_filename = get_unique_filename(dest_folder_path, filename)
            
            # Move File
            try:
                shutil.move(file_path, os.path.join(dest_folder_path, safe_filename))
                stats[destination_category] += 1
                moved_count += 1
            except Exception as e:
                console.print(f"[red]Failed to move {filename}: {e}[/red]")

    # --- REPORTING ---
    table = Table(title="📊 Organization Report", style="green")
    table.add_column("Category", style="cyan")
    table.add_column("Files Moved", justify="right", style="bold white")

    for cat, count in stats.items():
        if count > 0:
            table.add_row(cat, str(count))

    console.print("\n")
    console.print(table)
    console.print(f"\n[bold green]✅ DONE! Successfully organized {moved_count} files.[/bold green]")
    console.print(f"[dim]Log time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]")

if __name__ == "__main__":
    app()