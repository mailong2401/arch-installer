"""Progress bar utilities"""

import curses

class ProgressBar:
    """Simple progress bar for curses"""
    
    @staticmethod
    def draw(stdscr, y, x, width, progress, label=""):
        """Draw a progress bar"""
        filled = int(width * progress)
        bar = "█" * filled + " " * (width - filled)
        percent = int(progress * 100)
        
        try:
            stdscr.addstr(y, x, f"{label} [{bar}] {percent}%")
        except curses.error:
            pass

class Spinner:
    """Simple spinner for indeterminate progress"""
    
    def __init__(self):
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.current = 0
    
    def next(self):
        """Get next spinner frame"""
        frame = self.frames[self.current]
        self.current = (self.current + 1) % len(self.frames)
        return frame
