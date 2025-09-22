"""Microcode detection and installation"""

from arch_installer.utils import run

class MicrocodeManager:
    """Manage CPU microcode installation"""
    
    @staticmethod
    def detect_cpu_type():
        """Detect CPU type (Intel/AMD)"""
        try:
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()
            
            if "GenuineIntel" in cpuinfo:
                return "intel"
            elif "AuthenticAMD" in cpuinfo:
                return "amd"
        except Exception as e:
            print(f"Could not determine CPU type: {e}")
        
        return None
    
    def add_microcode(self):
        """Add appropriate microcode package"""
        cpu_type = self.detect_cpu_type()
        
        if cpu_type == "intel":
            run("pacstrap /mnt intel-ucode")
            return "intel-ucode.img"
        elif cpu_type == "amd":
            run("pacstrap /mnt amd-ucode")
            return "amd-ucode.img"
        
        return None
