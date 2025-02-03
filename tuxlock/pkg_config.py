import subprocess
import os
import re

class PkgConfig:
    ####
    # > (private).__change_prog_status
    # Enables/Disables, Starts/Stops program
    ####
    def __change_prog_status(self, program_name, running_status, boot_status):
        print("Enabling " + program_name + "...")
        if running_status:
            subprocess.run(['systemctl', 'start', program_name], check=True)
        else:
            subprocess.run(['systemctl', 'stop', program_name], check=True)

        if boot_status:
            subprocess.run(['systemctl', 'enable', program_name], check=True)
        else:
            subprocess.run(['systemctl', 'disable', program_name], check=True)

    ####
    # PkgConfig.auditd(self, running_status, boot_status, [install_rules])
    # Configures Auditd
    ####
    def auditd(self, running_status, boot_status, install_rules = False):
        if install_rules:
            self.__change_prog_status("auditd", False, boot_status)
            try:
                if install_rules:
                    subprocess.run(['wget', '-O', '/etc/audit/audit.rules.auto', 'https://raw.githubusercontent.com/Neo23x0/auditd/refs/heads/master/audit.rules'], check=True)
                    subprocess.run(['auditctl', '-R', '/etc/audit/audit.rules.auto'], check=True)

            except Exception as e:
                print("Logic error: " + repr(e))
        self.__change_prog_status("auditd", running_status, boot_status)

    ####
    # PkgConfig.apparmor(self, running_status, boot_status, [install_rules], [force_enforcing], [run_on_boot])
    # Configures Apparmor
    ####
    def apparmor(self, running_status, boot_status, install_rules = False,
                 force_enforcing = False, run_on_boot = False):
        self.__change_prog_status("apparmor", False, boot_status)
        if install_rules:
            try:
                subprocess.run(["tee", "-a", "/etc/apparmor/parser.conf"], input="write-cache\n", text=True, check=True)
                subprocess.run(["tee", "-a", "/etc/apparmor/parser.conf"], input="Optimize=compress-fast\n", text=True, check=True)

                self.__install_package("build-essential config-package-dev debhelper golang-go git rsync")

                print("Cloning AppArmor profiles repository...")
                subprocess.run(["git", "clone", "https://github.com/roddhjav/apparmor.d.git"], check=True)
                os.chdir("apparmor.d")

                print("Building the AppArmor package...")
                subprocess.run(["dpkg-buildpackage", "-b", "-d", "--no-sign"], check=True)

                print("Installing the AppArmor package...")
                subprocess.run(["dpkg", "-i", "../apparmor.d_*.deb"], shell=True, check=True)
            except Exception as e:
                print("Logic error: " + repr(e))
        
        # Run all profiles in enforcing mode (CIS 1.3.1.4)
        if force_enforcing:
            subprocess.run(['aa-enforce', '/etc/apparmor.d/*'], check=True)
        else:
            print("TODO: undo changes if present")
        
        if run_on_boot:
            # Makes AppArmor be loaded on boot by GRUB (CIS 1.3.1.2)
            with open('/etc/default/grub', 'r') as file:
                lines = file.readlines()
                grub_cmdline_pattern = r'^GRUB_CMDLINE_LINUX="(.*)"'
                updated_lines = []

                for line in lines:
                    match = re.match(grub_cmdline_pattern, line)
                    if match:
                        current_options = match.group(1)
                        if 'apparmor=1' not in current_options and 'security=apparmor' not in current_options:
                            new_options = f'{current_options} apparmor=1 security=apparmor'
                            line = f'GRUB_CMDLINE_LINUX="{new_options}"\n'
                    updated_lines.append(line)

            with open('/etc/default/grub', 'w') as file:
                file.writelines(updated_lines)
            subprocess.run(['update-grub'], check=True)
        else:
            print("TODO: undo changes if present")

        self.__change_prog_status("apparmor", running_status, boot_status)

    ####
    # PkgConfig.fail2ban(self, running_status, boot_status)
    # Configures Fail2Ban
    ####
    def fail2ban(self, running_status, boot_status):
        self.__change_prog_status("fail2ban", running_status, boot_status)

    ####
    # PkgConfig.unattended(self)
    # Configures Unattended Upgrades
    ####
    def unattended(self, running_status, boot_status, set_defaults = False, unset_defaults = False):
        self.__change_prog_status("unattended-upgrades", running_status, boot_status)
        if set_defaults:
            default_exists = False
            with open("/etc/apt/apt.conf.d/50unattended-upgrades", "r") as file:
                # Check if recommended defaults are already present
                content = file.read()
                for line in content:
                    if '// TUXLOCK Defaults' in line:
                        default_exists = True
                        break
            
            with open("/etc/apt/apt.conf.d/50unattended-upgrades", "a") as file:
                if not default_exists:
                    file.write("\n// TUXLOCK Defaults\n")
                    file.write('Unattended-Upgrade::AutoFixInterruptedDpkg "true";\n')
                    file.write('Unattended-Upgrade::Remove-New-Unused-Dependencies "true";\n')
                    file.write('Unattended-Upgrade::Remove-Unused-Dependencies "true";\n')
                    file.write('Unattended-Upgrade::MinimalSteps "true";\n')
        if unset_defaults:
            with open("/etc/apt/apt.conf.d/50unattended-upgrades", "r") as file:
                lines = file.readlines()
            
            lines = [line for line in lines if not line.strip().startswith('// TUXLOCK Defaults')]

            with open("/etc/apt/apt.conf.d/50unattended-upgrades", "w") as file:
                file.writelines(lines)

    ####
    # PkgConfig.firewalld(self, running_status, boot_status, [set_defaults], [ipv6], [docker])
    # Configures Firewalld
    ####
    def firewalld(self, running_status, boot_status, set_defaults = False, 
                  ipv6 = False, docker = False):
        if set_defaults:
            subprocess.run(['firewall-cmd', '--permanent', '--zone=public', '--set-target=DROP'], check=True)
            subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv4 filter OUTPUT 0 -m state --state ESTABLISHED,RELATED -j ACCEPT'], check=True)
            subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv4 filter OUTPUT 1 -p tcp --state NEW --dport 80 -j ACCEPT'], check=True)
            subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv4 filter OUTPUT 1 -p tcp --state NEW --dport 443 -j ACCEPT'], check=True)
            subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv4 filter OUTPUT 1 -p tcp --state NEW --dport 53 -j ACCEPT'], check=True)
            subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv4 filter OUTPUT 1 -p udp --state NEW --dport 53 -j ACCEPT'], check=True)
            subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv4 filter OUTPUT 1 -p udp --state NEW --dport 123 -j ACCEPT'], check=True)
            subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv4 filter OUTPUT 2 -j DROP'], check=True)

            if ipv6:
                subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv6 filter OUTPUT 0 -m state --state ESTABLISHED,RELATED -j ACCEPT'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv6 filter OUTPUT 1 -p tcp --state NEW --dport 80 -j ACCEPT'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv6 filter OUTPUT 1 -p tcp --state NEW --dport 443 -j ACCEPT'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv6 filter OUTPUT 1 -p tcp --state NEW --dport 53 -j ACCEPT'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv6 filter OUTPUT 1 -p udp --state NEW --dport 53 -j ACCEPT'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv6 filter OUTPUT 1 -p udp --state NEW --dport 123 -j ACCEPT'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--direct', '--add-rule' 'ipv6 filter OUTPUT 2 -j DROP'], check=True)

            if docker:
                subprocess.run(['firewall-cmd', '--permanent', '--new-zone=docker'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--zone=docker', '--set-target=DROP'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--new-policy=docker-out'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--policy=docker-out', '--add-ingress-zone docker'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--policy=docker-out', '--add-egress-zone public'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--policy=docker-out', '--set-target ACCEPT'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--policy=docker-out', '--add-masquerade'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--new-policy=docker-routing'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--policy=docker-routing', '--add-ingress-zone docker'], check=True)
                subprocess.run(['firewall-cmd', '--permanent', '--policy=docker-routing', '--add-egress-zone docker'], check=True)
        # TO DO: Loopback interface (CIS 4.2.4)
        # TO DO: Ask user to open ports (CIS 4.2.6)
