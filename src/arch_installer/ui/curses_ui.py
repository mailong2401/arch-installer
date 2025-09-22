import curses
from typing import List, Dict, Any

class CursesUI:
    def __init__(self):
        self.lang = "vi"
        self.messages = {
            "STEP_UPDATE": {"vi": "Đang cập nhật hệ thống...", "en": "Updating system..."},
            "STEP_COPY": {"vi": "Sao chép file cấu hình cá nhân...", "en": "Copying personal configuration files..."},
            # ... thêm các message khác
        }

    def get_message(self, key):
        return self.messages.get(key, {}).get(self.lang, key)

    def choose_language(self, stdscr):
        curses.curs_set(0)
        options = ["Tiếng Việt", "English"]
        index = 0

        while True:
            stdscr.clear()
            stdscr.addstr("Chọn ngôn ngữ / Choose language:\n\n")
            for i, option in enumerate(options):
                if i == index:
                    stdscr.addstr(f"> {option}\n", curses.A_REVERSE)
                else:
                    stdscr.addstr(f"  {option}\n")
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP:
                index = (index - 1) % len(options)
            elif key == curses.KEY_DOWN:
                index = (index + 1) % len(options)
            elif key in [curses.KEY_ENTER, 10, 13]:
                self.lang = "vi" if index == 0 else "en"
                return self.lang

    def show_progress_screen(self, stdscr, title, function, *args):
        """Hiển thị màn hình progress với hàm thực thi."""
        curses.start_color()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

        stdscr.clear()
        stdscr.addstr(f"[STEP] {title}\n", curses.A_BOLD)
        stdscr.refresh()
        
        return function(stdscr, *args)

    def wait_for_key(self, stdscr, message):
        stdscr.addstr(f"\n{message}")
        stdscr.refresh()
        stdscr.getch()
