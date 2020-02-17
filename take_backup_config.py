# v2.2

import datetime
import os
import paramiko
import time

now = datetime.datetime.now()


def backup_config(ip, user, pw, group_name):
    """Take back up of the VC with host IP, username and password as the input and write it to a file"""

    # Open a socket,copy the output
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=pw)
    chan = client.invoke_shell()
    time.sleep(2)
    chan.send('sh running-config no-encrypt\n')
    time.sleep(2)
    output = chan.recv(99999999)
    # Create a file,write the config and close it
    backup_file = open("{}_backup_config.txt".format(ip), "w")
    backup_file.write(output.decode("utf-8"))
    backup_file.close()
    os.system('move {0}_backup_config.txt {1}'.format(ip, group_name))
    client.close()


# Input a group name,create a folder and store logs,backup files
group_name = input('Enter the group_name :')
os.system('md {}'.format(group_name))

# Open the file with the list of IPs
vc_list = open("vc_list.txt", "r")

# Maintain logs
logs = open('{}/backup_logs.txt'.format(group_name), "a")

print('='*66+"\n")

suc = 0
fail = 0

for ip_address in vc_list.readlines():
    IP = ip_address.strip()
    # Check if host is reachable and proceed
    response = os.system('ping {} -n 1'.format(ip_address))
    if response == 0:
        try:
            # Use SG user,pass
            backup_config(IP, 'admin', 'sgwifi', group_name)
            print('{0} {1} Backup successful!'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
            logs.write('{0} {1} Backup successful!\n'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
            suc += 1
        except paramiko.ssh_exception.AuthenticationException:
            # Use factory-set user,pass
            backup_config(IP, 'admin', 'admin', group_name)
            print('{0} {1} Backup successful!'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
            logs.write('{0} {1} Backup successful!\n'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
            suc += 1
        except:
            # Throw error if any
            print('{0} {1} Backup failed! [Host reachable]\n'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
            logs.write('{0} {1} Backup failed! [Host reachable]\n'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
            fail += 1
    else:
        # If host unreachable
        print('{0} {1} Backup failed![Host unreachable]\n'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
        logs.write('{0} {1} Backup failed![Host unreachable]\n'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
        fail += 1

# Print and log results:
print(' \n'*5)
print('Finished!\n')
print('Total={0} Successful={1} Fail={2}\n'.format(suc+fail, suc, fail))
logs.write(' \n'*5)
logs.write('Total={0} Successful={1} Fail={2}\n'.format(suc+fail, suc, fail))

# Close files
logs.close()
vc_list.close()

# Move vc_list.txt to the group folder
os.system('move vc_list.txt {}'.format(group_name))
