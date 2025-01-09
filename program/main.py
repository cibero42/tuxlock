import inquirer
import sys

from os_class import OsManip, OsPackages

def main_menu():
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
        os_packages = OsPackages(os_manip.dist)
        os_packages.menu_installer()


if __name__ == "__main__":
    main_menu()