import logging
import subprocess
from typing import Callable, List, Optional


def build_package_list(kernel: str, gpu: str, wmde: str) -> List[str]:
    """
    Xây dựng danh sách gói cần cài đặt dựa theo kernel, GPU driver và WM/DE.

    :param kernel: "linux", "linux-lts", "linux-zen", ...
    :param gpu: "intel", "amd", "nvidia", "vmware", ...
    :param wmde: "gnome", "kde", "xfce", "bspwm", "hyprland", ...
    :return: list gói pacman
    """
    pkgs = ["base", kernel, "linux-firmware", "vim", "networkmanager"]

    # GPU drivers
    gpu_drivers = {
        "intel": ["mesa", "xf86-video-intel"],
        "amd": ["mesa", "xf86-video-amdgpu"],
        "nvidia": ["nvidia", "nvidia-utils"],
        "vmware": ["xf86-video-vmware"],
    }
    if gpu in gpu_drivers:
        pkgs.extend(gpu_drivers[gpu])
    else:
        logging.warning("GPU %s không được hỗ trợ rõ ràng, bỏ qua driver", gpu)

    # Desktop environments / window managers
    wmde_pkgs = {
        "gnome": ["gnome", "gdm"],
        "kde": ["plasma", "sddm"],
        "xfce": ["xfce4", "lightdm", "lightdm-gtk-greeter"],
        "bspwm": ["bspwm", "sxhkd", "xorg", "lightdm", "lightdm-gtk-greeter"],
        "hyprland": ["hyprland", "waybar", "xdg-desktop-portal-hyprland"],
    }
    if wmde in wmde_pkgs:
        pkgs.extend(wmde_pkgs[wmde])
    else:
        logging.warning("WM/DE %s không được hỗ trợ rõ ràng, bỏ qua", wmde)

    return pkgs


def pacstrap(
    mountpoint: str,
    pkgs: List[str],
    progress_callback: Optional[Callable[[str], None]] = None,
    dry_run: bool = False,
):
    """
    Chạy pacstrap để cài đặt gói vào hệ thống mới.

    :param mountpoint: thư mục mount root (ví dụ: /mnt)
    :param pkgs: danh sách gói để cài đặt
    :param progress_callback: function(line: str), gọi mỗi dòng stdout/stderr
    :param dry_run: nếu True thì chỉ log lệnh mà không thực thi
    """
    cmd = ["pacstrap", mountpoint] + pkgs
    logging.info("Running: %s", " ".join(cmd))

    if dry_run:
        print("DRY-RUN:", " ".join(cmd))
        return

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assert process.stdout is not None
    for line in process.stdout:
        line = line.strip()
        if progress_callback:
            progress_callback(line)
        else:
            print(line)

    ret = process.wait()
    if ret != 0:
        raise RuntimeError(f"pacstrap failed with exit code {ret}")

