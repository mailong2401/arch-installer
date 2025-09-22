"""Utility functions"""

import os
import subprocess
import logging

def run(cmd, check=True, capture_output=True, silent=True):
    """Run a shell command with logging"""
    print(f"[RUN] {cmd}")
    logging.info(f"Running: {cmd}")
    try:
        # Nếu silent=True, chuyển hướng output để không làm hỏng curses
        if silent:
            result = subprocess.run(cmd, shell=True, check=check, 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, shell=True, check=check, 
                                  capture_output=capture_output, text=True)
        
        if capture_output and not silent:
            return result.stdout
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {cmd} - Error: {e}")
        if not silent:
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
