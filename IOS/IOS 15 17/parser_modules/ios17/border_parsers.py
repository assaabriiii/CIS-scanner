import re
from ssh import ssh_send
from report_temp.main_report import generate_report


def compliance_check_border_router_filtering(connection, command_one, command_two, cis_check_one, cis_check_two, level, global_report_output):
    
    def compliance_check_acl_private_external(connection, command_one, command_two, cis_check_one, cis_check_two, level, global_report_output):
        command_output = ssh_send(connection, command_one)
        
        private_acl_search = re.search(r'''
            Extended\s+IP\s+access\s+list\s+(?P<acl>\S+).*?
            (\s+\d+\s+deny\s+ip\s+127\.0\.0\.0\s+0\.255\.255\.255\s+any\s+log\n
            \s+\d+\s+deny\s+ip\s+10\.0\.0\.0\s+0\.255\.255\.255\s+any\s+log\n
            \s+\d+\s+deny\s+ip\s+0\.0\.0\.0\s+0\.255\.255\.255\s+any\s+log\n
            \s+\d+\s+deny\s+ip\s+172\.16\.0\.0\s+0\.15\.255\.255\s+any\s+log\n
            \s+\d+\s+deny\s+ip\s+192\.168\.0\.0\s+0\.0\.255\.255\s+any\s+log\n
            \s+\d+\s+deny\s+ip\s+192\.0\.2\.0\s+0\.0\.0\.255\s+any\s+log\n
            \s+\d+\s+deny\s+ip\s+169\.254\.0\.0\s+0\.0\.255\.255\s+any\s+log\n
            \s+\d+\s+deny\s+ip\s+224\.0\.0\.0\s+31\.255\.255\.255\s+any\s+log\n
            \s+\d+\s+deny\s+ip\s+host\s+255\.255\.255\.255\s+any\s+log\n)
            ''', command_output, re.MULTILINE | re.DOTALL | re.IGNORECASE | re.VERBOSE)
        
        if not private_acl_search:
            compliant = False
            current_configuration = None
            global_report_output.append(generate_report(cis_check_one, level, compliant, current_configuration))
            global_report_output.append(generate_report(cis_check_two, level, compliant, current_configuration))
            
            return
        
        else:
