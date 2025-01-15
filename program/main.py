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
            message="Which security packages should be present on the system ?",
            choices=options,
            default=installed
        )
    ])
    
    for pk in answers['installer_selection']:
        if pk == "auditd":
            installer.install_package("wget")
            installer.install_package("auditd")
            # Ask user for default rules and enable program
            auditd_answers = inquirer.prompt([
                inquirer.Confirm('enable_auditd', message="Enable auditd program?", default=True),
                inquirer.Confirm('install_default_rules', message="Install default auditd rules?", default=True)
            ])
            config.auditd(auditd_answers['enable_auditd'], True, install_rules=auditd_answers['install_default_rules'])

        elif pk == "apparmor":
            installer.install_package("apparmor apparmor-utils apparmor-profiles")
            # Ask user for options
            apparmor_answers = inquirer.prompt([
                inquirer.Confirm('enable_apparmor', message="Enable AppArmor?", default=True),
                inquirer.Confirm('install_rod_profiles', message="Install roddhjav's profiles?", default=True),
                inquirer.Confirm('enforce_apparmor', message="Enforce AppArmor policies?", default=True),
                inquirer.Confirm('run_on_boot', message="Enable AppArmor to run on boot?", default=True)
            ])
            config.apparmor(
                apparmor_answers['enable_apparmor'], 
                True, 
                install_rules=apparmor_answers['install_rod_profiles'],
                force_enforcing=apparmor_answers['enforce_apparmor'], 
                run_on_boot=apparmor_answers['run_on_boot']
            )

        elif pk == "fail2ban":
            installer.install_package("fail2ban")
            # TODO config: Add questions and call config.fail2ban

        elif pk == "firewalld":
            installer.remove_package("iptables-persistent")
            installer.remove_package("ufw")
            installer.install_package("firewalld")
            # Ask user for default rules and enable program
            firewalld_answers = inquirer.prompt([
                inquirer.Confirm('enable_firewalld', message="Enable firewalld?", default=True),
                inquirer.Confirm('set_default_rules', message="Set default firewall rules?", default=True),
                inquirer.Confirm('ipv6_support', message="Enable IPv6 support?", default=False),
                inquirer.Confirm('docker_support', message="Enable Docker support?", default=False)
            ])
            config.firewalld(
                firewalld_answers['enable_firewalld'], 
                True, 
                set_defaults=firewalld_answers['set_default_rules'],
                ipv6=firewalld_answers['ipv6_support'], 
                docker=firewalld_answers['docker_support']
            )

        elif pk == "unattended-upgrades":
            installer.install_package("unattended-upgrades")
            # TODO config: Add questions and call config.unattended_upgrades

    # uninstall logic when package was installed on the system and unselected by user
    for pk in options:
        if pk not in answers['installer_selection'] and installer.get_package(pk):
            uninstall_answer = inquirer.prompt([
                inquirer.Confirm(f"uninstall_{pk}", message=f"Do you want to uninstall {pk}?", default=False)
            ])
            if uninstall_answer[f"uninstall_{pk}"]:
                installer.remove_package(pk)

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
