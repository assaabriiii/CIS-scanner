#!/bin/bash
# Module: GRUB Security Hardening
# Description: Secures GRUB bootloader configuration according to CIS benchmarks

LOG_FILE="/var/log/hardening_script.log"
GRUB_CONFIG="/etc/default/grub"
GRUB_CUSTOM="/etc/grub.d/40_custom"

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

log "Starting GRUB Security Hardening..."

# Backup GRUB configuration
backup_file "$GRUB_CONFIG"

# Set GRUB password
if ! grep -q "^GRUB_PASSWORD" "$GRUB_CONFIG"; then
  log "Generating GRUB password..."
  GRUB_PW=$(grub-mkpasswd-pbkdf2 | grep "grub.pbkdf2.*" | awk '{print $NF}')
  
  # Add password protection to GRUB
  cat >> "$GRUB_CUSTOM" <<EOF
set superusers="root"
password_pbkdf2 root $GRUB_PW
EOF
  log "GRUB password protection configured."
fi

# Configure GRUB security parameters
sed -i 's/^GRUB_CMDLINE_LINUX=.*/GRUB_CMDLINE_LINUX="ipv6.disable=1 audit=1 audit_backlog_limit=8192 init_on_alloc=1 init_on_free=1 page_alloc.shuffle=1 pti=on randomize_kstack_offset=on vsyscall=none"/' "$GRUB_CONFIG"

# Disable GRUB recovery mode
sed -i 's/^GRUB_DISABLE_RECOVERY=.*/GRUB_DISABLE_RECOVERY="true"/' "$GRUB_CONFIG"

# Update GRUB configuration
update-grub && log "GRUB configuration updated successfully."

log "GRUB Security Hardening completed." 