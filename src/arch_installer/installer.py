"""Core installer workflow orchestration"""

import logging
from arch_installer.disk import DiskManager
from arch_installer.packages import PackageManager
from arch_installer.bootloader.systemd_boot import SystemdBoot
from arch_installer.bootloader.grub import Grub
from arch_installer.locale import LocaleManager
from arch_installer.microcode import MicrocodeManager
from arch_installer.swap import SwapManager
from arch_installer.utils import run, check_efi
from arch_installer.ui.curses_ui import CursesUI

class Installer:
    """Main installer class orchestrating the installation process"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.config = {}
        self.ui = CursesUI(stdscr)
        self.disk_manager = DiskManager()
        self.package_manager = PackageManager()
        self.locale_manager = LocaleManager()
        self.microcode_manager = MicrocodeManager()
        self.swap_manager = SwapManager()
        
        # Setup logging
        logfile = "/tmp/arch-install.log"
        logging.basicConfig(
            filename=logfile,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Run the complete installation process"""
        try:
            self._pre_install_checks()
            self._gather_configuration()
            self._confirm_installation()
            self._execute_installation()
            self._post_installation()
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            self.ui.show_error(f"Installation failed: {e}")
            raise

    def _pre_install_checks(self):
        """Perform pre-installation checks"""
        if not check_efi():
            self.ui.show_error("System does not support UEFI! UEFI only supported.")
            raise SystemExit("UEFI not supported")

    def _gather_configuration(self):
        """Gather all configuration from user"""
        # Disk selection
        disks = self.disk_manager.list_disks()
        if not disks:
            raise SystemExit("No disks found!")
        
        self.config['disk'] = self.ui.menu("Select Disk to install", disks, self.config, "Disk")
        self.config['disk'] = self.config['disk'].split()[0]  # Get /dev/sdX

        # User configuration
        make_user = self.ui.menu("Create user?", ["Yes", "No"], self.config, "User?")
        if make_user == "Yes":
            self.config['username'] = self.ui.input("Enter username:", self.config, "Username")
            self.config['userpass'] = self.ui.input("Enter password:", self.config, "Password", hidden=True)
        else:
            self.config['username'] = None

        self.config['rootpass'] = self.ui.input("Enter root password:", self.config, "Root Password", hidden=True)

        # System configuration
        self.config['kernel'] = self.ui.menu("Select Kernel", ["linux", "linux-lts", "linux-zen","None"], self.config, "Kernel")
        self.config['gpu'] = self.ui.menu("Select GPU Driver", ["intel", "amd", "nvidia","None"], self.config, "GPU")
        self.config['wmde'] = self.ui.menu("Select WM/DE", ["hyprland","bspwm",  "gnome", "kde","None"], self.config, "WM/DE")
        self.config['bootloader'] = self.ui.menu("Select Bootloader", ["systemd-boot", "grub","None"], self.config, "Bootloader")

        # Swap configuration
        swap_choice = self.ui.menu("Create swap file?", ["Yes", "No"], self.config, "Swap file")
        self.config['use_swap'] = (swap_choice == "Yes")

        # Locale configuration
        locale_choice = self.ui.menu("Configure locale?", ["Yes", "No"], self.config, "Configure locale?")
        if locale_choice == "Yes":
            self.config['locale'] = self.locale_manager.get_locale_config(self.ui, self.config)
        else:
            self.config['locale'] = self.locale_manager.get_default_locale_config()

    def _confirm_installation(self):
        """Show configuration summary and confirm installation"""
        if not self.ui.confirm_installation(self.config):
            raise SystemExit("Installation cancelled by user")

    def _execute_installation(self):
        """Execute the installation steps"""
        # Unmount disk
        self.ui.show_step("Unmounting disk...")
        self.disk_manager.unmount_disk(self.config['disk'])

        # Partitioning
        self.ui.show_step("Partitioning disk...")
        efi_partition, root_partition = self.disk_manager.partition_disk(self.config['disk'])
        self.config['efi_partition'] = efi_partition
        self.config['root_partition'] = root_partition

        # Format and mount
        self.ui.show_step("Formatting and mounting partitions...")
        self.disk_manager.format_and_mount(efi_partition, root_partition)

        # Optimize mirrorlist
        self.ui.show_step("Optimizing mirrorlist...")
        self.package_manager.optimize_mirrorlist()

        # Install base packages
        self.ui.show_step("Installing base packages...")
        self.package_manager.install_base_packages(
            self.ui, 
            self.config['kernel'], 
            self.config['gpu'], 
            self.config['wmde']
        )

        # Setup swap if selected
        if self.config['use_swap']:
            self.ui.show_step("Setting up swap file...")
            self.swap_manager.setup_swapfile()

        # Configure locale
        self.ui.show_step("Configuring locale...")
        self.locale_manager.setup_locale(self.config['locale'])

        # Basic system configuration
        self.ui.show_step("Configuring system...")
        self._configure_system()

        # Install bootloader
        self.ui.show_step("Installing bootloader...")
        self._install_bootloader()

        # Set passwords
        self.ui.show_step("Setting passwords...")
        self._set_passwords()

        # Configure user locale if user exists
        if self.config['username']:
            self.ui.show_step("Configuring user settings...")
            self.locale_manager.setup_user_locale(self.config['username'], self.config['locale'])

    def _configure_system(self):
        """Configure basic system settings"""
        run("arch-chroot /mnt ln -sf /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime")
        run("arch-chroot /mnt hwclock --systohc")
        run("arch-chroot /mnt systemctl enable NetworkManager")

        # Enable display manager based on WM/DE
        if self.config['wmde'] == "gnome":
            run("arch-chroot /mnt systemctl enable gdm")
        elif self.config['wmde'] == "kde":
            run("arch-chroot /mnt systemctl enable sddm")

    def _install_bootloader(self):
        """Install and configure bootloader"""
        if self.config['bootloader'] == "systemd-boot":
            bootloader = SystemdBoot()
        else:
            bootloader = Grub()
        
        microcode_file = self.microcode_manager.add_microcode()
        bootloader.install(
            self.config['root_partition'],
            self.config['kernel'],
            self.config['gpu'],
            microcode_file
        )

    def _set_passwords(self):
        """Set root and user passwords"""
        run(f"arch-chroot /mnt bash -c \"echo 'root:{self.config['rootpass']}' | chpasswd\"")
        
        if self.config['username']:
            run(f"arch-chroot /mnt useradd -m -G wheel -s /bin/bash {self.config['username']}")
            run(f"arch-chroot /mnt bash -c \"echo '{self.config['username']}:{self.config['userpass']}' | chpasswd\"")
            run("arch-chroot /mnt bash -c \"echo '%wheel ALL=(ALL:ALL) ALL' >> /etc/sudoers\"")

    def _post_installation(self):
        """Post-installation steps"""
        self.ui.show_success("Installation completed successfully!")
        
        if self.ui.prompt_reboot():
            run("reboot")
