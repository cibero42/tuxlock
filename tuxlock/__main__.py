import tuxlock
from tuxlock import user_interface, os_manip, pkg_config, pkg_installer

def main():
    OsManip = os_manip.OsManip()
    PkgConfig = pkg_config.PkgConfig()
    PkgInstaller = pkg_installer.PkgInstaller(OsManip.dist)
    Menu = user_interface.UserMenu(OsManip, PkgConfig, PkgInstaller)

    while Menu.execute:
        Menu.main_menu()


if __name__ == "__main__":
    main()