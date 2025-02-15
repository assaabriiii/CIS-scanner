#!/bin/bash
# Module: Cron Security Hardening
# Description: Secures cron configuration according to CIS benchmarks

LOG_FILE="/var/log/hardening_script.log"
CRON_DIRS=("/etc/cron.hourly" "/etc/cron.daily" "/etc/cron.weekly" "/etc/cron.monthly" "/etc/cron.d")

log() {
  echo "[$(date +%Y-%m-%dT%H:%M:%S)] $1" | tee -a "$LOG_FILE"
}

log "Starting Cron Security Hardening..."

# Ensure cron is installed and enabled
apt-get install -y cron && systemctl enable cron
log "Cron installed and enabled."

# Remove cron.deny and at.deny
rm -f /etc/cron.deny /etc/at.deny
log "Removed cron.deny and at.deny files."

# Create cron.allow and at.allow with restrictive permissions
touch /etc/cron.allow /etc/at.allow
chmod 600 /etc/cron.allow /etc/at.allow
chown root:root /etc/cron.allow /etc/at.allow
log "Created and secured cron.allow and at.allow files."

# Secure cron directories
for dir in "${CRON_DIRS[@]}"; do
  if [[ -d "$dir" ]]; then
    chmod 700 "$dir"
    chown root:root "$dir"
    log "Secured directory: $dir"
  fi
done

# Secure cron files
chmod 600 /etc/crontab
chown root:root /etc/crontab
log "Secured /etc/crontab"

# Configure periodic jobs security
for file in /etc/cron.*/*; do
  if [[ -f "$file" ]]; then
    chmod 700 "$file"
    chown root:root "$file"
    log "Secured cron job: $file"
  fi
done

log "Cron Security Hardening completed." 