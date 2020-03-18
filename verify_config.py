# v3

import os
import paramiko
import time
from openpyxl import load_workbook

def running_config(ip, user, pw):
    # Open a socket,copy the output to a temporary file
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=pw)
    chan = client.invoke_shell()
    time.sleep(5)
    chan.send('sh running-config no-encrypt\n')
    time.sleep(5)
    output = chan.recv(99999999)
    run_config = open('temp.txt', 'w')
    try:
        run_config.write(output.decode("utf-8"))
    except UnicodeEncodeError:
        run_config.write(output.decode("latin1"))
    client.close()
    run_config.close()

def no_mismatches(name):
    print('{0} {1} Verified![No mismatches]\n!'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Verified![No mismatches]\n'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))

def mismatch(name):
    print('{0} {1} Mismatch in config!\n!'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Mismatch in config!\n'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))

def timeout_error(name):
    print('{0} {1} Unable to login!TimeoutError[Host reachable]\n!'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Unable to login!TimeoutError[Host reachable]\n'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))

def unknown_error(name):
    print('{0} {1} Unable to login!Unknown Error[Host reachable]\n!'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Unable to login!Unknown Error[Host reachable]\n'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))

def unreachable(name):
    print('{0} {1} Verfication failed![Host unreachable]\n!'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))
    logs.write('{0} {1} Verfication failed![Host unreachable]\n'.format(name, time.strftime('%d/%m/%Y %I:%M:%S %p')))

# Input the group name,old/target firmware version
group_name = input('Enter the group_name : \n')
os.makedirs('{}/verify_files'.format(group_name))

n = int(input('no. of VCs :\n'))

# Maintain logs
logs = open("{}/verify_logs.txt".format(group_name), "a")

print('='*66+"\n")

suc = 0
mismatch = 0
fail = 0
failed_list = {}
mismatched_list = {}

vc_list = load_workbook(filename = '{0}/{1}.xlsx'.format(group_name, group_name))
vc = vc_list[group_name]
for i in range(1,n+1):
    ip_address = vc['B{}'.format(i)].value
    vc_name = vc['A{}'.format(i)].value
    # Check if host is reachable and proceed
    response = os.system('ping {} -n 2'.format(ip_address))
    if response == 0:
        try:
            running_config(ip_address, 'admin', 'sgwifi')# Use SG user,pass
            with open("temp.txt", 'r') as temp:
                new = set(str(temp.read()).split('\n'))
                old_config = open("{0}/backup_files/{1}.txt".format(group_name, vc_name), 'r')
                old = set(str(old_config.read()).split('\n'))
                # Compare both the configs
                if new == old :  #  If both are same
                    no_mismatches(vc_name)
                    suc += 1
                elif new ^ old != {}:  # If there is a mismatch
                    with open("{0}/verify_files/{1}_mismatch_logs.txt".format(group_name, vc_name), "w") as mismatch_logs: 
                        mismatch_logs.write('Mismatch in files : ( Missing lines - ; New lines + )\n')
                        mismatch_logs.write('+  {} \n'.format(new - old))
                        mismatch_logs.write('-  {} \n'.format(old - new))
                    mismatch(vc_name)    
                    mismatch += 1
                    mismatched_list.update({vc_name:ip_address})
                old_config.close()
            os.system('del temp.txt')
        except TimeoutError:
                    # Response timed out
                    timeout_error(vc_name)
                    fail += 1
                    failed_list.update({vc_name:ip_address})
        except paramiko.ssh_exception.AuthenticationException:
                running_config(ip_address, 'admin', 'admin')  # Use default user,pass
                with open('temp.txt', 'r') as temp:
                    new = set(str(temp.read()).split('\n'))
                    old_config = open("{0}/backup_files/{1}.txt".format(group_name, vc_name), 'r')
                    old = set(str(old_config.read()).split('\n'))
                    # Compare both the configs
                    if new == old :  #  If both are same
                        no_mismatches(vc_name)
                        suc += 1
                    elif new ^ old != {}:  # If there is a mismatch
                        with open("{0}/verify_files/{1}_mismatch_logs.txt".format(group_name,IP), "w") as mismatch_logs: 
                            mismatch_logs.write('Mismatch in files : ( Missing lines - ; New lines + )\n')
                            mismatch_logs.write('+  {} \n'.format(new - old))
                            mismatch_logs.write('-  {} \n'.format(old - new))
                        mismatch(vc_name)
                        mismatch += 1
                        mismatched_list.update({vc_name:ip_address})
                    old_config.close()
                os.system('del temp.txt')
        except :
                # Throw error if any and continue
                unknown_error(vc_name)
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
print('Total={0} Successful={1} Mismatches={2} Unreachables/Login fail={3}\n'.format(suc+fail+mismatch, suc, mismatch, fail))
print('Unreachables/Login fail :\n')
for vc,ip in failed_list.items():
    print(vc,ip)
print('\n'*2)
print('Mismatched :\n')
for vc,ip in mismatched_list.items():
    print(vc,ip)
print('='*66+"\n")

logs.write(' \n'*4)
logs.write('Total={0} Successful={1} Mismatches={2} Unreachable/Login fail={3}\n'.format(suc+fail+mismatch, suc, mismatch, fail))
logs.write('Unreachables/Login fail :\n')
for vc,ip in failed_list.items():
    logs.write('{0} {1}'.format(vc, ip))
logs.write('\n'*2)
logs.write('Mismatched :\n')
for vc,ip in mismatched_list.items():
    logs.write('{0} {1}'.format(vc, ip))
logs.write('='*66+"\n")    
logs.close()
