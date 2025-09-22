#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from arch_installer.installer import ArchInstaller
from arch_installer.utils import setup_logging

def main():
    parser = argparse.ArgumentParser(description="Arch Linux installer")
    parser.add_argument("--dry-run", action="store_true", help="Test mode without actual changes")
    parser.add_argument("--log-file", default="install.log", help="Log file path")
    args = parser.parse_args()
    
    setup_logging(args.log_file)
    installer = ArchInstaller(dry_run=args.dry_run)
    installer.run()

if __name__ == "__main__":
    main()
