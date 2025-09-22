# src/arch_installer/disk.py
import subprocess
import logging
import os

class DiskManager:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def _run(self, cmd: str):
        """Run a shell command (or just print if dry-run)."""
        logging.info(f"[disk] {cmd}")
        if self.dry_run:
            print(f"[DRY-RUN] {cmd}")
            return ""
        try:
            result = subprocess.run(
                cmd, shell=True, check=True, capture_output=True, text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed: {cmd} - {e.stderr}")
            raise

    # --- Disk listing ---
    def list_disks(self):
        """Return list of dicts: {name, size, type}"""
        out = self._run("lsblk -d -n -o NAME,SIZE,TYPE")
        disks = []
        for line in out.splitlines():
            parts = line.split()
            if len(parts) == 3:
                name, size, type_ = parts
                disks.append({"name": f"/dev/{name}", "size": size, "type": type_})
        return disks

    # --- Mount helpers ---
    def is_mounted(self, path: str) -> bool:
        return os.path.ismount(path)

    def unmount_path(self, path: str):
        if self.is_mounted(path):
            self._run(f"umount -f {path}")

    def unmount_disk(self, disk: str):
        """Unmount all mountpoints on a disk and its partitions."""
        out = self._run(f"lsblk -ln -o MOUNTPOINT {disk}")
        for mp in filter(None, out.splitlines()):
            self.unmount_path(mp)
        # force unmount any partition
        self._run(f"umount -f {disk}* 2>/dev/null || true")

    # --- Partitioning ---
    def wipe_disk(self, disk: str):
        self._run(f"wipefs -a {disk}")
        self._run(f"sgdisk -Z {disk}")
        self._run(f"sgdisk -o {disk}")

    def partition_disk(self, disk: str, layout: str = "default"):
        """
        Create partitions.
        layout: "default" => EFI + root
        """
        if layout == "default":
            self._run(f"sgdisk -n 1:0:+1G -t 1:ef00 {disk}")
            self._run(f"sgdisk -n 2:0:0 -t 2:8300 {disk}")
            return {
                "efi": f"{disk}1",
                "root": f"{disk}2",
            }
        else:
            raise ValueError(f"Unknown partition layout: {layout}")

