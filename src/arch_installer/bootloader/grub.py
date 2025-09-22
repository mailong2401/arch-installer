"""GRUB configuration"""

from arch_installer.utils import run

class Grub:
    """GRUB bootloader manager"""
    
    def install(self, root_partition, kernel, gpu, microcode_file=None):
        """Install and configure GRUB"""
        run("arch-chroot /mnt pacman -S --noconfirm grub efibootmgr")
        run("arch-chroot /mnt grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB")
        
        # Add microcode if available
        if microcode_file:
            run(f"arch-chroot /mnt sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT=\"/GRUB_CMDLINE_LINUX_DEFAULT=\"initrd=\\\\{microcode_file} /' /etc/default/grub")
        
        run("arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg")
