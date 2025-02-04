#!/bin/bash
# Module: Core Dumps Security
# Description: Disables core dumps according to CIS benchmarks

LOG_FILE="/var/log/hardening_script.log"
LIMITS_CONF="/etc/security/limits.conf"
SYSCTL_CONF="/etc/sysctl.d/50-coredump.conf"
SYSTEMD_CONF="/etc/systemd/coredump.conf"

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

log "Starting Core Dumps Security Configuration..."

# Backup configuration files
backup_file "$LIMITS_CONF"
backup_file "$SYSCTL_CONF"
backup_file "$SYSTEMD_CONF"

# Disable core dumps in limits.conf
echo "* hard core 0" >> "$LIMITS_CONF"
log "Disabled core dumps in limits.conf"

# Disable core dumps in sysctl
cat > "$SYSCTL_CONF" <<EOF
fs.suid_dumpable = 0
kernel.core_pattern=|/bin/false
EOF
sysctl -p "$SYSCTL_CONF"
log "Disabled core dumps in sysctl"

# Disable core dumps in systemd
cat > "$SYSTEMD_CONF" <<EOF
[Coredump]
Storage=none
ProcessSizeMax=0
EOF
systemctl daemon-reload
log "Disabled core dumps in systemd"

# Mask systemd-coredump service
systemctl mask systemd-coredump.socket
log "Masked systemd-coredump.socket"

log "Core Dumps Security Configuration completed." 