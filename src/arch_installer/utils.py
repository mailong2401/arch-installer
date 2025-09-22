"""Utility functions"""

import os
import subprocess
import logging

def run(cmd, check=True, capture_output=True):
    """Run a shell command with logging"""
    print(f"[RUN] {cmd}")
    logging.info(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                              capture_output=capture_output, text=True)
        if capture_output:
            return result.stdout
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {cmd} - Error: {e}")
        print(f"ERROR: {e.stderr}")
        raise

def safe_run(cmd):
    """Run a command but don't raise exception on failure"""
    try:
        return run(cmd, check=False)
    except Exception:
        return None

def check_efi():
    """Check if system uses UEFI"""
    return os.path.exists("/sys/firmware/efi")
