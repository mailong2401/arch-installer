"""Locale configuration management"""

import subprocess
from arch_installer.utils import run

class LocaleManager:
    """Manage locale configuration"""
    
    @staticmethod
    def get_available_locales():
        """Get list of available locales"""
        try:
            result = subprocess.run("locale -a", shell=True, capture_output=True, text=True)
            return result.stdout.strip().split('\n')
        except:
            return ["en_US.UTF-8", "vi_VN.UTF-8", "C.UTF-8"]
    
    def get_locale_config(self, ui, config):
        """Get locale configuration from user"""
        available_locales = self.get_available_locales()
        main_locale = ui.menu("Select main locale", available_locales, config, "Main locale")
        
        locale_config = {
            'locale': main_locale,
            'lang': ui.input("System language (LANG):", config, "LANG", default=main_locale.split('.')[0]),
            'time_format': ui.input("Time format (LC_TIME):", config, "LC_TIME", default=main_locale),
            'number_format': ui.input("Number format (LC_NUMERIC):", config, "LC_NUMERIC", default=main_locale),
            'currency_format': ui.input("Currency format (LC_MONETARY):", config, "LC_MONETARY", default=main_locale)
        }
        
        return locale_config
    
    @staticmethod
    def get_default_locale_config():
        """Get default locale configuration"""
        return {
            'locale': 'en_US.UTF-8',
            'lang': 'en_US.UTF-8',
            'time_format': 'en_US.UTF-8',
            'number_format': 'en_US.UTF-8',
            'currency_format': 'en_US.UTF-8'
        }
    
    @staticmethod
    def setup_locale(locale_conf):
        """Configure system locale"""
        # Configure locale.gen
        locales_to_enable = [
            "en_US.UTF-8 UTF-8",
            "vi_VN.UTF-8 UTF-8",
            locale_conf['locale'] + " UTF-8"
        ]
        
        # Remove duplicates
        unique_locales = list(set(locales_to_enable))
        
        with open("/mnt/etc/locale.gen", "r") as f:
            content = f.read()
        
        for locale in unique_locales:
            # Uncomment locale if needed
            content = content.replace(f"#{locale}", locale)
        
        with open("/mnt/etc/locale.gen", "w") as f:
            f.write(content)
        
        # Create locale.conf
        locale_content = f"""LANG={locale_conf['lang']}
LC_TIME={locale_conf['time_format']}
LC_NUMERIC={locale_conf['number_format']}
LC_MONETARY={locale_conf['currency_format']}
"""
        with open("/mnt/etc/locale.conf", "w") as f:
            f.write(locale_content)
        
        # Generate locales
        run("arch-chroot /mnt locale-gen")
    
    @staticmethod
    def setup_user_locale(username, locale_conf):
        """Create locale configuration for user"""
        if not username:
            return

        # Create user locale configuration
        locale_content = f"""LANG={locale_conf['lang']}
LC_TIME={locale_conf['time_format']}
LC_NUMERIC={locale_conf['number_format']}
LC_MONETARY={locale_conf['currency_format']}
"""

        import os
        temp_path = f"/mnt/home/{username}/.config"
        os.makedirs(temp_path, exist_ok=True)
        with open(f"{temp_path}/locale.conf", "w") as f:
            f.write(locale_content)

        # Ensure user owns the file
        run(f"arch-chroot /mnt chown -R {username}:{username} /home/{username}/.config")
