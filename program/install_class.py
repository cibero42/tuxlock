import subprocess
import os
import sys

class Installer:
    def __init__(self, dist):
        self.__dist = dist

    ####
    # > Installer.install_all
    # Installs all required packages
    ###
    def install_all():
        print("Run all installers")

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