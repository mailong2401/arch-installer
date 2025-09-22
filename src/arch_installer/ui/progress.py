def create_progress_bar(width, progress):
    """Tạo progress bar dạng text."""
    filled = int(width * progress)
    empty = width - filled
    return "█" * filled + " " * empty

def update_progress(stdscr, y, x, width, progress, status=""):
    """Cập nhật progress bar trên màn hình curses."""
    bar = create_progress_bar(width, progress)
    percent = int(progress * 100)
    stdscr.addstr(y, x, f"[{bar}] {percent}% {status}")
    stdscr.refresh()
