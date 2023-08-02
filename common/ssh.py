import paramiko


class SSHPool(object):

    def __init__(self):
        self.pool = {}

    def connect(self, ip, port, username, password):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username, password)
        return ssh

    def get(self, ip, port, username, password):
        for ssh_ip, ssh_client in self.pool.items():
            if ssh_ip == ip:
                if ssh_client.get_transport() and ssh_client.get_transport(
                ).is_alive():
                    return ssh_client
                else:
                    break
            else:
                continue
        ssh = self.connect(ip, port, username, password)
        self.pool[ip] = ssh
        return ssh


ssh_pool = SSHPool()
