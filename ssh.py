import paramiko


def format_data(std_out, std_err):
    r_std_out = [line.strip() for line in std_out]
    r_std_err = [line.strip() for line in std_err]
    return r_std_out, r_std_err


if __name__ == '__main__':
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("connecting...")
        ssh.connect(hostname='192.168.0.27', port=22, username='pi', password='ricca170814')
        print("connected!\r\n")

        command = "source Downloads/mjpg-streamer/mjpg_streamer_end.sh"
        print("command : {0}\r\n".format(command))

        stdin, stdout, stderr = ssh.exec_command(command)
        result_stdout, result_stderr = format_data(stdout, stderr)
        for line in result_stdout:
            print(line)

        for line in result_stderr:
            print(line)
