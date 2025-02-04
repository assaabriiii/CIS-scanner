#!/bin/bash
# Module: System Logging Hardening
# Description: Configures system logging according to CIS benchmarks

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

log "Starting System Logging Hardening..."

# Install required packages
apt-get install -y rsyslog logrotate

# Backup configuration files
backup_file "$RSYSLOG_CONF"
backup_file "$LOGROTATE_CONF"

# Configure rsyslog
cat > "$RSYSLOG_CONF" <<EOF
# Log auth messages
auth,authpriv.*                 /var/log/auth.log
# Log all kernel messages
kern.*                          /var/log/kern.log
# Log all system messages
*.info;auth,authpriv.none      /var/log/syslog
# Log emergency messages
*.emerg                        :omusrmsg:*
# Log boot messages
local7.*                       /var/log/boot.log
EOF

# Configure logrotate
cat > "$LOGROTATE_CONF" <<EOF
weekly
rotate 13
create
dateext
compress
include /etc/logrotate.d
notifempty
nomail
noolddir
missingok
size=100M
EOF

# Set permissions on log files
chmod 640 /var/log/syslog
chmod 640 /var/log/auth.log
chmod 640 /var/log/kern.log
chmod 640 /var/log/boot.log

# Restart rsyslog
systemctl restart rsyslog

log "System Logging Hardening completed." 