#!/bin/bash
# Module: System Banners Hardening
# Description: Configures system banners and warning messages according to CIS benchmarks

LOG_FILE="/var/log/hardening_script.log"
ISSUE_FILE="/etc/issue"
ISSUE_NET_FILE="/etc/issue.net"
MOTD_FILE="/etc/motd"

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

log "Starting System Banners Hardening..."

# Backup banner files
backup_file "$ISSUE_FILE"
backup_file "$ISSUE_NET_FILE"
backup_file "$MOTD_FILE"

# Create secure banner content
BANNER_TEXT="Authorized users only. All activity may be monitored and reported."

# Configure login banner
echo "$BANNER_TEXT" > "$ISSUE_FILE"
echo "$BANNER_TEXT" > "$ISSUE_NET_FILE"
echo "$BANNER_TEXT" > "$MOTD_FILE"

# Set secure permissions
chmod 644 "$ISSUE_FILE" "$ISSUE_NET_FILE" "$MOTD_FILE"
chown root:root "$ISSUE_FILE" "$ISSUE_NET_FILE" "$MOTD_FILE"

# Remove system information from banners
sed -i 's/\\[a-zA-Z]//g' "$ISSUE_FILE"
sed -i 's/\\[a-zA-Z]//g' "$ISSUE_NET_FILE"

log "System Banners Hardening completed." 