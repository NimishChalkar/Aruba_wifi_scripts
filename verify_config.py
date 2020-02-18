# v2.2

import time
import paramiko
import os


def take_config(ip, user, pw):
    """Take config of the AP with host IP, username and password as the input and store in a variable"""
    # Open a socket,copy the output
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=pw)
    chan = client.invoke_shell()
    time.sleep(2)
    chan.send('sh running-config no-encrypt\n')
    time.sleep(2)
    output = chan.recv(99999999)
    output.decode("utf-8")
    return output


group_name = input('Enter the group_name :')
# Open the file with the list of IPs
vc_list = open("{}/vc_list.txt".format(group_name), "r")
# Maintain logs
logs = open("{}/verify_logs.txt".format(group_name), "a")

print(('=' * 66) + "\n")

suc = 0
fail = 0
mismatch = 0

for ip_address in vc_list.readlines():
    IP = ip_address.strip()
    # Check if host is reachable and proceed
    response = os.system('ping {} -n 2\n'.format(ip_address))
    if response == 0:
        try:
            diff = ""
            running_config = str(take_config(IP, 'admin', 'sgwifi'))  # Use SG user,pass
            with open("{}_backup_config.txt".format(IP), "r") as backup_config:
                if len(running_config) == len(str(backup_config.read())):
                    for b in running_config:
                        if b not in str(backup_config.read()):
                            diff = diff + b
                            print('{0} Upgraded successfully to {1}! {2}'.format(IP, diff, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                            logs.write('{0} Upgraded successfully to {1}! {2}'.format(IP, diff, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                            suc += 1
                elif len(running_config) != len(str(backup_config.read())):
                    print('{0} Mismatched! {1}'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                    logs.write('{0} Mismatched! {1}'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                    mismatch += 1
        except paramiko.ssh_exception.AuthenticationException:
            diff = ""
            running_config = str(take_config(IP, 'admin', 'sgwifi'))  # Use SG user,pass
            with open("{}_backup_config.txt".format(IP), "r") as backup_config:
                if len(running_config) == len(str(backup_config.read())):
                    for b in running_config:
                        if b not in str(backup_config.read()):
                            diff = diff + b
                            print('{0} Upgraded successfully to {1}! {2}'.format(IP, diff, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                            logs.write('{0} Upgraded successfully to {1}! {2}'.format(IP, diff, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                            suc += 1
                elif len(running_config) != len(str(backup_config.read())):
                    print('{0} Mismatched! {1}'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                    logs.write('{0} Mismatched! {1}'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                    mismatch += 1
        except:
            # Throw error if any
            print('{0} {1} Verification failed! [Host reachable]\n'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
            logs.write('{0} {1} Verification failed! [Host reachable]\n'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
            fail += 1
    else:
        # If host unreachable
        print('{0} {1} Verification failed! [Host unreachable]\n'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
        logs.write('{0} {1} Verification failed! [Host unreachable]\n'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
        fail += 1

# Print and log results:
print(' \n'*5)
print('Finished!\n')
print('Total={0} Successful={1} Verification Failed={2} Configuration mismatches={3}\n'.format(suc+fail+mismatch, suc, fail, mismatch))
logs.write(' \n'*5)
logs.write('Total={0} Successful={1} Verification Failed={2} Configuration mismatches={3}\n'.format(suc+fail+mismatch, suc, fail, mismatch))

# Close files
logs.close()
vc_list.close()