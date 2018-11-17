import paramiko
import json


def format_data(std_out, std_err):
    r_std_out = [line.strip() for line in std_out]
    r_std_err = [line.strip() for line in std_err]
    return r_std_out, r_std_err


def control_ssh(command):
    with open('config.json', 'r') as f:
        obj = json.load(f)

    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("connecting...\r\n")
        ssh.connect(hostname=obj["ssh"]["ip"],
                    port=obj["ssh"]["port"],
                    username=obj["ssh"]["username"],
                    password=obj["ssh"]["password"])
        print("connected!\r\n")

        print("command : {0}\r\n".format(command))

        stdin, stdout, stderr = ssh.exec_command(command)
        result_stdout, result_stderr = format_data(stdout, stderr)

        for out in result_stdout:
            print(out)

        for err in result_stderr:
            print(err)
