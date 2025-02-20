### `account.sh`

```
CIS 24.04
7.2.1
5.4.2.1
5.3.3.1.3
```

find UIDs less then 1000, that means it's reserved for system users and services, which made by OS or installed apps like Daemon and nobody, this script locks them to prevent unauthorized access

and then checks for empty passwords (UID >= 1000) if they dont have password locks them

modify the `/etc/login.defs` for enforcing string passwords:

    maximum password age to 90 days.
    Sets the minimum password age to 7 days
    Sets a warning period of 14 days before password expiration
    Ensures that the password encryption method is set to SHA512


It sets a password expiration policy for all user accounts (with UID 1000 or greater) that have been inactive for 30 days.


### `aide.sh`

```
CIS 24.04
6.3.1: page 924
```

AIDE: monitor changes to the filesystem

The script initializes the AIDE database using the aideinit command. This process may take some time. If successful, it moves the newly created database to the expected location (/var/lib/aide/aide.db) and logs the success. If it fails, it logs an error and exits.

The script creates a new script (/usr/local/bin/aide_check.sh) that runs the AIDE check command and logs the output to a separate log file (/var/log/aide_check.log).

It checks if this check script is already scheduled in the crontab. If not, it adds a cron job to run the check daily at 3 AM. If it is already scheduled, it logs that information.


### `apparmor.sh`

```
CIS 24.04
1.3.1.1-4
```

The install_apparmor function updates the package list and installs AppArmor and its utilities. It uses the validate_change function to log the success or failure of the installation.

The configure_grub_for_apparmor function checks the GRUB configuration file (/etc/default/grub) to see if AppArmor is already enabled. If not, it modifies the GRUB configuration to enable AppArmor and updates GRUB. It also creates a backup of the GRUB configuration file before making changes.

The set_profiles_to_complain_mode function sets all active AppArmor profiles to "complain mode." In this mode, violations of the profile rules are logged but not enforced, allowing administrators to review the logs and adjust profiles as needed. The function checks for active profiles and applies the change using the aa-complain command.


### `audit.sh`

```
CIS 24.04
6.2.3.20
6.2.4.1-10
```

auditd: responsible for writing audit records to the disk

The script logs the start of the installation process for auditd and attempts to install it using apt-get. If the installation is successful, it logs a success message; otherwise, it logs an error and exits the script.

The script backs up existing audit rules and configuration files (/etc/audit/audit.rules and /etc/audit/auditd.conf) using the backup_file function. This ensures that the original configurations can be restored if needed.

The script writes a set of audit rules to the AUDIT_RULES_FILE (/etc/audit/audit.rules). These rules define what events should be logged by the audit system, such as file access, user modifications, and system calls. The rules cover a wide range of system activities to ensure comprehensive monitoring.

The script modifies the auditd configuration file (/etc/audit/auditd.conf) to enhance logging settings. It updates parameters like num_logs, max_log_file, and max_log_file_action to control log retention and management.

After making changes to the configuration and rules, the script restarts the auditd service to apply the new settings. It logs whether the restart was successful or if it failed.


### `auth.sh`

```
CIS 24.04
6.1.2.1.2
5.1.9
5.2.5
5.2.6
```

The provided Bash script (auth.sh) is designed to harden system authentication settings according to the Center for Internet Security (CIS) benchmarks

/etc/login.defs: Contains user account and password settings.
/etc/pam.d/common-auth: Defines authentication methods.
/etc/pam.d/common-password: Defines password policies.

Configure login.defs:

    PASS_MAX_DAYS: Maximum number of days a password is valid (set to 90).
    PASS_MIN_DAYS: Minimum number of days before a password can be changed (set to 7).
    PASS_WARN_AGE: Number of days before password expiration to warn the user (set to 14).
    ENCRYPT_METHOD: Password encryption method (set to SHA512).
    SHA_CRYPT_MIN_ROUNDS: Minimum number of rounds for SHA-512 hashing (set to 5000).
    LOGIN_RETRIES: Maximum number of login attempts before lockout (set to 3).
    LOGIN_TIMEOUT: Time in seconds before a login attempt times out (set to 60).
    UMASK: Default file creation permissions (set to 027).
    USERGROUPS_ENAB: Enables user groups (set to yes).

Configure PAM Password Requirements:

    The script modifies the common-password file to set password quality requirements using the pam_pwquality module. It specifies:

        Minimum password length of 14 characters.
        At least one digit, one uppercase letter, one lowercase letter, and one special character.
        A minimum of 4 character classes must be used.
        A maximum of 3 repeated characters.

Configure PAM Authentication:

    The script appends additional authentication settings to the common-auth file:

        pam_tally2.so: Locks the account after 5 failed login attempts for 15 minutes.
        pam_faildelay.so: Introduces a delay of 4 seconds after a failed login attempt.

Install and Configure Password Quality Checking:

    The script installs the libpam-pwquality package, which provides password quality checking.
    It creates a configuration file (/etc/security/pwquality.conf) to define password quality parameters, including minimum length and character requirements.


### `cron.sh`

```
CIS 24.04
2.4.1.2-8: page 333
2.4.1.1
```

Ensure Cron is Installed and Enabled

The script removes the cron.deny and at.deny files, which can restrict users from scheduling cron jobs. By removing these files, it ensures that there are no restrictions on cron job scheduling.

The script creates cron.allow and at.allow files, which can be used to explicitly allow users to schedule cron jobs. It sets the permissions to 600 (read and write for the owner only) and changes the ownership to root:root, securing these files.

The script iterates over predefined cron directories (/etc/cron.hourly, /etc/cron.daily, /etc/cron.weekly, /etc/cron.monthly, and /etc/cron.d). For each directory, it sets the permissions to 700 (read, write, and execute for the owner only) and changes the ownership to root:root, securing these directories.

The script secures the main cron configuration file (/etc/crontab) by setting its permissions to 600 and changing its ownership to root:root.

The script iterates over all files in the cron directories (/etc/cron.*/*). For each file, it sets the permissions to 700 and changes the ownership to root:root, ensuring that only the root user can read and execute these files.


### `files.sh`

```
CIS 24.04
5.1.2-3
7.1.13
6.1.4.1
6.2.4.8-10
7.1.1-10
```

The provided Bash script (files.sh) is designed to configure secure file permissions for critical system files and directories.

The secure_permissions function takes four parameters: a file path, an owner, a group, and the desired permissions. It checks if the specified file exists and, if so, changes its ownership and permissions. If the file does not exist, it logs a message indicating that the file was not found.

Setting Secure Permissions for Critical Files:

    /etc/passwd: User account information.
    /etc/shadow: User password information (restricted access).
    /etc/group: Group account information.
    /etc/gshadow: Group password information (restricted access).
    /etc/hosts: Hostname resolution.
    /etc/issue: Pre-login message.
    /etc/issue.net: Network pre-login message.
    /etc/motd: Message of the day.

Secure Permissions for Sensitive Directories:

    /root: The home directory for the root user (restricted access).
    /var/log: Directory for log files (restricted access).


### `filesystem.sh`

```
CIS 24.04
6.3.2: page 926
1.1.1.10
```

modprobe: is a command-line utility in Linux used to manage kernel modules.

The script backs up the configuration files for disabled filesystems and modprobe settings, ensuring they exist by creating them if they do not.

The script iterates over the list of filesystems to be disabled, adding entries to the disabled-fs.conf file to prevent their installation and to the modprobe.conf file to blacklist them. It logs each action.

The script checks if each filesystem module is currently loaded in the kernel. If it is, the script attempts to unload it using modprobe -r. It logs whether the unload was successful or if the module was not loaded.


### `kernel.sh`

```
CIS 24.04
3.2.1-4
1.1.1.1-10
6.2.3.19: page 889
1.1.1.9
```

The provided Bash script (kernel.sh) is designed to apply kernel-level hardening

modifying various kernel parameters using the sysctl command

sysctl: including Linux, that is used to examine and modify kernel parameters at runtime

 The apply_sysctl_param function takes a key-value pair representing a sysctl parameter. It checks if the parameter is already in the configuration file and either adds or updates it. It then applies the parameter using sysctl -w and logs the result.

 ```bash
  params=(
     "kernel.randomize_va_space=2"
     "kernel.yama.ptrace_scope=2"
     ...
   )
```

The script defines an array of kernel parameters to be applied for hardening. These parameters include settings for address space layout randomization, process tracing, filesystem protections, network security, and more.

The script iterates over the defined parameters, splits each parameter into its key and value, and applies them using the apply_sysctl_param function.


### `limits.sh`

```
CIS 24.04
6.2.1.4: page 928
```

The provided Bash script (limits.sh) is designed to configure system resource limits and kernel parameters according to security best practices

The script appends resource limits to the limits.conf file. These limits include:

    Disabling core dumps (core 0).
    Setting the maximum number of processes (nproc) for users.
    Setting the maximum number of open files (nofile).
    Limiting the number of simultaneous logins for users.

Configure Kernel Parameters for System Limits:

    Disabling core dumps for setuid programs.
    Restricting access to kernel messages.
    Configuring kernel panic behavior.
    Enabling address space layout randomization.
    Disabling unprivileged BPF (Berkeley Packet Filter) usage.

Apply Sysctl Settings:

    The script applies the sysctl settings defined in the configuration file and logs the result.

BPF: allows users to define rules for capturing and filtering network packets


### `logging.sh`

```
CIS 24.04
6.1.3.5
6.1.1.4
6.1.3.5
```

designed to configure system logging

The script installs the rsyslog and logrotate packages, which are essential for logging and managing log files.

The script backs up the existing rsyslog and logrotate configuration files to ensure that the original settings can be restored if needed.

The script writes a new configuration to the rsyslog configuration file, specifying how different types of messages should be logged. It sets up logging for authentication messages, kernel messages, system messages, emergency messages, and boot messages.

The script writes a new configuration to the logrotate configuration file, specifying how logs should be rotated. It sets the rotation frequency to weekly, keeps 13 old logs, creates new log files, compresses old logs, and includes additional configurations from /etc/logrotate.d.

The script sets the permissions on the main log files to ensure that only the root user and the group can read and write to them, enhancing security.

The script restarts the rsyslog service to apply the new configuration.


### `ntp.sh`

```
CIS 24.04
2.3.2.1: page 312
2.3.3: page 318
2.3.3.1: page 319
2.3.2
```

The provided Bash script (ntp.sh) is designed to configure secure and accurate time synchronization settings on a Linux system using the Chrony NTP (Network Time Protocol) client
NTP: allows the synchronization of system clocks (from desktops to servers)

The script installs the Chrony package for time synchronization. If the installation is successful, it logs a success message; otherwise, it logs an error and exits.

Configure Chrony with Secure Settings:

    The script writes a new configuration to the Chrony configuration file, specifying NTP servers to use for time synchronization and restricting NTP traffic to localhost only. It also enables logging of measurements and statistics for monitoring purposes.

Restart Chrony to Apply Changes:

    The script restarts the Chrony service to apply the new configuration and logs the result.

Disable systemd-timesyncd if Active:

    If the systemd-timesyncd service is active, the script stops and disables it. This is done to prevent conflicts between Chrony and systemd's built-in time synchronization service.


### `pam.sh`

```
CIS 24.04
5.3.1.1-3
5.1.22
5.3.2.1-4
5.3.3.3.3
5.3.3.4.1-3
```

is designed to configure and harden the Pluggable Authentication Modules (PAM)

The script installs the libpam-pwquality package, which provides password quality checking. If the installation is successful, it logs a success message; otherwise, it logs an error and exits.

The script modifies the common-password configuration file to enforce strong password policies using pam_pwquality. It sets parameters such as:

    Minimum password length of 12 characters.
    At least one digit, one uppercase letter, one lowercase letter, and one special character.
    A maximum of 3 repeated characters.

The script tests the password policy by attempting to set a weak password for a test user. It expects the operation to fail, indicating that the policy is enforced.

The script tests the account lockout policy by simulating 5 failed login attempts for a test user. It checks if the user is locked out after the specified number of failures.


### `partitions.sh`

```
CIS 24.04
1.1.2: page 74
```

designed to secure temporary partitions on a Linux system, specifically /tmp, /var/tmp, and /dev/shm

Several variables are defined for logging, the path to the fstab configuration file, and the mount options for the temporary partitions:

    nodev: Prevents the interpretation of character or block device files.
    nosuid: Prevents the execution of setuid and setgid bits.
    noexec: Prevents the execution of binaries.

fstab: located in /etc/ contains descriptive information about the filesystems the system can mount.

The secure_partition function takes a partition and its corresponding options as arguments. It checks if the partition is already listed in the fstab file:

        If it is, it updates the mount options.
        If it is not, it adds a new entry for the partition.
    
    The function then attempts to remount the partition with the updated options and logs the result.

The script calls the secure_partition function for each of the temporary partitions, applying the defined restrictive options.


### `process.sh`

```
CIS 24.04
1.5.1-5
```

designed to enhance the security of a Linux system by configuring kernel parameters and removing unnecessary packages and services.

The apply_sysctl_param function takes a key-value pair representing a sysctl parameter. It checks if the parameter is already in the configuration file and either adds or updates it. It then applies the parameter using sysctl -w and logs the result.

ptrace: ptrace is a system call found in Unix and several Unix-like operating systems. By using ptrace one process can control another, enabling the controller to inspect and manipulate the internal state of its target. ptrace is used by debuggers and other code-analysis tools, mostly as aids to software development.

Kernel Parameters for Process Hardening:

    kernel.randomize_va_space=2: Enables address space layout randomization (ASLR) for all processes, making it harder for attackers to predict the location of specific functions in memory.
    kernel.yama.ptrace_scope=2: Restricts the use of the ptrace system call, which can be used for debugging and can also be exploited by attackers.
    fs.suid_dumpable=0: Prevents core dumps for setuid programs, which can contain sensitive information.

The script iterates over the defined parameters, splits each parameter into its key and value, and applies them using the apply_sysctl_param function.

The script defines an array of unnecessary packages to be removed. It checks if each package is installed and purges it if it is, logging the result.

The script defines an array of unnecessary services to be disabled. It checks if each service is active and stops it if it is, then disables it, logging the result.


### `rotate.sh`

```
CIS 24.04
6.1.3.8
6.2.2.4: page 815
```

configure auditing and logging settings on a Linux system to enhance security. It sets up the auditd service, which is responsible for monitoring and logging system events, and applies specific audit rules to track various activities on the system.

The script installs the auditd package, which is responsible for auditing. If the installation is successful, it logs a success message; otherwise, it logs an error and exits.

MAC -> mandatory: a model of access control where the operating system provides users with access based on data confidentiality and user clearance levels

The script writes a new set of audit rules to the audit.rules file. These rules specify what events to monitor, including:

    Monitoring access to critical files and directories (e.g., /etc/passwd, /etc/shadow).
    Tracking changes to system configurations and user management commands.
    Logging attempts to access sensitive files and directories.
    Monitoring for changes to the system's MAC (Mandatory Access Control) policies.

The script modifies the auditd.conf file to set the number of logs to keep, the maximum log file size, and the action to take when the maximum log file size is reached.

The script restarts the auditd service to apply the new configuration and logs the result.


### `rsyslog.sh`

```
CIS 24.04
6.1.3.1-7: page 777 and 778
```

configure and harden the logging settings of the rsyslog service on a Linux system

rsyslog: allows a system administrator to monitor and manage logs from different parts of the system

The script checks if rsyslog is installed and installs it if it is not. If the installation is successful, it logs a success message; otherwise, it logs an error and exits.

The script writes a new configuration to the rsyslog.conf file, specifying how different types of messages should be logged. It includes:

    Loading the necessary modules for socket and kernel logging.
    Directing all log messages to /var/log/messages.
    Logging authentication messages to /var/log/auth.log.
    Logging kernel messages to /var/log/kern.log.
    Logging daemon messages to /var/log/daemon.log.
    Logging general syslog messages to /var/log/syslog.

The script restricts access to the log files by removing read, write, and execute permissions for group and others. This enhances security by preventing unauthorized access to log files.

The script restarts the rsyslog service to apply the new configuration and logs the result.


### `services.sh`

```
CIS 24.04
2.1.1-20
6.1.1.1
```

enhance the security of a Linux system by disabling and removing unnecessary services

The remove_service function takes a service name as an argument and performs the following actions:

    Stops the service if it is currently active.
    Disables the service if it is enabled.
    Removes the service package if it is installed.

```bash
   SERVICES_TO_REMOVE=(
     "autofs" "avahi-daemon" "isc-dhcp-server" "bind9" "dnsmasq" "slapd"
     "dovecot-imapd" "dovecot-pop3d" "nfs-kernel-server" "ypserv" "cups"
     "rpcbind" "rsync" "samba" "snmpd" "tftpd-hpa" "squid" "apache2"
     "nginx" "xinetd" "xserver-common" "postfix" "nis" "rsh-client"
     "talk" "telnet" "inetutils-telnet" "ldap-utils" "ftp" "tnftp" "lp"
     "bluez" "gdm3" "whoopsie" "snapd"
   )
```

The script iterates over the list of services to remove, calling the remove_service function for each one.


### `ssh.sh`

```
CIS 24.04
5.1.1
5.1.5
5.1.7
5.1.10
5.1.13
5.1.16-19
5.1.21-22
```

configure the SSH (Secure Shell) service

The script defines the path to the SSH daemon configuration file (/etc/ssh/sshd_config) and backs it up.

The script writes a new configuration to the sshd_config file, specifying various security settings:

    Include: Allows additional configuration files to be included from the specified directory.
    LogLevel: Sets the verbosity of logging.
    PermitRootLogin: Disables root login via SSH for security.
    MaxAuthTries: Limits the number of authentication attempts.
    MaxSessions: Limits the number of concurrent sessions.
    IgnoreRhosts: Ignores .rhosts files for security.
    PermitEmptyPasswords: Disallows empty passwords.
    KbdInteractiveAuthentication: Disables keyboard-interactive authentication.
    UsePAM: Enables Pluggable Authentication Modules.
    AllowAgentForwarding: Disables SSH agent forwarding.
    AllowTcpForwarding: Disables TCP forwarding.
    X11Forwarding: Disables X11 forwarding.
    PrintMotd: Disables printing the message of the day.
    TCPKeepAlive: Disables TCP keepalive messages.
    ClientAliveCountMax: Sets the maximum number of client alive messages.
    ClientAliveInterval: Sets the interval for sending client alive messages.
    Banner: Specifies a banner file to display upon login.
    Ciphers: Specifies allowed ciphers for encryption.
    KexAlgorithms: Specifies key exchange algorithms.
    MACs: Specifies message authentication codes.
    DisableForwarding: Disables forwarding of connections.
    GSSAPIAuthentication: Disables GSSAPI authentication.
    HostbasedAuthentication: Disables host-based authentication.

The script attempts to restart the SSH service to apply the new configuration. It logs whether the restart was successful or if there was a failure.


### `ufw.sh`

```
CIS 24.04
4.2.1-7
4.3.2
4.4.1.3
```

designed to configure the Uncomplicated Firewall (UFW)

The script sets the default policies for UFW:

        Incoming traffic is denied by default.
        Outgoing traffic is allowed by default.

    These policies help secure the system by blocking unsolicited incoming connections while allowing outgoing connections.

The script allows SSH connections to ensure that remote access remains available. This is crucial for managing the server remotely.

~~The script for allowing HTTP and HTTPS traffic. These can be uncommented if web services are hosted on the server.~~

The script enables the UFW firewall, using the --force flag to bypass any interactive confirmation prompts.

The script outputs the current status of UFW, including active rules, to the log file.