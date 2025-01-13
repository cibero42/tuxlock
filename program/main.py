import inquirer
import sys

from os_class import OsManip, OsPackages

def menu_installer(distribution):
    os_pkg = OsPackages(distribution)

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
        if not os_pkg.__get_package(pk):
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
            print("TODO: auditd")
        elif pk == "apparmor":
            print("TODO: Apparmor")
        elif pk == "fail2ban":
            print("TODO: fail2ban")
        elif pk == "firewalld":
            print("TODO: firewalld")


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