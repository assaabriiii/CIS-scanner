#!/bin/bash
# Module: System Modules Security
# Description: Secures kernel modules according to CIS benchmarks

LOG_FILE="/var/log/hardening_script.log"
MODULES_DIR="/etc/modprobe.d"

log() {
  echo "[$(date +%Y-%m-%dT%H:%M:%S)] $1" | tee -a "$LOG_FILE"
}

log "Starting System Modules Security Configuration..."

# Create blacklist configuration file
BLACKLIST_CONF="$MODULES_DIR/cis-blacklist.conf"
touch "$BLACKLIST_CONF"

# List of modules to blacklist
BLACKLIST_MODULES=(
    "cramfs"
    "freevxfs"
    "jffs2"
    "hfs"
    "hfsplus"
    "squashfs"
    "udf"
    "usb-storage"
    "dccp"
    "sctp"
    "rds"
    "tipc"
)

# Blacklist modules
for module in "${BLACKLIST_MODULES[@]}"; do
    if ! grep -q "^install $module /bin/true" "$BLACKLIST_CONF"; then
        echo "install $module /bin/true" >> "$BLACKLIST_CONF"
        echo "blacklist $module" >> "$BLACKLIST_CONF"
        log "Blacklisted module: $module"
    fi
done

# Unload modules if they're currently loaded
for module in "${BLACKLIST_MODULES[@]}"; do
    if lsmod | grep -q "^$module"; then
        modprobe -r "$module"
        log "Unloaded module: $module"
    fi
done

# Update module dependencies
depmod -a
log "Updated module dependencies"

log "System Modules Security Configuration completed." 