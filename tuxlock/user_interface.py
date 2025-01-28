import sys
import inquirer
from time import sleep

class UserMenu:
    def __init__(self, os_manip, pkg_config, pkg_installer):
        self.__supported_packages = [ # Supported tuxlock packages
            "auditd",
            "apparmor",
            "fail2ban",
            "firewalld",
            "unattended-upgrades"
        ]
        self.os_manip = os_manip
        self.config = pkg_config
        self.installer = pkg_installer
        self.execute = True

    def __config_auditd(self):
        print("\n\n##################################\nAuditd Configuration\n##################################\n")
        answers = inquirer.prompt([
            inquirer.Confirm('enable_auditd', message="Enable auditd program?", default=True),
            inquirer.Confirm('install_default_rules', message="Install Neo23x0 Auditd rules?", default=True)
        ])
        self.config.auditd(
            running_status=answers['enable_auditd'], 
            boot_status=answers['enable_auditd'], 
            install_rules=answers['install_default_rules']
        )

    def __config_apparmor(self):
        print("\n\n##################################\nAppArmor Configuration\n##################################\n")
        answers = inquirer.prompt([
            inquirer.Confirm('enable_apparmor', message="Enable AppArmor?", default=True),
            inquirer.Confirm('install_rod_profiles', message="Install roddhjav's profiles?", default=True),
            inquirer.Confirm('enforce_apparmor', message="Enforce AppArmor policies?", default=True),
            inquirer.Confirm('run_on_boot', message="Enable AppArmor to run on boot?", default=True)
        ])
        self.config.apparmor(
            running_status=answers['enable_apparmor'], 
            boot_status=answers['enable_apparmor'], 
            install_rules=answers['install_rod_profiles'],
            force_enforcing=answers['enforce_apparmor'], 
            run_on_boot=answers['run_on_boot']
        )

    def __config_fail2ban(self):
        pass

    def __config_firewalld(self):
        print("\n\n##################################\nFirewalld Configuration\n##################################\n")
        answers = inquirer.prompt([
            inquirer.Confirm('enable_firewalld', message="Enable firewalld?", default=True),
            inquirer.Confirm('set_default_rules', message="Set default firewall rules?", default=True),
            inquirer.Confirm('ipv6_support', message="Enable IPv6 support?", default=False),
            inquirer.Confirm('docker_support', message="Enable Docker support?", default=False)
        ])
        self.config.firewalld(
            running_status=answers['enable_firewalld'], 
            boot_status=answers['enable_firewalld'],
            set_defaults=answers['set_default_rules'],
            ipv6=answers['ipv6_support'], 
            docker=answers['docker_support']
        )

    def __config_unattended(self):
        print("\n\n##################################\nUnattended Upgrades Configuration\n##################################\n")
        answers = inquirer.prompt([
            inquirer.Confirm('enable_unattended', message="Enable unattended-upgrades?", default=True),
            inquirer.Confirm('set_default_rules', message="Set recommended unattended-upgrades rules?", default=True)
        ])
        self.config.unattended(
            running_status=answers['enable_unattended'],
            boot_status=answers['enable_unattended'],
            set_defaults=answers['set_default_rules']
        )

    def __menu_installer(self):
        installed = []
        print("Checking for currently installed packages...")
        for pk in self.__supported_packages:
            if not self.installer.get_package(pk):
                installed.append(pk)

        answers = inquirer.prompt([
            inquirer.Checkbox(
                'installer_selection',
                message="Which security packages should be present on the system ?",
                choices=self.__supported_packages,
                default=installed
            )
        ])
        
        for pk in answers['installer_selection']:
            if pk == "auditd":
                self.installer.install_package("wget")
                self.installer.install_package("auditd")
                self.__config_auditd()

            elif pk == "apparmor":
                self.installer.install_package("apparmor apparmor-utils apparmor-profiles")
                self.__config_apparmor()

            elif pk == "fail2ban":
                self.installer.install_package("fail2ban")
                self.__config_fail2ban()

            elif pk == "firewalld":
                answers = inquirer.promt([
                    inquirer.Confirm(
                        "proceed", 
                        message="Upon Firewalld installation, IPTables Persistent and UFW will be uninstalled. All previous firewall configurations may be lost. Procceed?",
                        default=False
                        )
                ])
                if answers["proceed"]:
                    self.installer.remove_package("iptables-persistent")
                    self.installer.remove_package("ufw")
                    self.installer.install_package("firewalld")
                    self.__config_firewalld()
                else:
                    print(f"Firewalld won't be installed!")
                    
            elif pk == "unattended-upgrades":
                self.installer.install_package("unattended-upgrades")
                self.__config_unattended()

        # uninstall logic when package was installed on the system and unselected by user
        for pk in options:
            if pk not in answers['installer_selection'] and self.installer.get_package(pk):
                answer = inquirer.prompt([
                    inquirer.Confirm(f"uninstall_{pk}", message=f"Do you want to uninstall {pk}?", default=False)
                ])
                if answer[f"uninstall_{pk}"]:
                    self.installer.remove_package(pk)

    def __menu_config(self):
        installed = []
        print("Checking for currently installed packages...")
        for pk in self.__supported_packages:
            if not self.installer.get_package(pk):
                installed.append(pk)
        
        # Checks if there are no packets installed
        if not installed:
            print("No supported security packages were found.\nTry installing them first.")
            sleep(2)
            return

        print("\n\n################################################")
        print("Configuration Menu\n")
        answers = inquirer.prompt([
            inquirer.Checkbox(
                'selection',
                message="Which security packages should be configured?",
                choices=self.__supported_packages,
                default=installed
            )
        ])
        
        for pk in answers['selection']:
            if pk == "auditd":
                self.__config_auditd()

            elif pk == "apparmor":
                self.__config_apparmor()

            elif pk == "fail2ban":
                self.__config_fail2ban()

            elif pk == "firewalld":
                self.__config_firewalld()
                    
            elif pk == "unattended-upgrades":
                self.__config_unattended()

    def __menu_about(self):
        supported_list = ", ".join(map(str, self.__supported_packages))
        print("\n\n##############################################################################")
        print("About Tuxlock")
        print("Version: 0.1.0")
        print("License: AGPLv3")
        print("Maintainers: cibero42, Mayssa-Ayachi and KHLIFMOHAMEDAMINE")
        print(f"Supported security packages: {supported_list}")
        print("\nHelp improving this project! https://github.com/cibero42/tuxlock")

    def main_menu(self):
        options = [
            "Install/Remove Packages",
            "Configure Packages",
            "About",
            "Quit Program"
        ]

        answers = inquirer.prompt([
            inquirer.List(
                "menu_choice",
                message="MAIN MENU - Please select an option:",
                choices=options
            )
        ])

        # Enters installer menu
        if answers["menu_choice"] == options[0]:
            if not self.os_manip.is_root(True):
                print("Please run as root!")
                sys.exit(1)
            self.__menu_installer()

        # Enters config menu
        if answers["menu_choice"] == options[1]:
            if not self.os_manip.is_root(True):
                print("Please run as root!")
                sys.exit(1)
            self.__menu_config()

        # Shows about
        if answers["menu_choice"] == options[2]:
            self.__menu_about()

        # Exits program
        if answers["menu_choice"] == options[3]:
            self.execute = False