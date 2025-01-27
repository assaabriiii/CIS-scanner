#!/bin/bash
# Module: Kernel Hardening
# Description: Applies kernel-level hardening using sysctl parameters

LOG_FILE="/var/log/hardening_script.log"
BACKUP_SUFFIX=".bak"
SYSCTL_CONF="/etc/sysctl.conf"

log() {
  echo "[$(date +%Y-%m-%dT%H:%M:%S)] $1" | tee -a "$LOG_FILE"
}

backup_file() {
  local file="$1"
  if [[ -f "$file" ]]; then
    cp "$file" "${file}${BACKUP_SUFFIX}" && log "Backup created for $file"
  else
    log "File $file not found, skipping backup."
  fi
}

apply_sysctl_param() {
  local key="$1"
  local value="$2"
  if ! grep -q "^$key" "$SYSCTL_CONF"; then
    echo "$key = $value" >> "$SYSCTL_CONF"
  else
    sed -i "s/^$key.*/$key = $value/" "$SYSCTL_CONF"
  fi
  if sysctl -w "$key=$value"; then
    log "Applied sysctl parameter: $key=$value"
  else
    log "Failed to apply sysctl parameter: $key=$value"
  fi
}

# Backup sysctl configuration
backup_file "$SYSCTL_CONF"

# Kernel Hardening Parameters
params=(
  "kernel.randomize_va_space=2"
  "kernel.yama.ptrace_scope=2"
)

for param in "${params[@]}"; do
  IFS="=" read -r key value <<< "$param"
  apply_sysctl_param "$key" "$value"
done

log "Kernel hardening parameters applied."

echo "Kernel Hardening Completed."