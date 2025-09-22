"""Swap file management"""

from arch_installer.utils import run

class SwapManager:
    """Manage swap file creation and configuration"""
    
    @staticmethod
    def setup_swapfile(size_mb=2048):
        """Create and configure swap file"""
        # Create swap file
        run(f"dd if=/dev/zero of=/mnt/swapfile bs=1M count={size_mb} status=progress")
        run("chmod 600 /mnt/swapfile")
        run("mkswap /mnt/swapfile")
        
        # Add to fstab
        run("echo '/swapfile none swap defaults 0 0' >> /mnt/etc/fstab")
