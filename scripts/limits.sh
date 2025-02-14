#!/bin/bash
# Module: System Limits Hardening
# Description: Configures system resource limits according to CIS benchmarks

LOG_FILE="/var/log/hardening_script.log"
LIMITS_CONF="/etc/security/limits.conf"
SYSCTL_CONF="/etc/sysctl.d/99-security-limits.conf"

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

log "Starting System Limits Hardening..."

# Backup configuration files
backup_file "$LIMITS_CONF"
backup_file "$SYSCTL_CONF"

# Configure system limits
cat >> "$LIMITS_CONF" <<EOF
* hard core 0
* soft core 0
* hard nproc 1024
* soft nproc 512
* hard nofile 65535
* soft nofile 65535
* hard maxlogins 10
root hard core 0
root soft core 0
EOF

# Configure kernel parameters for system limits
cat > "$SYSCTL_CONF" <<EOF
fs.suid_dumpable = 0
kernel.core_uses_pid = 1
kernel.dmesg_restrict = 1
kernel.panic = 60
kernel.panic_on_oops = 60
kernel.perf_event_paranoid = 3
kernel.randomize_va_space = 2
kernel.sysrq = 0
kernel.unprivileged_bpf_disabled = 1
net.core.bpf_jit_harden = 2
vm.panic_on_oom = 0
vm.swappiness = 10
EOF

# Apply sysctl settings
sysctl -p "$SYSCTL_CONF" && log "System limits applied successfully."

log "System Limits Hardening completed." 