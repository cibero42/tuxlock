import subprocess
import os
import sys
import glob
import re
import inquirer

class OsManip:
    def __init__(self):
        self.__supported_dists = ["ubuntu", "rhel", "fedora"]
        self.dist = self.__get_dist()

    ####
    # > (private).__get_dist
    # Checks and stores running OS.
    # Exits if not supported.
    ###
    def __get_dist(self):
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('ID='):
                        dist = line.strip().split('=')[1].strip('"').lower()
                        if dist in self.__supported_dists:
                            return dist
                        else:
                            print("Sorry, your system isn't supported.")
                            exit(1)
        except FileNotFoundError:
            print("ERROR! Can't determine OS")
            exit(1)

    ####
    # > OsManip.is_root
    # Checks if the script is running as root.
    # Attempts escalation if escalate=True.
    ###
    def is_root(self, escalate=False):
        if os.geteuid() != 0:
            if escalate:
                print("Not running as root, attempting to escalate.")
                try:
                    subprocess.check_call(['sudo', 'python3'] + sys.argv)
                except subprocess.CalledProcessError as e:
                    print(f"Failed to escalate to root: {e}")
                self.is_root()
            else:
                return False
        else:
            return True

    ####
    # > (private).get_gpg_keys
    # CIS Benchmark v1.0.0 1.2.1.1 (for Ubuntu 24.04)
    # Backend: Returns GPG keys for user to validate them, or None if none are found
    ####
    def __get_gpg_keys():
        patterns = [
            "/etc/apt/trusted.gpg.d/*.gpg",
            "/etc/apt/trusted.gpg.d/*.asc",
            "/etc/apt/sources.list.d/*.gpg",
            "/etc/apt/sources.list.d/*.asc"
        ]
        files_to_process = []
        results = {}
        
        for pattern in patterns:
            files = glob.glob(pattern, recursive=False)
            files_to_process.extend(file for file in files if os.path.isfile(file))
        
        if not files_to_process:
            return None

        for file_path in files_to_process:
            try:
                result = subprocess.run(
                    ["gpg", "--list-packets", file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True
                )
                output = result.stdout

                # Parse output
                keyids = set()
                signed_by = []

                for line in output.splitlines():
                    if "keyid" in line:
                        key_part = line.split()[-1]
                        if key_part not in keyids:
                            keyids.add(key_part)
                    if "Signed-By:" in line:
                        signed_by.append(line.split(":")[-1].strip())

                results[file_path] = {
                    "keyids": list(keyids),
                    "signed_by": signed_by
                }

            except Exception as e:
                results[file_path] = {"error": str(e)}
            return results

        
class PkgInstaller:
    def __init__(self, dist):
        self.__dist = dist

    ####
    # > OsPackages.get_package
    # Checks if a package is installed on the system.
    ####
    def get_package(self, package_name):
        try:
            if self.__dist == "ubuntu":
                subprocess.run(['dpkg', '-l', package_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return True
            raise Exception("on Installer.get_package")
        except subprocess.CalledProcessError:
            return False
        except Exception as e:
            print("Logic error: " + repr(e))

    ####
    # > PkgInstaller.install_package
    # Installs a package
    ####
    def install_package(self, program_name):
        try:
            if self.__dist == "ubuntu":
                if not self.get_package("program_name"):
                    subprocess.run(['apt', 'install', program_name, '-qq', '-y'], check=True)
            else:
                raise Exception("on Installer.get_package")
        except Exception as e:
            print("Logic error: " + repr(e))

    ####
    # > PkgInstaller.remove_package
    # Removes a package
    ####
    def remove_package(self, program_name):
        try:
            if self.__dist == "ubuntu":
                if self.get_package("program_name"):
                    subprocess.run(['apt', 'purge', program_name, '-qq', '-y'], check=True)
            else:
                raise Exception("on Installer.get_package")
        except Exception as e:
            print("Logic error: " + repr(e))

    ####
    # > PkgInstaller.update_pkg_list
    # Updates pkg database
    ####
    def update_pkg_list(self, program_name):
        try:
            if self.__dist == "ubuntu":
                subprocess.run(['apt', 'update', '-qq'], check=True)
            else:
                raise Exception("on Installer.get_package")
        except Exception as e:
            print("Logic error: " + repr(e))
    
    ####
    # > PkgInstaller.update_system
    # Updates system
    ####
    def update_system(self, program_name):
        try:
            if self.__dist == "ubuntu":
                subprocess.run(['apt', 'upgrade', '-qq', '-y'], check=True)
            else:
                raise Exception("on Installer.get_package")
        except Exception as e:
            print("Logic error: " + repr(e))

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
                # Prompt for Neo23x0 Auditd rules
                user_input = input("Install Neo23x0 Auditd rules? [y/n] (default: y): ").strip().lower()
                if not user_input:
                    user_input = "y"

                if user_input == "y":
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
        # TODO
        self.__change_prog_status("fail2ban", running_status, boot_status)

    ####
    # PkgConfig.unattended(self)
    # Configures Unattended Upgrades
    ####
    def unattended(self):
        # TODO
        pass

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
