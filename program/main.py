import inquirer
import sys

from os_class import OsManip, PkgInstaller, PkgConfig

def menu_installer(distribution):
    installer = PkgInstaller(distribution)
    config = PkgConfig()

    options = [
        "auditd",
        "apparmor",
        "fail2ban",
        "firewalld",
        "unattended-upgrades"
    ]
    installed = []
    print("Checking for currently installed packages...")
    for pk in options:
        if not installer.get_package(pk):
            installed.append(pk)

    answers = inquirer.prompt([
        inquirer.Checkbox(
            'installer_selection',
            message="Which security packages should be present on the system?",
            choices=options,
            default=installed
        )
    ])
    for pk in answers['installer_selection']:
        if pk == "auditd":
            installer.install_package("wget")
            installer.install_package("auditd")
            # TODO: ask user for default rules + enable program
            # config.auditd(running_status, boot_status, install_rules = False)

        elif pk == "apparmor":
            installer.install_package("apparmor apparmor-utils apparmor-profiles")
            # TODO: Ask user for options
            # roddhjav's profiles (https://github.com/roddhjav/apparmor.d)
            # config.apparmor(self, running_status, boot_status, install_rules = False, force_enforcing = False, run_on_boot = False)

        elif pk == "fail2ban":
            installer.install_package("fail2ban")
            # TODO config

        elif pk == "firewalld":
            installer.remove_package("iptables-persistent")
            installer.remove_package("ufw")
            installer.install_package("firewalld")
            # TODO: ask user for default rules + enable program
            # config.firewalld(self, running_status, boot_status, set_defaults = False, ipv6 = False, docker = False):
        
        elif pk == "unattended-upgrades":
            installer.install_package("unattended-upgrades")
            # TODO config

    # TODO: pkg uninstall logic when installed on the system and unselected by user
    # Ask for user confirmation per package!!!!!


if __name__ == "__main__":
    os_manip = OsManip()

    options = [
        "Install/Remove Packages",
        "Quit Program"
    ]
    answers = inquirer.prompt([
        inquirer.List(
            "menu_choice",
            message="MAIN MENU - Please select an option:",
            choices=options
        )
    ])

    if answers["menu_choice"] == options[0]:
        if not os_manip.is_root(True):
            print("Failed to escalate. Exiting program")
            sys.exit(1)
        menu_installer(os_manip.dist)