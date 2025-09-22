from typing import List
from arch_installer.utils import run

class PackageManager:
    BASE_PACKAGES = [
        "hyprland", "wofi", "waybar", "zsh", "python-pip", "npm", "nodejs", "ruby",
        "lsd", "ttf-jetbrains-mono-nerd", "brightnessctl", "swaybg", "iwd", 
        "wl-clipboard", "otf-comicshanns-nerd", "noto-fonts-cjk", "fcitx5", 
        "fcitx5-configtool", "fcitx5-gtk", "fcitx5-qt", "firefox", "fcitx5-unikey", 
        "fcitx5-hangul", "thunar", "thunar-archive-plugin", "grim", "slurp", 
        "xdg-desktop-portal-hyprland", "kitty"
    ]
    
    NEOVIM_DEPS = [
        "sudo npm install -g neovim",
        "gem install neovim", 
        "pip install --user neovim --break-system-packages"
    ]

    @classmethod
    def update_system(cls, dry_run=False):
        return run("sudo pacman -Syu --noconfirm", dry_run, "Updating system...")

    @classmethod
    def install_packages(cls, packages: List[str], dry_run=False):
        pkg_list = " ".join(packages)
        return run(f"sudo pacman -S --needed --noconfirm {pkg_list}", dry_run, f"Installing {len(packages)} packages...")

    @classmethod
    def install_oh_my_zsh(cls, dry_run=False):
        cmd = 'export RUNZSH=yes; export CHSH=no; yes | sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"'
        return run(cmd, dry_run, "Installing Oh My Zsh...")

    @classmethod
    def install_zsh_plugin(cls, name: str, url: str, dry_run=False):
        dest = f"~/.oh-my-zsh/custom/plugins/{name}"
        return run(f"git clone {url} {dest}", dry_run, f"Installing Zsh plugin: {name}")
