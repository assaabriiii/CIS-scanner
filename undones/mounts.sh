#!/bin/bash
# Module: Mount Points Security
# Description: Secures mount points and filesystem options according to CIS benchmarks

LOG_FILE="/var/log/hardening_script.log"
FSTAB="/etc/fstab"

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

log "Starting Mount Points Security Configuration..."

# Backup fstab
backup_file "$FSTAB"

# Function to add or update mount options
update_mount_options() {
    local mount_point="$1"
    local options="$2"
    
    if grep -q "^[^#].*\s${mount_point}\s" "$FSTAB"; then
        sed -i "s|\([^#].*\s\)${mount_point}\s.*|\1${mount_point} ${options}|" "$FSTAB"
        log "Updated mount options for $mount_point"
    else
        echo "tmpfs ${mount_point} tmpfs ${options} 0 0" >> "$FSTAB"
        log "Added new mount entry for $mount_point"
    fi
}

# Configure secure mount options
update_mount_options "/tmp" "defaults,rw,nosuid,nodev,noexec,relatime 0 0"
update_mount_options "/var/tmp" "defaults,rw,nosuid,nodev,noexec,relatime 0 0"
update_mount_options "/dev/shm" "defaults,rw,nosuid,nodev,noexec,relatime 0 0"
update_mount_options "/home" "defaults,rw,nosuid,relatime 0 2"

# Remount all filesystems
mount -a
log "Remounted all filesystems with updated options"

log "Mount Points Security Configuration completed." 