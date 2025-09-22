# Arch Linux Installer

A professional Arch Linux installer with curses-based UI.

## Features

- Interactive curses-based interface
- Automatic disk partitioning
- Multiple kernel support (linux, linux-lts, linux-zen)
- GPU driver selection (Intel, AMD, NVIDIA)
- Desktop environment/WM selection (GNOME, KDE, bspwm, Hyprland)
- Bootloader support (systemd-boot, GRUB)
- Locale configuration
- Swap file setup
- Microcode detection and installation

## Installation

```bash
git clone https://github.com/yourusername/arch-installer.git
cd arch-installer
pip install -e .
