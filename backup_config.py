#!/usr/bin/env/python

import os
import paramiko
import time
from openpyxl import load_workbook

def backup_config(ip: str, name: str, user: str, pw: str, group: str):
    """Take back up of the VC with host IP, username and password as the input and write it to a file"""

    # Open a socket,copy the output
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=pw)
    chan = client.invoke_shell()
    time.sleep(5)
    chan.send('sh running-config no-encrypt\n')
    time.sleep(5)
    output = chan.recv(99999999)
    # Create a file,write the config and close it
    backup_file = open("{0}/backup_files/{1}.txt".format(group, name), "w")
    try:
        backup_file.write(output.decode("latin1"))
    except UnicodeEncodeError:
        backup_file.write(output.decode("utf-8"))
    backup_file.close()
    client.close()


def backup_successful(name: str):
    print('{0} {1} Backup successful\n!'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Backup successful\n'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))

def unable_to_login(name: str):
    print('{0} {1} Unable to login![Host reachable]\n!'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Unable to login![Host reachable]\n'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))

def timeout_error(name: str):
    print('{0} {1} Backup failed!TimeoutError[Host reachable]\n!'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Backup failed!TimeoutError[Host reachable]\n'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))

def backup_failed(name: str):
    print('{0} {1} Backup failed![Host reachable]\n!'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Backup failed![Host reachable]\n'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))

def unreachable(name: str):
    print('{0} {1} Host unreachable!\n!'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Host unreachable!\n'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))
          
# Input a group name,create a folder and store logs,backup files
group_name = input('Enter the group_name :\n')
n = int(input('no. of VCs :\n'))
os.makedirs('{}/backup_files'.format(group_name))
logs = open("{}/backup_logs.txt".format(group_name), "a")

print('='*66+"\n")

suc = 0
fail = 0
failed_list = {}

vc_list = load_workbook(filename = '{}.xlsx'.format(group_name))
vc = vc_list[group_name]
for i in range(1,n+1):
    ip_address = vc['B{}'.format(i)].value
    vc_name = vc['A{}'.format(i)].value
    # Check if host is reachable and proceed
    response = os.system('ping {} -n 2\n'.format(ip_address))
    if response == 0:
        try:
            backup_config(ip_address, vc_name, 'username', 'password', group_name)  # Use SG user,pass
            backup_successful(vc_name)
            suc += 1
        except paramiko.ssh_exception.AuthenticationException:
            backup_config(ip_address, vc_name, 'altusername', 'altpassword', group_name)  # Use default user,pass
            backup_successful(vc_name)
            suc += 1
        except TimeoutError:
            # Response timed out
            timeout_error(vc_name)
            fail += 1
            failed_list.update({vc_name:ip_address})
        except:
            # Throw error if any and continue
            backup_failed(vc_name)
            fail += 1
            failed_list.update({vc_name:ip_address})
    else:
        # If host unreachable
        unreachable(vc_name)
        fail += 1
        failed_list.update({vc_name:ip_address})
        
# Print and log results and close vc_list:
print(' \n'*4)
print('Finished!\n')
print('Total={0} Successful={1} Unreachables/Login fail={2}\n'.format(suc+fail, suc, fail))
print('Unreachables/Login fail :\n')
for vc,ip in failed_list.items():
    print(vc,ip)

print('='*66+"\n")

logs.write(' \n'*4)
logs.write('Total={0} Successful={1} Unreachable/Login fail={2}\n'.format(suc+fail, suc, fail))
logs.write('Unreachables/Login fail :\n')
for vc,ip in failed_list.items():
    logs.write('{0} {1}'.format(vc, ip))
logs.write('\n'*2)
logs.close()

# Move vc list to the group folder
os.system('move {0}.xlsx {1}'.format(group_name, group_name))
