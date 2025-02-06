#!/bin/bash
# Module: System Logging Security
# Description: Configures secure system logging according to CIS benchmarks

LOG_FILE="/var/log/hardening_script.log"
RSYSLOG_CONF="/etc/rsyslog.conf"
LOGROTATE_CONF="/etc/logrotate.conf"

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

log "Starting System Logging Security Configuration..."

# Install required packages
apt-get install -y rsyslog logrotate
log "Installed required logging packages"

# Backup configuration files
backup_file "$RSYSLOG_CONF"
backup_file "$LOGROTATE_CONF"

# Configure rsyslog
cat > "$RSYSLOG_CONF" <<EOF
# Log all kernel messages
kern.*                                                  /var/log/kern.log

# Log authentication and authorization events
auth,authpriv.*                                        /var/log/auth.log

# Log all system messages
*.info;auth,authpriv.none                              /var/log/syslog

# Log emergency messages to all users
*.emerg                                                :omusrmsg:*

# Log boot events
local7.*                                               /var/log/boot.log

# Set file permissions on creation
\$FileCreateMode 0640
\$DirCreateMode 0750
EOF

# Configure logrotate
cat > "$LOGROTATE_CONF" <<EOF
weekly
rotate 13
create
dateext
compress
notifempty
missingok
nomail
size 100M
EOF

# Set permissions on log files
chmod 640 /var/log/syslog
chmod 640 /var/log/auth.log
chmod 640 /var/log/kern.log
chmod 640 /var/log/boot.log
log "Set secure permissions on log files"

# Create log directories if they don't exist
mkdir -p /var/log/audit
chmod 750 /var/log/audit
chown root:root /var/log/audit
log "Created and secured audit log directory"

# Restart rsyslog service
systemctl restart rsyslog
log "Restarted rsyslog service"

log "System Logging Security Configuration completed." 