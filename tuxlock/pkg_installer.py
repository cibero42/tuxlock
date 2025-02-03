import subprocess

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
                subprocess.run(['dpkg', '-s', package_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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