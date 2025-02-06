#!/bin/bash
# Module: Users and Groups Security
# Description: Configures secure user and group settings according to CIS benchmarks

LOG_FILE="/var/log/hardening_script.log"

log() {
  echo "[$(date +%Y-%m-%dT%H:%M:%S)] $1" | tee -a "$LOG_FILE"
}

log "Starting Users and Groups Security Configuration..."

# Set secure umask for users
echo "umask 027" > /etc/profile.d/umask.sh
chmod 644 /etc/profile.d/umask.sh
log "Set secure umask for users"

# Lock system accounts
for user in $(awk -F: '($3 < 1000) {print $1 }' /etc/passwd); do
  if [ "$user" != "root" ]; then
    usermod -L "$user"
    log "Locked system account: $user"
  fi
done

# Set strong password requirements
sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS 90/' /etc/login.defs
sed -i 's/^PASS_MIN_DAYS.*/PASS_MIN_DAYS 7/' /etc/login.defs
sed -i 's/^PASS_WARN_AGE.*/PASS_WARN_AGE 14/' /etc/login.defs
log "Updated password aging controls"

# Verify no legacy "+" entries
sed -i '/^+/d' /etc/passwd /etc/shadow /etc/group
log "Removed legacy '+' entries from passwd/shadow/group files"

# Set default group for root account
usermod -g 0 root
log "Set root's default group to GID 0"

# Verify root is only member of GID 0
for group in $(groups root); do
  if [ "$group" != "root" ]; then
    gpasswd -d root "$group"
    log "Removed root from group: $group"
  fi
done

# Set secure permissions on user/group files
chmod 644 /etc/passwd
chmod 000 /etc/shadow
chmod 644 /etc/group
chmod 000 /etc/gshadow
log "Set secure permissions on user/group files"

log "Users and Groups Security Configuration completed." 