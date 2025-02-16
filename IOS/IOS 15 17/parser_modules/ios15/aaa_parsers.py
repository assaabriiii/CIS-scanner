import re
from ssh import ssh_send
from report_temp.main_report import generate_report


def compliance_check_aaa_auth_line_con(connection, command, cis_check, level, global_report_output):
    command_output = ssh_send(connection, command)
    regex_pattern = re.compile(r'line con (?P<channel>\d+(?: \d+)*)(\n(?P<config>(?: [^\n]*\n?)*))(?=\nline con|$)', re.DOTALL)
    parser = regex_pattern.finditer(command_output)

    line_con_list = []
    non_compliant_con_counter = 0

    for match in parser:
        line_channel = match.group('channel')
        line_config = match.group('config') if match.group('config') else None

        if line_config == None:
            non_compliant_con_counter += 1
            login_auth = None
        
        else:
            login_auth_search = re.search(r'login\s+authentication\s+(?P<auth_list>\S+)', line_config)
            if not login_auth_search:
                non_compliant_con_counter += 1
                login_auth = None
            else:
                login_auth = login_auth_search.group('auth_list')

        current_line_con_info = {'Channel':line_channel, 'Auth':login_auth}
        line_con_list.append(current_line_con_info)
    
    compliant = bool(line_con_list) and non_compliant_con_counter == 0
    current_configuration = line_con_list if line_con_list else None
    global_report_output.append(generate_report(cis_check, level, compliant, current_configuration))


def compliance_check_aaa_auth_line_tty(connection, command_one, command_two, cis_check, level, global_report_output):
    tty_line_check_output = ssh_send(connection, command_one)
    
    if "TTY" not in tty_line_check_output:
        compliant = "Not Applicable"
        current_configuration = "No TTY Lines"

    else:
        command_output = ssh_send(connection, command_two)
        regex_pattern = re.compile(r'line tty (?P<channel>\d+(?: \d+)*)(\n(?P<config>(?: [^\n]*\n?)*))(?=\nline tty|$)', re.DOTALL)
        parser = regex_pattern.finditer(command_output)

        line_tty_list = []
        non_compliant_tty_counter = 0

        for match in parser:
            line_channel = match.group('channel')
            line_config = match.group('config') if match.group('config') else None

            if line_config == None:
                non_compliant_tty_counter += 1
                login_auth = None
            
            else:
                login_auth_search = re.search(r'login\s+authentication\s+(?P<auth_list>\S+)', line_config)
                if not login_auth_search:
                    non_compliant_tty_counter += 1
                    login_auth = None
                else:
                    login_auth = login_auth_search.group('auth_list')

            current_line_tty_info = {'Channel':line_channel, 'Auth':login_auth}
            line_tty_list.append(current_line_tty_info)

        compliant = bool(line_tty_list) and non_compliant_tty_counter == 0
        current_configuration = line_tty_list if line_tty_list else None

    global_report_output.append(generate_report(cis_check, level, compliant, current_configuration))


def compliance_check_aaa_auth_line_vty(connection, command, cis_check, level, global_report_output):
    command_output = ssh_send(connection, command)
    regex_pattern = re.compile(r'line vty (?P<channel>\d+(?: \d+)*)(\n(?P<config>(?: [^\n]*\n?)*))(?=\nline vty|$)', re.DOTALL)
    parser = regex_pattern.finditer(command_output)

    line_vty_list = []
    non_compliant_vty_counter = 0

    for match in parser:
        line_channel = match.group('channel')
        line_config = match.group('config') if match.group('config') else None

        if line_config == None:
            non_compliant_vty_counter += 1
            login_auth = None
        
        else:
            login_auth_search = re.search(r'login\s+authentication\s+(?P<auth_list>\S+)', line_config)
            if not login_auth_search:
                non_compliant_vty_counter += 1
                login_auth = None
            else:
                login_auth = login_auth_search.group('auth_list')
        
        current_line_vty_info = {'Channel':line_channel, 'Auth':login_auth}
        line_vty_list.append(current_line_vty_info)
    
    compliant = bool(line_vty_list) and non_compliant_vty_counter == 0
    current_configuration = line_vty_list if line_vty_list else None
    global_report_output.append(generate_report(cis_check, level, compliant, current_configuration))
        

def compliance_check_aaa_source_int(connection, command_one, command_two, cis_check, level, global_report_output):
    command_output_one = ssh_send(connection, command_one)
    command_output_two = ssh_send(connection, command_two)
    if not command_output_one and not command_output_two:
        compliant = False
        current_configuration = None
        global_report_output.append(generate_report(cis_check, level, compliant, current_configuration))
    else:
        compliant = True
        current_configuration = f"TACACS+:{command_output_one if command_output_one else None}, RADIUS:{command_output_two if command_output_two else None}"
        global_report_output.append(generate_report(cis_check, level, compliant, current_configuration))