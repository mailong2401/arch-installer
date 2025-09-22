import curses
from typing import List, Optional, TextIO


class CursesUI:
    def __init__(self, stdscr=None):
        """
        Nếu stdscr = None → dùng context manager (__enter__/__exit__).
        Nếu stdscr != None → giả sử đang chạy trong curses.wrapper().
        """
        self.stdscr = stdscr
        self._own_screen = False

    def __enter__(self):
        if self.stdscr is None:
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            self._own_screen = True
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)   # titles
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)   # highlight
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # success
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # error
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._own_screen:
            self.stdscr.keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()

    # --- Helpers ---
    def _draw_centered(self, y: int, text: str, attr=0):
        h, w = self.stdscr.getmaxyx()
        x = (w - len(text)) // 2
        if x < 0:
            x = 0
        self.stdscr.addstr(y, x, text, attr)

    # --- API methods ---
    def select(self, prompt: str, options: List[str]) -> str:
        current = 0
        while True:
            self.stdscr.clear()
            self._draw_centered(0, prompt, curses.color_pair(1) | curses.A_BOLD)
            for i, opt in enumerate(options):
                y = 2 + i
                if i == current:
                    self._draw_centered(y, f"> {opt}", curses.color_pair(2))
                else:
                    self._draw_centered(y, f"  {opt}")
            key = self.stdscr.getch()
            if key in [curses.KEY_UP, ord("k")]:
                current = (current - 1) % len(options)
            elif key in [curses.KEY_DOWN, ord("j")]:
                current = (current + 1) % len(options)
            elif key in [10, 13, curses.KEY_ENTER]:
                return options[current]
            elif key == 27:  # ESC
                raise SystemExit("User aborted")

    def input(
        self, prompt: str, hidden: bool = False, default: Optional[str] = None
    ) -> str:
        curses.curs_set(1)
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, prompt, curses.color_pair(1))
        if default:
            self.stdscr.addstr(1, 0, f"(Default: {default})")
        inp = list(default or "")
        cursor = len(inp)
        while True:
            self.stdscr.move(3, 0)
            self.stdscr.clrtoeol()
            display = "*" * len(inp) if hidden else "".join(inp)
            self.stdscr.addstr(3, 0, display)
            self.stdscr.move(3, cursor)
            self.stdscr.refresh()
            ch = self.stdscr.getch()
            if ch in [10, 13]:
                break
            elif ch in (curses.KEY_BACKSPACE, 127, 8):
                if cursor > 0:
                    inp.pop(cursor - 1)
                    cursor -= 1
            elif ch == curses.KEY_LEFT:
                cursor = max(0, cursor - 1)
            elif ch == curses.KEY_RIGHT:
                cursor = min(len(inp), cursor + 1)
            elif ch == 27:  # ESC
                raise SystemExit("User aborted")
            elif 32 <= ch <= 126:
                inp.insert(cursor, chr(ch))
                cursor += 1
        curses.curs_set(0)
        return "".join(inp).strip() or (default or "")

    def show_progress(self, stream: TextIO, label: str):
        self.stdscr.clear()
        self._draw_centered(0, label, curses.color_pair(1) | curses.A_BOLD)
        y = 2
        for line in stream:
            self.stdscr.addstr(y, 0, line[: curses.COLS - 1])
            y += 1
            if y >= curses.LINES - 1:
                y = 2
                self.stdscr.clear()
                self._draw_centered(0, label, curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.refresh()

    def confirm(self, summary: str) -> bool:
        options = ["Yes", "No"]
        choice = self.select(summary, options)
        return choice == "Yes"


# --- entry for curses.wrapper ---
def run_ui(func, *args, **kwargs):
    def wrapped(stdscr):
        with CursesUI(stdscr) as ui:
            return func(ui, *args, **kwargs)

    return curses.wrapper(wrapped)

