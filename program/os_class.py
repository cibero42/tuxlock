import subprocess
import os
import sys
import glob
import re

class OsManip:
    def __init__(self):
        self.__supported_dists = ["ubuntu", "rhel", "fedora"]
        self.dist = self.__get_dist()
        print(self.dist)

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
                return True
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

        
class OsPackage:
    def __init__(self, dist):
        self.__dist = dist

    ####
    # > (private).__get_package
    # Checks if a package is installed on the system.
    ####
    def __get_package(self, package_name):
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
    # > (private).__enable_program
    # Starts and enables program
    ####
    def __enable_program(self, program_name):
        print("Enabling " + program_name + "...")
        subprocess.run(['systemctl', 'start', program_name], check=True)
        subprocess.run(['systemctl', 'enable', program_name], check=True)

    ####
    # > (private).__disable_program
    # Stops and disables program
    ####
    def __disable_program(self, program_name):
        print("Enabling " + program_name + "...")
        subprocess.run(['systemctl', 'stop', program_name], check=True)
        subprocess.run(['systemctl', 'disable', program_name], check=True)

    ####
    # > (private).__install_dependencies
    # Install dependencies for program execution.
    ####
    def __install_dependencies(self):
        try:
            if self.__dist == "ubuntu":
                subprocess.run(['apt', 'update', '-qq'], check=True)
                subprocess.run(['apt', 'install', 'wget', '-qq', '-y'], check=True)
            else:
                raise Exception("on Installer.get_package")

        except Exception as e:
            print("Logic error: " + repr(e))

    ####
    # > (private).install_auditd
    # Installs Auditd.
    ####
    def __install_auditd(self):
        try:
            if self.__dist == "ubuntu":
                if not self.__get_package("auditd"):
                    print("Installing Auditd...")
                    subprocess.run(['apt', 'install', 'auditd', '-qq', '-y'], check=True)
            else:
                raise Exception("on Installer.get_package")
            
            # Prompt for Neo23x0 Auditd rules
            user_input = input("Install Neo23x0 Auditd rules? [y/n] (default: y): ").strip().lower()
            if not user_input:
                user_input = "y"

            if user_input == "y":
                subprocess.run(['wget', '-O', '/etc/audit/audit.rules.auto', 'https://raw.githubusercontent.com/Neo23x0/auditd/refs/heads/master/audit.rules'], check=True)
                subprocess.run(['auditctl', '-R', '/etc/audit/audit.rules.auto'], check=True)

        except Exception as e:
            print("Logic error: " + repr(e))

        self.__enable_program("auditd")
        
    ####
    # > (private).install_apparmor
    # Installs AppArmor.
    ####
    def __install_apparmor(self):
        try:
            if self.__dist == "ubuntu":
                    print("Installing AppArmor...")
                    subprocess.run(['apt', 'install', 'apparmor', 'apparmor-utils', 'apparmor-profiles', 'apparmor-notify', '-qq', '-y'], check=True)
                    user_input = input("Install experimental AppArmor profiles? [y/n] (default: n) ").strip().lower()
                    if not user_input:
                        user_input = "n"
                    
                    if user_input == "y":
                        subprocess.run(['apt', 'install', 'apparmor-profiles-extra', '-qq', '-y'], check=True)
            else:
                raise Exception("on Installer.get_package")
        except Exception as e:
            print("Logic error: " + repr(e))

        self.__enable_program("apparmor.service")

        # Makes AppArmor be loaded on boot by GRUB
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