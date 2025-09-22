"""Curses-based user interface"""

import curses
from arch_installer.ui.progress import ProgressBar

class CursesUI:
    """Curses-based user interface handler"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self._init_colors()
        curses.curs_set(0)  # Hide cursor by default
    
    def _init_colors(self):
        """Initialize color pairs"""
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)   # title
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)   # highlight
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # success
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # error
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # warning
    
    def menu(self, title, options, config, keyname):
        """Display a menu and return selected option"""
        curses.curs_set(0)
        h, w = self.stdscr.getmaxyx()
        current = 0

        while True:
            self.stdscr.clear()
            self.stdscr.attron(curses.color_pair(1))
            self.stdscr.addstr(0, 2, f"[ {title} ]")
            self.stdscr.attroff(curses.color_pair(1))

            # Display options
            for idx, option in enumerate(options):
                x = 2
                y = h//2 - len(options)//2 + idx
                if 0 <= y < h-1:
                    if idx == current:
                        self.stdscr.attron(curses.color_pair(2))
                        self.stdscr.addstr(y, x, f"> {option}")
                        self.stdscr.attroff(curses.color_pair(2))
                    else:
                        self.stdscr.addstr(y, x, f"  {option}")

            self._draw_summary(config)

            key = self.stdscr.getch()
            if key == curses.KEY_UP and current > 0:
                current -= 1
            elif key == curses.KEY_DOWN and current < len(options)-1:
                current += 1
            elif key in [curses.KEY_ENTER, 10, 13]:
                config[keyname] = options[current]
                return options[current]
            elif key == 27:  # ESC key
                raise SystemExit("Installation cancelled")
    
    def input(self, prompt, config, keyname, hidden=False, default=""):
        """Get input from user"""
        curses.curs_set(1)  # Show cursor
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        self.stdscr.addstr(0, 2, prompt)
        if default:
            self.stdscr.addstr(1, 2, f"(Default: {default})")
        
        self.stdscr.refresh()
        
        inp = default
        cursor_pos = len(inp)
        
        while True:
            self.stdscr.move(2, 2)
            self.stdscr.clrtobot()
            if hidden:
                self.stdscr.addstr(2, 2, "*" * len(inp))
            else:
                self.stdscr.addstr(2, 2, inp)
            
            # Show cursor position
            self.stdscr.move(2, 2 + cursor_pos)
            self.stdscr.refresh()
            
            ch = self.stdscr.getch()
            if ch in [curses.KEY_ENTER, 10, 13]:
                break
            elif ch in [curses.KEY_BACKSPACE, 127, 8]:
                if cursor_pos > 0:
                    inp = inp[:cursor_pos-1] + inp[cursor_pos:]
                    cursor_pos -= 1
            elif ch == curses.KEY_LEFT:
                cursor_pos = max(0, cursor_pos - 1)
            elif ch == curses.KEY_RIGHT:
                cursor_pos = min(len(inp), cursor_pos + 1)
            elif ch == 27:  # ESC key
                raise SystemExit("Installation cancelled")
            elif ch in [curses.KEY_HOME, 1]:  # Home key or Ctrl+A
                cursor_pos = 0
            elif ch in [curses.KEY_END, 5]:  # End key or Ctrl+E
                cursor_pos = len(inp)
            elif ch in [21, 11]:  # Ctrl+U or Ctrl+K
                inp = ""
                cursor_pos = 0
            elif 32 <= ch <= 126:  # Printable characters
                inp = inp[:cursor_pos] + chr(ch) + inp[cursor_pos:]
                cursor_pos += 1
        
        curses.curs_set(0)  # Hide cursor
        config[keyname] = inp.strip()
        return inp.strip()
    
    def _draw_summary(self, config):
        """Draw configuration summary"""
        h, w = self.stdscr.getmaxyx()
        x = w//2 + 2
        self.stdscr.attron(curses.color_pair(2))
        self.stdscr.addstr(0, x, " SELECTED CONFIGURATION ")
        self.stdscr.attroff(curses.color_pair(2))
        
        y = 2
        for key, value in config.items():
            if y < h-1:
                # Show max 2 lines per value
                if len(str(value)) > w - x - 10:
                    value_str = str(value)[:w - x - 13] + "..."
                else:
                    value_str = str(value)
                self.stdscr.addstr(y, x, f"{key}: {value_str}")
            y += 1
    
    def confirm_installation(self, config):
        """Show final confirmation before installation"""
        self.stdscr.clear()
        self.stdscr.addstr(0, 2, "INSTALLATION SUMMARY", curses.A_BOLD)
        
        y = 2
        for k, v in config.items():
            if y < curses.LINES-1:
                self.stdscr.addstr(y, 2, f"{k}: {v}")
            y += 1
        
        self.stdscr.addstr(y+2, 2, "Press Enter to start installation, ESC to cancel...")
        self.stdscr.refresh()
        
        key = self.stdscr.getch()
        return key not in [27]  # Not ESC
    
    def show_step(self, message):
        """Show current installation step"""
        self.stdscr.clear()
        self.stdscr.addstr(0, 2, f"STEP: {message}", curses.A_BOLD)
        self.stdscr.refresh()
    
    def show_error(self, message):
        """Show error message"""
        self.stdscr.clear()
        self.stdscr.attron(curses.color_pair(4))
        self.stdscr.addstr(0, 2, f"ERROR: {message}")
        self.stdscr.attroff(curses.color_pair(4))
        self.stdscr.addstr(2, 2, "Press any key to continue...")
        self.stdscr.refresh()
        self.stdscr.getch()
    
    def show_success(self, message):
        """Show success message"""
        self.stdscr.clear()
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.addstr(0, 2, f"SUCCESS: {message}")
        self.stdscr.attroff(curses.color_pair(3))
        self.stdscr.refresh()
    
    def prompt_reboot(self):
        """Prompt for reboot"""
        self.stdscr.addstr(2, 2, "Press Enter to reboot or ESC to skip reboot...")
        self.stdscr.refresh()
        
        key = self.stdscr.getch()
        return key not in [27]  # Not ESC
    
    def show_package_installation(self, packages):
        """Simple wrapper to show package installation start"""
        self.stdscr.clear()
        self.stdscr.addstr(0, 2, "PREPARING PACKAGE INSTALLATION...", curses.A_BOLD)
        self.stdscr.refresh()
    
    def update_package_status(self, package, status):
        """Update status for a specific package"""
        # Find package index (simplified - in real implementation would track indices)
        pass
    
    def update_package_progress(self, package, current, total):
        """Update progress for a specific package"""
        # Update progress bar for package (simplified)
        pass
