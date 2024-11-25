#!/bin/bash
## Auditd install script

source ../global_functions.sh

# Check if it root
if ! get_is_root; then
    msg_run_as_root
    exec sudo "$0" "$@"
fi

apt -qq update
echo "Installing Auditd..."
apt -qq -y install auditd

echo "Enabling Auditd..."
systemctl start auditd
systemctl enable auditd

# Rules? https://github.com/Neo23x0/auditd/blob/master/audit.rules
echo "Install Neo23x0 Auditd rules? [y/n] (default: y) "
read -r user_input
if [[ -z "$user_input" ]]; then
    user_input="y"
fi
user_input="${user_input,,}" #lowercase convertion

if [[ "$user_input" == "y" ]]; then
    apt -qq -y install wget
    wget -P /etc/audit/audit.rules https://raw.githubusercontent.com/Neo23x0/auditd/refs/heads/master/audit.rules
    augenrules --load
    auditctl -l
fi

echo "Enabling Auditd..."
systemctl start auditd
systemctl enable auditd
