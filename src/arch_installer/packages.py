"""Package management"""

import subprocess
import curses
from arch_installer.utils import run

class PackageManager:
    """Manage package installation"""
    
    @staticmethod
    def optimize_mirrorlist():
        """Optimize pacman mirrorlist"""
        run("pacman -S --noconfirm reflector")
        run("reflector --country Vietnam --age 12 --protocol https --sort rate --save /etc/pacman.d/mirrorlist")
    
    @staticmethod
    def get_package_list(kernel, gpu, wmde):
        """Build package list based on configuration"""
        pkgs = ["base", kernel, f"{kernel}-headers", "networkmanager", "sudo"]
        
        # GPU drivers
        if gpu == "nvidia":
            pkgs += ["nvidia-dkms", "nvidia-utils", "nvidia-settings"]
        elif gpu == "amd":
            pkgs += ["xf86-video-amdgpu", "mesa", "vulkan-radeon"]
        elif gpu == "intel":
            pkgs += ["mesa", "vulkan-intel", "xf86-video-intel"]
        
        # WM/DE packages
        if wmde == "bspwm":
            pkgs += ["bspwm", "sxhkd", "alacritty", "polybar", "xorg", "xorg-xinit"]
        elif wmde == "hyprland":
            pkgs += ["hyprland", "waybar", "alacritty", "xdg-desktop-portal-hyprland"]
        elif wmde == "gnome":
            pkgs += ["gnome", "gdm"]
        elif wmde == "kde":
            pkgs += ["plasma", "sddm", "konsole"]
        
        return pkgs
    
    def install_base_packages(self, ui, kernel, gpu, wmde):
        """Install base packages with progress display - fixed version"""
        pkgs = self.get_package_list(kernel, gpu, wmde)
        
        # Initialize UI for package installation
        stdscr = ui.stdscr  # Get the curses window
        
        curses.start_color()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

        stdscr.clear()
        stdscr.addstr("[STEP] Installing base packages...\n", curses.A_BOLD)
        stdscr.refresh()

        h, w = stdscr.getmaxyx()
        left_col_w = 30
        right_col_w = w - left_col_w - 2

        # Draw separator column
        for i in range(h-1):
            try:
                stdscr.addstr(i, left_col_w + 2, "│")
            except curses.error:
                pass
        
        try:
            stdscr.addstr(h-1, 0, "─" * (w-1))
        except curses.error:
            pass

        # Show package names in left column
        for i, pkg in enumerate(pkgs):
            if i + 2 < h-1:
                try:
                    stdscr.addstr(i+2, 2, pkg[:left_col_w-2])
                except curses.error:
                    pass
        stdscr.refresh()

        # Install each package
        for i, pkg in enumerate(pkgs):
            if i + 2 >= h-1:
                break

            cmd = f"pacstrap -K /mnt {pkg}"
            
            # Clear status area and show starting message
            try:
                stdscr.addstr(i+2, left_col_w+4, " " * (right_col_w-4))
                stdscr.addstr(i+2, left_col_w+4, "Starting...", curses.color_pair(1))
                stdscr.refresh()
            except curses.error:
                pass

            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                     stderr=subprocess.STDOUT, text=True, bufsize=1)

            # Simulate progress bar
            progress_width = 20
            lines_seen = 0
            
            # Read output in real-time and update progress
            for line in process.stdout:
                line = line.strip()
                lines_seen += 1
                done = min(progress_width, lines_seen)
                bar = "█" * done + " " * (progress_width - done)
                percent = int(done / progress_width * 100)
                
                try:
                    stdscr.addstr(i+2, left_col_w+4, " " * (right_col_w-4))
                    stdscr.addstr(i+2, left_col_w+4, f"[{bar}] {percent}%".ljust(right_col_w-4), curses.color_pair(1))
                    stdscr.refresh()
                except curses.error:
                    pass

            # Process has finished at this point, no need for wait()
            # Get the return code
            returncode = process.poll()
            if returncode is None:
                # Process is still running (shouldn't happen with our loop)
                process.wait()
                returncode = process.returncode

            # Show final status
            if returncode == 0:
                final_status = "✓ Installed successfully"
                color = curses.color_pair(2)
            else:
                final_status = "✗ Installation failed"
                color = curses.color_pair(3)
            
            try:
                stdscr.addstr(i+2, left_col_w+4, " " * (right_col_w-4))
                stdscr.addstr(i+2, left_col_w+4, final_status[:right_col_w-4], color)
                stdscr.refresh()
            except curses.error:
                pass
            
            # If installation failed, raise exception
            if returncode != 0:
                raise Exception(f"Failed to install package: {pkg}")

        # Show completion message
        try:
            msg = "Installation completed."
            stdscr.addstr(h-1, 2, msg[:w-3])
            stdscr.refresh()
        except curses.error:
            pass
