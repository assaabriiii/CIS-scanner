import subprocess
import re
import json
import logging
import argparse
import os
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import paramiko
from getpass import getpass

# Set up argument parser
# The above code is creating an ArgumentParser object from the argparse module in Python. It is
# setting the description of the parser to be 'System Scanner based on JSON configuration.'. This
# parser will be used to parse command-line arguments provided to the script.
parser = argparse.ArgumentParser(description='System Scanner based on JSON configuration.')
parser.add_argument('-c', '--config', required=True, help='Path to the JSON configuration file.')
parser.add_argument('-l', '--log', default='scanner.log', help='Path to the log file.')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.')
args = parser.parse_args()

# Set up logging
logging.basicConfig(
    filename=args.log,
    # The code snippet is setting the logging level to `DEBUG` if the `args.verbose` is `True`,
    # otherwise it sets the logging level to `INFO`.
    level=logging.DEBUG if args.verbose else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def execute_command_ssh(ssh, command, password):
    print(command)
    command = "sudo -S -p '' %s" % command
    
    stdin, stdout, stderr = ssh.exec_command(command)
    stdin.write(f"{password}" + "\n")
    stdin.flush()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print(output)
    print(error)
    return output, error

def execute_script_ssh(ssh, local_script_path, remote_script_path, password):
    # Upload the script to the remote server
    sftp = ssh.open_sftp()
    sftp.put(local_script_path, remote_script_path)
    
    # Make the script executable
    execute_command_ssh(ssh, f"chmod +x {remote_script_path}", password)

    # Execute the script
    output, error = execute_command_ssh(ssh, "/home/amir/" + remote_script_path, password)
    
    # Remove the script from the remote server after execution
    # execute_command_ssh(ssh, f"rm {remote_script_path}")

    return output, error


def clean_command(cmd):
    """
    The `clean_command` function removes excessive escaping and fixes escaped quotes in a given command
    string.
    
    :param cmd: It looks like the `cmd` parameter is a string representing a command that may contain
    excessive escaping. The `clean_command` function is designed to clean up this excessive escaping by
    removing extra backslashes and fixing escaped quotes
    :return: The `clean_command` function returns the cleaned version of the input command after
    removing excessive escaping, fixing escaped quotes, and printing the fixed command.
    """
    try:
        cmd = cmd.encode().decode('unicode_escape')
    except: 
        cmd = re.sub(r'\\', r'', cmd)
        cmd = re.sub(r"\\\h", "\\\h", cmd)
        cmd = re.sub(r"\\\s+", "\\\s+", cmd)
        cmd = cmd.replace('\\"', '"') 
        cmd = cmd.replace("\'",  "'") # Fix escaped quotes
        
    cmd = re.sub(r'\\\\+', r'\\', cmd)  # Remove excessive backslashes

    return cmd

from tqdm import tqdm
import time

def execute_command(cmd, desc):
    """
    The `execute_command` function executes a shell command, handling bash scripts and regular commands
    differently.
    
    :param cmd: The `execute_command` function takes a shell command as input and executes it. If the
    command starts with `#!/bin/bash`, it is treated as a bash script and executed accordingly.
    Otherwise, the command is executed using `subprocess.getoutput()`
    :return: The function `execute_command` returns the output of the executed shell command.
    """
    cmd = clean_command(cmd)
    if cmd.startswith('#!/bin/bash'):
        logging.info('Command starts with #!/bin/bash, executing as a bash script.')
        script_file = 'temp_script.sh'
        with open(script_file, 'w') as file:
            file.write(cmd)
        
        with tqdm(total=100, desc=f"{desc}") as pbar:
            result = subprocess.run(['/bin/bash', script_file], capture_output=True, text=True)
            for _ in range(10):
                time.sleep(0.01)  # Simulating progress
                pbar.update(10)
        result = result.stdout
        os.remove(script_file)
    else:
        logging.info('Executing command: %s', cmd)
        
        with tqdm(total=100, desc=f"{desc}") as pbar:
            result = subprocess.getoutput(cmd)
            for _ in range(10):
                time.sleep(0.01)  # Simulating progress
                pbar.update(10)
    
    os.system("clear")
    
    return result, cmd 



def execute_command_over_ssh(cmd, desc, ssh, password):
    """
    The `execute_command` function executes a shell command, handling bash scripts and regular commands
    differently.
    
    :param cmd: The `execute_command` function takes a shell command as input and executes it. If the
    command starts with `#!/bin/bash`, it is treated as a bash script and executed accordingly.
    Otherwise, the command is executed using `subprocess.getoutput()`
    :return: The function `execute_command` returns the output of the executed shell command.
    """
    cmd = clean_command(cmd)
    if cmd.startswith('#!/bin/bash'):
        logging.info('Command starts with #!/bin/bash, executing as a bash script.')
        script_file = 'temp_script.sh'
        with open(script_file, 'w') as file:
            file.write(cmd)
        
        with tqdm(total=100, desc=f"{desc}") as pbar:
            # result = subprocess.run(['/bin/bash', script_file], capture_output=True, text=True)
            result, error = execute_script_ssh(ssh, script_file, script_file, password)
            for _ in range(10):
                time.sleep(0.01)  # Simulating progress
                pbar.update(10)
        # result = result.stdout
        os.remove(script_file)
    else:
        logging.info('Executing command: %s', cmd)
        
        with tqdm(total=100, desc=f"{desc}") as pbar:
            # result = subprocess.getoutput(cmd)
            result, error = execute_command_ssh(ssh, cmd, password)
            for _ in range(10):
                time.sleep(0.01)  # Simulating progress
                pbar.update(10)
    
    # os.system("clear")
    
    return result, cmd 



def fix_regex(regex):
    """
    The `fix_regex` function corrects corrupted regular expressions by removing excessive escaping.
    
    :param regex: It looks like you have not provided the value for the `regex` parameter. Please
    provide the regex pattern that needs to be fixed so that I can assist you in correcting it
    :return: The function `fix_regex` returns the fixed regex after removing excessive escaping.
    """
    # regex = re.sub(r"\\\s+", "\\\s+", regex)
    # regex = re.sub(r"\\\h+", "\\\h+", regex)
    
    regex = re.sub(r'\\\\', r'\\', regex)
    regex = regex.replace(r"\h", r"\s")
    # r"\h"
    # regex = re.sub(r"\\h+", r"\t\p{Zs}+", regex)
    return regex

def check_output(output, expect):
    """
    The function `check_output` compares the output with an expected value using regular expressions and
    returns True if they match.
    
    :param output: It seems like you have not provided the `output` parameter for the `check_output`
    function. Please provide the actual output that you want to check against the expected value
    :param expect: It seems like you were about to provide the value for the `expect` parameter in the
    `check_output` function. Please go ahead and provide the value you want to use for the `expect`
    parameter so that I can assist you further
    :return: The function `check_output` is returning a boolean value - `True` if the regular expression
    pattern `fixed_expect` is found in the `output` string, and `False` otherwise.
    """
    fixed_expect = fix_regex(expect)
    
    if re.search(fixed_expect, output, re.MULTILINE):
        return True
    else: 
        return False

def generate_html_report(results, logo_path, filename='report.html'):
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64
    from datetime import datetime

    # Read the logo image and convert to base64
    with open(logo_path, "rb") as logo_file:
        logo_base64 = base64.b64encode(logo_file.read()).decode('utf-8')

    total_tests = len(results)
    passed_tests = sum(1 for result in results if result['status'] == 'passed')
    failed_tests = sum(1 for result in results if result['status'] == 'failed')
    manual_tests = sum(1 for result in results if result['status'] == 'manual')

    # Generate pie chart
    fig, ax = plt.subplots()
    fig.patch.set_facecolor('#1e1e1e')
    ax.patch.set_facecolor('#1e1e1e')
    ax.pie([passed_tests, failed_tests, manual_tests], labels=['Passed', 'Failed', 'Manual'], autopct='%1.1f%%', colors=['#4CAF50', '#F44336', '#1eabe9'])
    ax.set_title('Test Results')

    # Save plot to a PNG image in memory
    img_data = BytesIO()
    plt.savefig(img_data, format='png', facecolor=fig.get_facecolor())
    img_data.seek(0)
    img_base64 = base64.b64encode(img_data.read()).decode('utf-8')
    plt.close(fig)

    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Scan Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #1e1e1e;
                color: #ccc;
            }}
            h1, h2 {{
                color: #ccc;
            }}
            .chart {{
                text-align: center;
                margin: 20px 0;
            }}
            .results {{
                margin: 20px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                color: #ccc;
            }}
            th, td {{
                border: 1px solid #444;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #333;
                color: #ccc;
            }}
            tr:nth-child(odd) {{
                background-color: #2e2e2e;
            }}
            tr:nth-child(even) {{
                background-color: #3e3e3e;
            }}
            pre {{
                background-color: #2e2e2e;
                padding: 10px;
                border: 1px solid #444;
                overflow: auto;
                color: #ccc;
            }}
            code {{
                background-color: #2e2e2e;
                padding: 5px;
                border-radius: 3px;
                color: #ccc;
            }}
            .summary {{
                background-color: #2e2e2e;
                border: 1px solid #444;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.5);
            }}
            .logo {{
                display: block;
                margin-left: auto;
                margin-right: auto;
                width: 100px;
                margin-bottom: 20px;
            }}
        </style>
        <script>
            function toggleSolution(id) {{
                var elem = document.getElementById(id);
                if (elem.style.display === 'none') {{
                    elem.style.display = 'block';
                }} else {{
                    elem.style.display = 'none';
                }}
            }}
        </script>
    </head>
    <body>
        <img src="data:image/png;base64,{logo_base64}" alt="Logo" class="logo">
        <h1>Scan Report</h1>
        <p>Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div class="chart">
            <h2>Test Results</h2>
            <img src="data:image/png;base64,{img_base64}" alt="Test Results Chart">
        </div>
        <div class="summary">
            <h2>Summary</h2>
            <p>Total tests run: {total_tests}</p>
            <p>Passed: {passed_tests}</p>
            <p> Manual: {manual_tests}</p>
            <p>Failed: {failed_tests}</p>
        </div>
        <div class="results">
            <h2>Detailed Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Information</th>
                        <th>Result</th>
                        <th>Output</th>
                        <th>Solution</th>
                    </tr>
                </thead>
                <tbody>
    """

    for idx, result in enumerate(results):
        sol = str(result.get('solution', 'N/A')).replace("\n", "<br>")
        html_content += f"""
            <tr>
                <td>{result['description']}</td>
                <td>{result['info']}</td>
                <td style="color: {'#4CAF50' if result['status'] == 'passed' else '#F44336'};">{result['status'].capitalize()}</td>
                <td><pre>{result['output']}</pre></td>
                <td>
                    <button onclick="toggleSolution('solution-{idx}')">Show</button>
                    <div id="solution-{idx}" style="display:none;">
                        <code>{sol}</code>
                    </div>
                </td>
            </tr>
        """

    html_content += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    with open(filename, 'w') as file:
        file.write(html_content)

def main():
    ssh_flag = False
    choice = input("Execute over (ssh/local): ")
    if choice == "ssh": 
        try: 
            # hostname = input("Enter your hostname IP addr: ")
            hostname = "212.33.202.241"
            # port = int(input("Enter your port number: "))
            port = 4242
            # username = input("Enter your username: ")
            username = "amir"
            # password = getpass(f"Enter password for {username.strip()}@{hostname.strip()}:{port}: ")
            password = "Amir@1403"
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, port, username, password)
            ssh_flag = True
        except Exception as e: 
            print(e)
    
    # Initialize SSH client
    
    """
    The main function processes custom items from a JSON configuration, executes commands, checks output
    against expected patterns, and generates a test summary and HTML report.
    """
    # Load JSON configuration
    logging.info('Loading configuration file: %s', args.config)
    with open(args.config, 'r') as file:
        config = json.load(file)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    results = []
    
    store = str()
    
    # Iterate over each custom item
    for item_key, item in config.items():
        logging.info('Processing item: %s', item_key)
        description = item.get('description')
        cmd = item.get('cmd')
        expect = item.get('expect')
        info = item.get('info', 'N/A')
        solution = item.get('solution', 'N/A')
        see_also = item.get('see_also', '')
        if len(info) >= 5: 
            store = description  
        if info == "N/A": 
            temp = str()
            temp = description
            description = store
            info = temp
                        
        try:
            if "@" in expect or expect == "Manual Review Require" or expect == "^Manual Review Required$": 
                logging.error('needs manual check')
                cmd = clean_command(cmd)
                results.append({
                    'description': description,
                    'info': info,
                    'command': cmd,
                    'status': 'manual',
                    'output': 'N/A',
                    'solution': solution,
                    'see_also': see_also
                })
                continue
        except: 
            pass 

        if cmd is None:
            logging.warning('No command found for item: %s. Skipping.', item_key)
            continue

        logging.info('Description: %s', description)
        logging.info('Expected pattern: %s', expect)

        total_tests += 1

        # Execute the command
        if ssh_flag: 
            result, cmd = execute_command_over_ssh(cmd, description, ssh, password)
        else: 
            result, cmd = execute_command(cmd, description)
            result = str(result)
    
        logging.info('Command output: %s', result)
        cap = str(result.capitalize())
        exp = str(expect.capitalize())
        # Check the output against the expected pattern
        if check_output(result, expect) or check_output(cap, exp):     
            logging.info('Check passed.')
            passed_tests += 1
            results.append({
                'description': description,
                'info': info,
                'command': cmd, 
                'status': 'passed',
                'output': result,
                'solution': solution,
                'see_also': see_also
            })
        else:
            logging.error('Check failed.')
            failed_tests += 1
            results.append({
                'description': description,
                'info': info,
                'command': cmd,
                'status': 'failed',
                'output': result,
                'solution': solution,
                'see_also': see_also
            })

    # Output summary
    logging.info('Test Summary: %d tests run, %d passed, %d failed.', total_tests, passed_tests, failed_tests)
    print('Test Summary:')
    print(f'Total tests run: {total_tests}')
    print(f'Passed: {passed_tests}')
    print(f'Failed: {failed_tests}')

    # if failed_tests > 0:
    #     print('\nFailed Test Details:')
    #     for detail in results:
    #         if detail['status'] == 'failed':
    #             print(f"Description: {detail['description']}")
    #             print(f"Error: {detail['output']}")
    #             print(f"Solution: {detail['solution']}")
    #             print('')

    # Generate HTML report
    generate_html_report(results, "logo.png")

if __name__ == '__main__':
    main()