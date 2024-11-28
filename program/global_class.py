import subprocess
import os
import sys

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
