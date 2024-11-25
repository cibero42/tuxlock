#!/bin/bash
## Global functions used by other scripts

#####
# > get_is_root
# Returns 0 if running as root
# Returns 1 if not
#####
get_is_root() {
    if [ "$EUID" -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

#####
# > msg_run_as_root
# Returns 0 if running as root
# Returns 1 if not
#####
msg_run_as_root() {
    echo "This program should run as root!"
}