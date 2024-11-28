from install_class import Installer
from global_class import OsManip

if __name__ == "__main__":
    os_manip = OsManip()
    installer = Installer(os_manip.dist)