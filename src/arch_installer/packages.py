"""Package management"""

import subprocess
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
        """Install base packages with progress display"""
        pkgs = self.get_package_list(kernel, gpu, wmde)
        ui.show_package_installation(pkgs)
        
        # Install packages using pacstrap
        for pkg in pkgs:
            cmd = f"pacstrap -K /mnt {pkg}"
            ui.update_package_status(pkg, "Installing...")
            
            try:
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, text=True, bufsize=1)
                
                # Simulate progress
                lines_seen = 0
                for line in process.stdout:
                    lines_seen += 1
                    ui.update_package_progress(pkg, lines_seen, 20)  # 20 lines per package as progress indicator
                
                process.wait()
                
                if process.returncode == 0:
                    ui.update_package_status(pkg, "✓ Installed")
                else:
                    ui.update_package_status(pkg, "✗ Failed")
                    raise Exception(f"Failed to install package: {pkg}")
                    
            except Exception as e:
                ui.update_package_status(pkg, "✗ Error")
                raise
