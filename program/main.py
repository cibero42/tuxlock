import global_class

if __name__ == "__main__":
    os_manip = global_class.OsManip()
    if os_manip.is_root(True) == 1:
        print("fail :(")
