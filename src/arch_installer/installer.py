# src/arch_installer/installer.py

import logging
import os
import sys
import traceback

from arch_installer import packages


class Installer:
    def __init__(self, config, ui=None, dry_run=False):
        """
        :param config: dict hoặc object chứa cấu hình cài đặt
        :param ui: instance của CursesUI hoặc None (noninteractive)
        :param dry_run: bool, nếu True thì chỉ log mà không thực thi
        """
        self.config = config
        self.ui = ui
        self.dry_run = dry_run

    def run(self):
        """Thực hiện toàn bộ quy trình cài đặt Arch Linux"""
        logging.info("Starting installation process")
        try:
            self._validate_preconditions()
            self._unmount_disk()
            self._partition_and_format()
            self._mount_filesystems()
            self._optimize_mirrorlist()
            self._pacstrap_base()
            self._setup_swap()
            self._configure_system()
            self._enable_services()
            self._install_bootloader()
            self._setup_users()
            self._finish()
            logging.info("Installation finished successfully")

        except Exception as e:
            logging.error("Installation failed: %s", e)
            traceback.print_exc()
            self._cleanup_on_error()
            sys.exit(1)

    # --- Các bước chi tiết ---
    def _validate_preconditions(self):
        logging.info("Validating preconditions (root, UEFI)")
        if os.geteuid() != 0:
            raise RuntimeError("Installer must be run as root")
        if not os.path.exists("/sys/firmware/efi"):
            raise RuntimeError("UEFI firmware not detected")

    def _unmount_disk(self):
        logging.info("Unmounting target disk if mounted")
        # TODO: implement umount logic

    def _partition_and_format(self):
        logging.info("Partitioning disk and creating filesystems")
        # TODO: run parted, mkfs, etc.

    def _mount_filesystems(self):
        logging.info("Mounting filesystems")
        # TODO: mount root, boot, home, etc.

    def _optimize_mirrorlist(self):
        logging.info("Optimizing mirrorlist")
        # TODO: run reflector or rankmirrors

    def _pacstrap_base(self):
        logging.info("Installing base packages with pacstrap")

        kernel = self.config.get("kernel", "linux")
        gpu = self.config.get("gpu", "intel")
        wmde = self.config.get("wmde", "gnome")

        pkgs = packages.build_package_list(kernel, gpu, wmde)

        def progress(line: str):
            if self.ui:
                # nếu có UI curses → show_progress
                # (ở đây có thể gom vào self.ui.show_progress, nhưng show_progress hiện cần stream,
                # nên ta feed từng dòng thay thế)
                try:
                    self.ui.stdscr.addstr(line + "\n")
                    self.ui.stdscr.refresh()
                except Exception:
                    pass
            else:
                print(line)

        packages.pacstrap("/mnt", pkgs, progress_callback=progress, dry_run=self.dry_run)
    def _setup_swap(self):
        logging.info("Setting up swap")
        # TODO: swapon hoặc tạo swapfile

    def _configure_system(self):
        logging.info("Configuring locale, timezone, hwclock")
        # TODO: write locale.gen, set timezone, hwclock --systohc

    def _enable_services(self):
        logging.info("Enabling system services")
        # TODO: systemctl enable NetworkManager, etc.

    def _install_bootloader(self):
        logging.info("Installing bootloader")
        # TODO: grub-install hoặc systemd-boot

    def _setup_users(self):
        logging.info("Setting root password and creating user")
        # TODO: passwd, useradd, usermod

    def _finish(self):
        logging.info("Finalizing installation (cleanup, unmount)")
        # TODO: unmount, reboot message

    def _cleanup_on_error(self):
        logging.info("Cleaning up after error (unmount, rollback)")
        # TODO: unmount chroot nếu cần


# --- API cho __main__.py ---
def run_from_config(config_path, dry_run=False):
    import yaml

    with open(config_path) as f:
        config = yaml.safe_load(f)

    installer = Installer(config, ui=None, dry_run=dry_run)
    installer.run()


def run_interactive(ui, dry_run=False):
    # TODO: implement UI-driven config gathering
    config = {"disk": "/dev/sda"}  # placeholder
    installer = Installer(config, ui=ui, dry_run=dry_run)
    installer.run()

