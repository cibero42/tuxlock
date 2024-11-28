import subprocess
import os
import sys

class OsManip:
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
                return 0
            else:
                return 1 
        else:
            return 0
