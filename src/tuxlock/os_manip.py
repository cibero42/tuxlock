import subprocess
import os
import sys
import glob

class OsManip:
    def __init__(self):
        self.__supported_dists = ["ubuntu", "debian"]
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