import os
import paramiko
import time


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

# Input the group name,old/target firmware version
group_name = input('Enter the group_name : \n')
os.makedirs('{}/verify_files'.format(group_name))

# Open the file with the list of IPs
vc_list = open("{}/vc_list.txt".format(group_name), "r")

# Maintain logs
logs = open("{}/verify_logs.txt".format(group_name), "a")

print('='*66+"\n")

suc = 0
mismatch = 0
fail = 0
unreach = 0

for ip_address in vc_list.readlines():
    IP = ip_address.strip()
    # Check if host is reachable and proceed
    response = os.system('ping {} -n 2\n'.format(ip_address))
    if response == 0:
        try:
            running_config(IP, 'admin', 'sgwifi')# Use SG user,pass
            with open("temp.txt", 'r') as temp:
                new = set(str(temp.read()).split('\n'))
                old_config = open("{0}/backup_files/{1}_backup_config.txt".format(group_name, IP), 'r')
                old = set(str(old_config.read()).split('\n'))
                # Compare both the configs
                if new == old :  #  If both are same
                    print('{0} {1} Verified![No mismatches]\n!'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                    logs.write('{0} {1} Verified![No mismatches]\n'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                    suc += 1
                elif new ^ old != {}:  # If there is a mismatch
                    with open("{0}/verify_files/{1}_mismatch_logs.txt".format(group_name,IP), "w") as mismatch_logs: 
                        mismatch_logs.write('Mismatch in files : ( Missing lines - ; New lines + )\n')
                        mismatch_logs.write('+  {} \n'.format(new - old))
                        mismatch_logs.write('-  {} \n'.format(old - new))
                    print('{0} {1} Mismatch in config!\n!'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                    logs.write('{0} {1} Mismatch in config!\n'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                    mismatch += 1       
                old_config.close()
            os.system('del temp.txt')
        except paramiko.ssh_exception.AuthenticationException:
            try:
                running_config(IP, 'admin', 'admin')  # Use default user,pass
                with open('temp.txt', 'r') as temp:
                    new = set(str(temp.read()).split('\n'))
                    old_config = open("{0}/backup_files/{1}_backup_config.txt".format(group_name, IP), 'r')
                    old = set(str(old_config.read()).split('\n'))
                    # Compare both the configs
                    if new == old :  #  If both are same
                        print('{0} {1} Verified![No mismatches]\n!'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                        logs.write('{0} {1} Verified![No mismatches]\n'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                        suc += 1
                    elif new ^ old != {}:  # If there is a mismatch
                        with open("{0}/verify_files/{1}_mismatch_logs.txt".format(group_name,IP), "w") as mismatch_logs: 
                            mismatch_logs.write('Mismatch in files : ( Missing lines - ; New lines + )\n')
                            mismatch_logs.write('+  {} \n'.format(new - old))
                            mismatch_logs.write('-  {} \n'.format(old - new))
                        print('{0} {1} Mismatch in config!\n!'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                        logs.write('{0} {1} Mismatch in config!\n'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                        mismatch += 1
                    old_config.close()
                os.system('del temp.txt')
            except :
                    # Throw error if any and continue
                    print('{0} {1} Unable to login! [Host reachable]\n!'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                    logs.write('{0} {1} Unable to login! [Host reachable]\n'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
                    fail += 1
                
    else:
        # If host unreachable
        print('{0} {1} Verfication failed![Host unreachable]\n!'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
        logs.write('{0} {1} Verfication failed![Host unreachable]\n'.format(IP, time.strftime('%d/%m/%Y %I:%M:%S %p')))
        unreach += 1

# Print and log results and close vc_list:
print(' \n'*5)
print('Finished!\n')
print('Total={0} Successful={1} Mismatches={2} Unreachables/Login fail={3}\n'.format(suc+fail+mismatch+unreach, suc, mismatch, fail+unreach))
logs.write(' \n'*5)
logs.write('Total={0} Successful={1} Mismatches={2} Unreachable/Login fail={3}\n'.format(suc+fail+mismatch+unreach, suc, mismatch, fail+unreach))
logs.close()
vc_list.close()
