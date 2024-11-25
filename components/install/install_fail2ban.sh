#!/bin/bash
## Fail2Ban install script

source ../global_functions.sh

# Check if it root
if ! get_is_root; then
    msg_run_as_root
    exec sudo "$0" "$@"
fi

apt -qq update
echo "Installing Fail2Ban..."
apt -qq -y install fail2ban

echo "Enabling Fail2Ban..."
systemctl start fail2ban
systemctl enable fail2ban