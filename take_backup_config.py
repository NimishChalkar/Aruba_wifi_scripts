# v2.2

import os
import paramiko
import time


def backup_config(ip, user, pw, group):
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
    backup_file = open("{0}/backup_files/{1}_backup_config.txt".format(group, ip), "w")
    try:
        backup_file.write(output.decode("latin1"))
    except UnicodeEncodeError:
        run_config.write(output.decode("utf-8"))
    backup_file.close()
    client.close()


def backup_successful(ip):
    print('{0} {1} Backup successful\n!'.format(ip, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Backup successful\n'.format(ip, time.strftime('%d/%m/%Y %I:%M:%S %p')))


def unable_to_login(ip):
    print('{0} {1} Unable to login![Host reachable]\n!'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Unable to login![Host reachable]\n'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))


def backup_failed(ip):
    print('{0} {1} Backup failed![Host reachable]\n!'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Backup failed![Host reachable]\n'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))


def host_unreachable(ip):
    print('{0} {1} Host unreachable!\n!'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Host unreachable!\n'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))

        
# Input a group name,create a folder and store logs,backup files
group_name = input('Enter the group_name :\n')
os.makedirs('{}/backup_files'.format(group_name))

# Open the file with the list of IPs
vc_list = open("vc_list.txt", "r")

# Maintain logs
logs = open("{}/backup_logs.txt".format(group_name), "a")

print('='*66+"\n")

suc = 0
fail = 0

for ip_address in vc_list.readlines():
    IP = ip_address.strip()
    # Check if host is reachable and proceed
    response = os.system('ping {} -n 2\n'.format(ip_address))
    if response == 0:
        try:
            backup_config(IP, 'admin', 'sgwifi', group_name)  # Use SG user,pass
            backup_successful(IP)
            suc += 1
        except paramiko.ssh_exception.AuthenticationException:
            try:
                backup_config(IP, 'admin', 'admin', group_name)  # Use default user,pass
                backup_successful(IP)
                suc += 1
            except :
                # Throw error and continue
                unable_to_login(IP)
                fail += 1
        except:
            # Throw error if any and continue
            backup_failed(IP)
            fail += 1
    else:
        # If host unreachable
        host_unreachable(IP)
        fail += 1

# Print and log results and close vc_list:
print(' \n'*5)
print('Finished!\n')
print('Total={0} Successful={1} Unreachable/Login fail={2}\n'.format(suc+fail, suc, fail))
logs.write(' \n'*5)
logs.write('Total={0} Successful={1} Unreachable/Login fail={2}\n'.format(suc+fail, suc, fail))
logs.close()
vc_list.close()

# Move vc_list.txt to the group folder
os.system('move vc_list.txt {}'.format(group_name))
