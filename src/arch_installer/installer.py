import curses
from arch_installer.ui.curses_ui import CursesUI
from arch_installer.packages import PackageManager
from arch_installer.utils import copy_configs, run

class ArchInstaller:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.ui = CursesUI()
        self.script_dir = Path(__file__).parent.parent.parent
        self.home_dir = Path.home()

    def run(self):
        """Chạy toàn bộ quá trình cài đặt."""
        curses.wrapper(self._main_flow)

    def _main_flow(self, stdscr):
        # Bước 1: Chọn ngôn ngữ
        self.ui.choose_language(stdscr)
        
        # Bước 2: Cập nhật hệ thống
        self.ui.show_progress_screen(stdscr, 
            self.ui.get_message("STEP_UPDATE"),
            self._update_system_curses
        )
        
        # Bước 3: Cài đặt packages
        self.ui.show_progress_screen(stdscr,
            self.ui.get_message("STEP_INSTALL_PACKAGES"), 
            self._install_packages_curses
        )
        
        # ... các bước tiếp theo

    def _update_system_curses(self, stdscr):
        # Triển khai giao diện curses cho update system
        pass
        
    def _install_packages_curses(self, stdscr):
        # Triển khai giao diện curses cho install packages
        pass
        
    # ... các phương thức curses khác
