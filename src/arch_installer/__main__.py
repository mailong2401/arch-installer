# src/arch_installer/__main__.py

import argparse
import logging
import os
import sys

from arch_installer import installer
from arch_installer.ui.curses_ui import CursesUI


def main():
    # ---- CLI ----
    parser = argparse.ArgumentParser(description="Arch Installer")
    parser.add_argument(
        "--noninteractive",
        action="store_true",
        help="Run in non-interactive mode using config file",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to YAML config file (required in non-interactive mode)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do everything except making actual changes",
    )
    args = parser.parse_args()

    # ---- Logging ----
    log_file = "arch_installer.log"
    logging.basicConfig(
        filename=log_file,
        filemode="w",
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logging.info("Arch Installer started")

    # ---- Environment setup ----
    os.environ["INSTALLER_MODE"] = (
        "noninteractive" if args.noninteractive else "interactive"
    )
    if args.dry_run:
        os.environ["DRY_RUN"] = "1"

    # ---- Run mode ----
    if args.noninteractive:
        if not args.config:
            logging.error("--config is required in non-interactive mode")
            sys.exit(1)
        logging.info("Running non-interactive install with config %s", args.config)
        installer.run_from_config(args.config, dry_run=args.dry_run)
    else:
        logging.info("Running interactive installer")
        try:
            with CursesUI() as ui:
                installer.run_interactive(ui, dry_run=args.dry_run)
        except Exception as e:
            logging.exception("Interactive installer failed: %s", e)
            sys.exit(1)

    logging.info("Arch Installer finished successfully")


if __name__ == "__main__":
    main()

