#!/usr/bin/env python3
"""Main entry point for arch-installer"""

import curses
from arch_installer.installer import Installer

def main():
    """Main function"""
    try:
        curses.wrapper(lambda stdscr: Installer(stdscr).run())
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user.")
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
