#!/bin/bash
# Module: Time Synchronization Hardening
# Description: Configures secure time synchronization according to CIS benchmarks

LOG_FILE="/var/log/hardening_script.log"
TIMESYNCD_CONF="/etc/systemd/timesyncd.conf"
CHRONY_CONF="/etc/chrony/chrony.conf"

log() {
  echo "[$(date +%Y-%m-%dT%H:%M:%S)] $1" | tee -a "$LOG_FILE"
}

backup_file() {
  local file="$1"
  if [[ -f "$file" ]]; then
    cp "$file" "${file}.bak" && log "Backup created for $file"
  else
    log "File $file not found, skipping backup."
  fi
}

log "Starting Time Synchronization Hardening..."

# Install chrony
apt-get install -y chrony
systemctl enable chronyd

# Backup configuration files
backup_file "$CHRONY_CONF"
backup_file "$TIMESYNCD_CONF"

# Configure chrony
cat > "$CHRONY_CONF" <<EOF
pool 2.ubuntu.pool.ntp.org iburst maxsources 4
keyfile /etc/chrony/chrony.keys
driftfile /var/lib/chrony/chrony.drift
logdir /var/log/chrony
maxupdateskew 100.0
rtcsync
makestep 1 3
leapsectz right/UTC
EOF

# Set restrictive permissions
chown -R root:root /etc/chrony
chmod -R 640 /etc/chrony
chmod 750 /var/lib/chrony

# Stop and disable systemd-timesyncd
systemctl stop systemd-timesyncd
systemctl disable systemd-timesyncd

# Restart chrony
systemctl restart chronyd

log "Time Synchronization Hardening completed." 