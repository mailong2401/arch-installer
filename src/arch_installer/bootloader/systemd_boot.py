"""systemd-boot configuration"""

from arch_installer.utils import run
from arch_installer.microcode import MicrocodeManager

class SystemdBoot:
    """systemd-boot bootloader manager"""
    
    def install(self, root_partition, kernel, gpu, microcode_file=None):
        """Install and configure systemd-boot"""
        run("arch-chroot /mnt bootctl install")
        
        # Create loader.conf
        loader_conf = """default arch.conf
timeout 3
console-mode keep
editor no
"""
        with open("/mnt/boot/loader/loader.conf", "w") as f:
            f.write(loader_conf)
        
        # Add microcode if available
        microcode_initrd = ""
        if microcode_file:
            microcode_initrd = f"initrd /{microcode_file}\n"
        
        # Create main Arch Linux entry
        options = f"root={root_partition} rw quiet"
        if gpu == "nvidia":
            options += " nvidia-drm.modeset=1"
        
        arch_entry = f"""title Arch Linux ({kernel})
linux /vmlinuz-{kernel}
{microcode_initrd}initrd /initramfs-{kernel}.img
options {options}
"""
        import os
        os.makedirs("/mnt/boot/loader/entries", exist_ok=True)
        with open("/mnt/boot/loader/entries/arch.conf", "w") as f:
            f.write(arch_entry)
        
        # Create fallback entry
        arch_fallback = f"""title Arch Linux ({kernel}) (fallback)
linux /vmlinuz-{kernel}
{microcode_initrd}initrd /initramfs-{kernel}-fallback.img
options {options}
"""
        with open("/mnt/boot/loader/entries/arch-fallback.conf", "w") as f:
            f.write(arch_fallback)
