import subprocess
import shutil
import os
import logging
from pathlib import Path

# Màu sắc cho terminal
class Colors:
    BLACK = "\033[30m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    ORANGE = "\033[38;5;208m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def color_print(msg, color_code=""):
    print(f"{color_code}{msg}{Colors.RESET}")

def setup_logging(log_file):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def run(cmd, dry_run=False, msg=None):
    logger = logging.getLogger(__name__)
    if msg:
        logger.info(msg)
    
    if dry_run:
        color_print(f"[DRY-RUN] {cmd}", Colors.GREEN)
        return True
    
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="")
            logger.info(line.strip())
        process.wait()
        if process.returncode != 0:
            logger.error(f"Command failed: {cmd}")
            return False
        return True
    except Exception as e:
        logger.error(f"Error executing {cmd}: {e}")
        return False

def copy_configs(source_dir, target_dir, dry_run=False):
    """Copy configuration files with dry-run support."""
    source = Path(source_dir)
    target = Path(target_dir)
    
    if dry_run:
        color_print(f"[DRY-RUN] Would copy configs from {source} to {target}", Colors.GREEN)
        return True
    
    try:
        shutil.copytree(source / ".config", target / ".config", dirs_exist_ok=True)
        shutil.copytree(source / "Pictures", target / "Pictures", dirs_exist_ok=True)
        shutil.copy(source / ".zshrc", target / ".zshrc")
        return True
    except Exception as e:
        logging.error(f"Copy configs failed: {e}")
        return False
