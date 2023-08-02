import logging
import paramiko
from common import aliyun_sdk
from common import common_config
from common.ssh import ssh_pool
import re
import os


class LinuxCmd(object):

    def __init__(self, vm_name=""):
        self.vm_ip = None
        self.username = common_config.ssh_username_default
        self.password = common_config.ssh_password_default
        self.ssh_port = common_config.ssh_port_default
        pass

    def setter(self, **kwargs):
        for key, value in kwargs.items():
            if key == "vm_ip":
                self.vm_ip = value

    def getter(self):
        pass

    def create_performance_pods(
        self, vtaps_mgt_ip, username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default
    ):
        '''Login to the vtaps by SSH,create pod for TCP performance
        '''
        logging.info(
            "create_performance_pods::vtaps_mgt_ip ==> {}"
            .format(vtaps_mgt_ip)
        )
        logging.info(
            "create_performance_pods::ssh_port ==> {}".format(ssh_port)
        )
        logging.info(
            "create_performance_pods::username ==> {}".format(username)
        )
        logging.info(
            "create_performance_pods::password ==> {}".format(password)
        )
        ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
        strin, stdout, stderr = ssh.exec_command(
            '''cat /dev/null > /etc/resolv.conf &&\
                                                  echo 'nameserver %s' >> /etc/resolv.conf && \
                                                  curl -O http://nexus.yunshan.net/repository/tools/automation/performance/performance_client.yaml && \
                                                  curl -O http://nexus.yunshan.net/repository/tools/automation/performance/performance_server.yaml && \
                                                  nerdctl -n k8s.io load -i performance_v1.tar && \
                                                  nerdctl -n k8s.io tag $(nerdctl -n k8s.io image list|grep overlayfs|awk -F ' ' '{print $3}') performance:lastest && \
                                                  kubectl apply -f performance_client.yaml && kubectl apply -f performance_server.yaml &&\
                                                  sleep 60''' %
            (common_config.ali_dns_ip)
        )
        logs = stdout.readlines()
        pod_client_name = ''
        pod_client_ip = ''
        pod_server_name = ''
        pod_server_ip = ''
        stdin, stdout, stderr = ssh.exec_command(
            'kubectl get pods -o wide|grep client'
        )
        client_logs = stdout.readlines()
        for i in client_logs:
            pod_client_name = i.split(' ')[0]
            pod_client_ip = i.split(' ')[24]
        stdin, stdout, stderr = ssh.exec_command(
            'kubectl get pods -o wide|grep server'
        )
        server_logs = stdout.readlines()
        for i in server_logs:
            pod_server_name = i.split(' ')[0]
            pod_server_ip = i.split(' ')[24]

        if pod_client_name == "" or pod_client_ip == "" or pod_server_name == "" or pod_server_ip == "":
            logging.error("create performance pods failed!")
            assert False

        logging.info(
            "create_performance_pods::pod_client_name ==> {}"
            .format(pod_client_name)
        )
        logging.info(
            "create_performance_pods::pod_client_ip ==> {}"
            .format(pod_client_ip)
        )
        logging.info(
            "create_performance_pods::pod_server_name ==> {}"
            .format(pod_server_name)
        )
        logging.info(
            "create_performance_pods::pod_server_ip ==> {}"
            .format(pod_server_ip)
        )
        return pod_client_name, pod_client_ip, pod_server_name, pod_server_ip

    def create_performance_pods_arm(
        self, vtaps_mgt_ip, username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default
    ):
        '''Login to the arm vtaps by SSH,create pod for TCP performance
        '''
        logging.info(
            "create_performance_pods::vtaps_mgt_ip ==> {}"
            .format(vtaps_mgt_ip)
        )
        logging.info(
            "create_performance_pods::ssh_port ==> {}".format(ssh_port)
        )
        logging.info(
            "create_performance_pods::username ==> {}".format(username)
        )
        logging.info(
            "create_performance_pods::password ==> {}".format(password)
        )
        ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
        strin, stdout, stderr = ssh.exec_command(
            '''cat /dev/null > /etc/resolv.conf &&\
                                                  echo 'nameserver %s' > /etc/resolv.conf && \
                                                  curl -O http://nexus.yunshan.net/repository/tools/automation/performance/performance_client.yaml && \
                                                  curl -O http://nexus.yunshan.net/repository/tools/automation/performance/performance_server.yaml && \
                                                  systemctl restart containerd && \
                                                  nerdctl -n k8s.io load -i performance_arm.tar && \
                                                  nerdctl -n k8s.io tag $(nerdctl -n k8s.io image list|grep performance_arm | awk -F ' ' '{print $3}') performance:lastest && \
                                                  kubectl apply -f performance_client.yaml && kubectl apply -f performance_server.yaml &&\
                                                  sleep 60''' %
            (common_config.ali_dns_ip)
        )
        logs = stdout.readlines()
        pod_client_name = ''
        pod_client_ip = ''
        pod_server_name = ''
        pod_server_ip = ''
        stdin, stdout, stderr = ssh.exec_command(
            'kubectl get pods -o wide|grep client'
        )
        client_logs = stdout.readlines()
        for i in client_logs:
            pod_client_name = i.split(' ')[0]
            pod_client_ip = i.split(' ')[24]
        stdin, stdout, stderr = ssh.exec_command(
            'kubectl get pods -o wide|grep server'
        )
        server_logs = stdout.readlines()
        for i in server_logs:
            pod_server_name = i.split(' ')[0]
            pod_server_ip = i.split(' ')[24]

        if pod_client_name == "" or pod_client_ip == "" or pod_server_name == "" or pod_server_ip == "":
            logging.error("create performance pods failed!")
            assert False

        logging.info(
            "create_performance_pods::pod_client_name ==> {}"
            .format(pod_client_name)
        )
        logging.info(
            "create_performance_pods::pod_client_ip ==> {}"
            .format(pod_client_ip)
        )
        logging.info(
            "create_performance_pods::pod_server_name ==> {}"
            .format(pod_server_name)
        )
        logging.info(
            "create_performance_pods::pod_server_ip ==> {}"
            .format(pod_server_ip)
        )
        return pod_client_name, pod_client_ip, pod_server_name, pod_server_ip

    def read_performance_image_id_of_centos7_from_common_config(self):
        return common_config.ali_image_centos7_performance_id

    def exec_cmd(self, cmd=""):
        if cmd == "":
            logging.error(
                "The command to be executed needs to be passed in when calling the function"
            )
            assert False
        logging.info("exec_cmd::cmd ==> {}".format(cmd))
        ssh = ssh_pool.get(
            self.vm_ip, self.ssh_port, self.username, self.password
        )
        stdin, stdout, stderr = ssh.exec_command(cmd)
        logs = stdout.readlines(
        )  # Reading std is a necessary action to trigger the actual execution of the command
        logging.info("exec_cmd::logs ==> {}".format(logs))
        err = stderr.readlines()
        if err:
            logging.error(f"exec_cmd::err ==> {err}")
        return logs, err

    def exec_cmd_use_nohup(self, cmd=""):
        if cmd == "":
            logging.error(
                "The command to be executed needs to be passed in when calling the function"
            )
            assert False
        cmd = "nohup {} &".format(cmd)
        logging.info("exec_cmd_use_nohup::cmd ==> {}".format(cmd))
        ssh = ssh_pool.get(
            self.vm_ip, self.ssh_port, self.username, self.password
        )
        stdin, stdout, stderr = ssh.exec_command(cmd)

    def exec_cmd_except_keyword(
        self, cmd="", keyword="", success_log="", fail_log=""
    ):
        if cmd == "":
            logging.error(
                "The command to be executed needs to be passed in when calling the function"
            )
            assert False

        logging.info("exec_cmd_except_keyword::cmd ==> {}".format(cmd))
        ssh = ssh_pool.get(
            self.vm_ip, self.ssh_port, self.username, self.password
        )
        stdin, stdout, stderr = ssh.exec_command(cmd)

        stdout_list = stdout.readlines()
        stdout_all_content = "".join(stdout_list)
        if keyword != "":
            if bool(re.search(keyword, stdout_all_content)) == True:
                if success_log != "":
                    logging.info(success_log)
                return True
            else:
                if fail_log != "":
                    logging.error(fail_log)
                logging.info(
                    "exec_cmd_except_keyword::stdout_list ==> {}"
                    .format(stdout_list)
                )
                logging.info(
                    "exec_cmd_except_keyword::keyword ==> {}".format(keyword)
                )
                assert False
        return True

    def get_standalone_yaml_file_path(self):
        yaml_file_path = os.path.abspath(__file__)
        par_path = os.path.dirname(yaml_file_path)
        source_file_path = os.path.join(par_path, "files")
        source_file_path = os.path.join(
            source_file_path, "deepflow-agent-standalone.yaml"
        )
        return source_file_path

    def upload_standalone_yaml_file_to_vm(self, source_file_path=""):
        if source_file_path == "":  # if the source file path is empty, the default path is actively obtained
            source_file_path = self.get_standalone_yaml_file_path()
        destination_file_path = '/etc/deepflow-agent-standalone.yaml'
        transport = paramiko.Transport((self.vm_ip, self.ssh_port))
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(
            source_file_path, destination_file_path
        )  # Upload windows files to linux using the put method.
        sftp.close()
        pass

    def upload_file_to_vm(self, source_file_path="", destination_file_path=""):
        if source_file_path == "" or destination_file_path == "":
            assert False
        transport = paramiko.Transport((self.vm_ip, self.ssh_port))
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(
            source_file_path, destination_file_path
        )  # Upload windows files to linux using the put method.
        sftp.close()
