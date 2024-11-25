#!/bin/bash
## AppArmor install script

source ../global_functions.sh

# Check if it root
if ! get_is_root; then
    msg_run_as_root
    exec sudo "$0" "$@"
fi

apt -qq update
echo "Installing AppArmor..."
apt -qq -y install apparmor apparmor-utils apparmor-profiles apparmor-notify

echo "Install experimental AppArmor profiles? [y/n] (default: n) "
read -r user_input
if [[ -z "$user_input" ]]; then
    user_input="n"
fi
user_input="${user_input,,}" #lowercase convertion

if [[ "$user_input" == "y" ]]; then
    echo "Installing experimental AppArmor profiles..."
    apt -qq -y install apparmor-profiles-extra
fi

echo "Enabling AppArmor..."
systemctl enable apparmor.service
systemctl reload apparmor.service