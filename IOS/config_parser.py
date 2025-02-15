import paramiko
import re
import time
from getpass import getpass

def get_variables_from_command(command):
    """Extract variables enclosed in <> from a command"""
    return re.findall(r'<([^>]+)>', command)

def prompt_for_variables(variables):
    """Ask user for values for each variable"""
    values = {}
    for var in variables:
        if 'PASSWORD' in var:
            values[var] = getpass(f"Enter {var.replace('_', ' ').lower()}: ")
        else:
            values[var] = input(f"Enter {var.replace('_', ' ').lower()}: ")
    return values

def replace_variables(command, values):
    """Replace variables in command with user-provided values"""
    result = command
    for var, value in values.items():
        result = result.replace(f'<{var}>', value)
    return result

def connect_to_switch():
    """Establish SSH connection to the switch"""
    print("\n=== SSH Connection Setup ===")
    hostname = input("Enter switch IP address: ")
    username = input("Enter username: ")
    password = getpass("Enter password: ")

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh_client.connect(hostname, username=username, password=password)
        print("Successfully connected to the switch!")
        return ssh_client
    except Exception as e:
        print(f"Failed to connect: {str(e)}")
        return None

def execute_command(ssh_client, command):
    """Execute a command on the switch"""
    stdin, stdout, stderr = ssh_client.exec_command(command)
    time.sleep(1)  # Give some time for command execution
    return stdout.read().decode()

def get_user_choice():
    """Get user choice for command execution"""
    while True:
        choice = input("Choose action (e)xecute/(s)kip/(q)uit: ").lower()
        if choice in ['e', 's', 'q']:
            return choice
        print("Invalid choice. Please enter 'e' for execute, 's' for skip, or 'q' for quit.")

def main():
    print("=== Cisco Switch Configuration Tool ===")
    
    # Connect to switch
    ssh_client = connect_to_switch()
    if not ssh_client:
        return

    # Read the commands file
    with open('codes.txt', 'r') as f:
        content = f.read()

    # Split into individual command blocks
    command_blocks = content.split('\n\n')

    for block in command_blocks:
        if block.strip() and not block.startswith('#'):
            print("\n" + "="*50)
            print("Command Description:")
            # Show the command with description
            print(block.strip())
            
            # Extract actual commands (lines that don't start with #)
            commands = [line.strip() for line in block.split('\n') 
                       if line.strip() and not line.strip().startswith('#')]
            
            for command in commands:
                if '<' in command and '>' in command:
                    print("\nCurrent command:")
                    print(f"Original command: {command}")
                    
                    choice = get_user_choice()
                    
                    if choice == 'q':
                        print("\nExiting program...")
                        ssh_client.close()
                        return
                    elif choice == 's':
                        print("Skipping command...")
                        continue
                    
                    # Get variables needed
                    variables = get_variables_from_command(command)
                    
                    # Get values from user
                    values = prompt_for_variables(variables)
                    
                    # Replace variables with values
                    final_command = replace_variables(command, values)
                    
                    print(f"Final command: {final_command}")
                    
                    try:
                        result = execute_command(ssh_client, final_command)
                        print("Command output:", result)
                    except Exception as e:
                        print(f"Error executing command: {str(e)}")
                    
                    input("Press Enter to continue...")

    ssh_client.close()
    print("\nConnection closed.")

if __name__ == "__main__":
    main() 