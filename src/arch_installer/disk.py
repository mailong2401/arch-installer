"""Disk management functions"""

import os
import subprocess
from arch_installer.utils import run, safe_run

class DiskManager:
    """Manage disk operations"""
    
    @staticmethod
    def list_disks():
        """List available disks"""
        out = subprocess.check_output("lsblk -d -n -o NAME,SIZE,TYPE", shell=True, text=True)
        disks = []
        for line in out.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 3 and parts[2] == "disk":
                name, size = parts[0], parts[1]
                disks.append(f"/dev/{name} ({size})")
        return disks

    @staticmethod
    def is_disk_mounted(disk):
        """Check if disk is mounted"""
        try:
            result = subprocess.run(f"mount | grep {disk}", shell=True, 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    @staticmethod
    def unmount_disk(disk):
        """Unmount disk and its partitions"""
        # Unmount partitions
        try:
            result = subprocess.run(f"lsblk -ln -o MOUNTPOINTS {disk} | grep -v '^$'", 
                                  shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                mount_points = result.stdout.strip().split('\n')
                for mount_point in mount_points:
                    if mount_point:
                        safe_run(f"umount -f {mount_point}")
        except:
            pass
        
        # Try to unmount main disk
        safe_run(f"umount -f {disk}* 2>/dev/null || true")

    @staticmethod
    def partition_disk(disk):
        """Partition disk with EFI and root partitions"""
        run(f"wipefs -a {disk}")
        run(f"sgdisk -Z {disk}")
        run(f"sgdisk -o {disk}")
        run(f"sgdisk -n 1:0:+1G -t 1:ef00 {disk}")
        run(f"sgdisk -n 2:0:0 -t 2:8300 {disk}")
        
        return f"{disk}1", f"{disk}2"

    @staticmethod
    def format_and_mount(efi_partition, root_partition):
        """Format partitions and mount them"""
        run(f"mkfs.fat -F32 {efi_partition}")
        run(f"mkfs.ext4 -F {root_partition}")
        run(f"mount {root_partition} /mnt")
        run("mkdir -p /mnt/boot")
        run(f"mount {efi_partition} /mnt/boot")
