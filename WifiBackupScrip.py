# v2.2(11th Feb)

import time
import paramiko
import datetime
import os
import sys

now = datetime.datetime.now()

def backup_config(ip, user, pw):
    """Take back up of the AP with host IP, username and password as the input and write it to a file"""

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
    backup_file = open("{0}{1}.txt".format(ip, now.strftime('%d/%m/%Y %I:%M:%S %p')), "w")
    backup_file.write(output.decode("utf-8"))
    backup_file.close()
    client.close()

# Input a group name,create a folder and store logs,backup files
group_name = input('Enter the group_name :')
os.system('md {}'.format(group_name))
os.system('{}\logs.txt'.format(group_name))

# Open the file with the list of IPs
vc_list = open("vc_list.txt", "r")
# Maintain logs
logs = open("{}\logs.txt".format(group_name), "a")

print(('='*66)+("\n"))

suc = 0
fail = 0

for ip_address in vc_list.readlines():
    IP = ip_address.strip()
    
    try:
        # Use SG user,pass
        backup_config(IP, 'admin', 'sgwifi')
        print('{0}   {1} backup successful!'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
        logs.write('{0}   {1} backup successful!\n'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
        suc += 1
    except paramiko.ssh_exception.AuthenticationException:
        # Use factory user,pass
        backup_config(IP, 'admin', 'admin')
        print('{0}   {1} backup successful!'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
        logs.write('{0}   {1} backup successful!\n'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
        suc += 1
    except:
        # Throw error if any
        print('{0}   {1} backup failed! [WARNING]'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
        logs.write('{0}   {1} backup failed!\n'.format(IP, now.strftime('%d/%m/%Y %I:%M:%S %p')))
        fail += 1

# Print and log results:
print(' \n'*5)
print('Finished!\n')
print('Total={0} Successful={1} Fail={2}\n'.format(suc+fail,suc,fail))
logs.write(' /n'*5)
logs.write('Total={0} Successful={1} Fail={2}\n'.format(suc+fail,suc,fail))

logs.close()
vc_list.close()
