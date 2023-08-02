import logging
import time
from common import common_config
from common.tool.linux_cmd import LinuxCmd
from common.ssh import ssh_pool
import time


class Flow(object):

    def __init__(self):
        self.linux_cmd = LinuxCmd()
        pass

    def vtaps_k8s_create_http_flow(
        self, vtaps_mgt_ip, pod_client_name, pod_server_name, pod_server_ip,
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default
    ):
        '''Login to the vtaps by SSH, use POD to generate http flow,parameter description:
        vtaps_mgt_ip; required field,The ip of vtaps
        pod_client_name; required field,pods that generate http flow
        pod_server_name; required field,Name of the pod that receive http package
        pod_server_ip; required field,Ip of the pod that receive http package
        '''
        ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
        stdin, stdout, stderr = ssh.exec_command(
            'kubectl exec -it %s -- systemctl restart nginx && kubectl exec -it %s -- systemctl status nginx'
            % (pod_server_name, pod_server_name)
        )
        if 'Started nginx' in stdout.readlines()[-1]:
            logging.info("Web server started successfully")
        chan = ssh.invoke_shell()
        chan.send(
            'kubectl exec -ti %s bash\nnohup wrk -t2 -c 3000 -d 300 http://%s/index.html &\n'
            % (pod_client_name, pod_server_ip)
        )
        time.sleep(1)
        start_time = int(time.time())
        logging.info("Start constructing HTTP traffic")
        time.sleep(300)
        end_time = int(time.time())
        logging.info("End constructing HTTP traffic")
        return start_time, end_time

    def vtaps_workloadv_create_http_flow_action_by_cmd(
        self, vtaps_mgt_ip="", cmd="", duration=300
    ):
        pass

    def vtaps_workloadv_create_http_flow_action(
        self, vtaps_mgt_ip, duration=300
    ):
        '''Login to workloadv vtaps by SSH to generate HTTP flow
        '''
        username = common_config.ssh_username_default
        password = common_config.ssh_password_default
        ssh_port = common_config.ssh_port_default

        ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
        stdin, stdout, stderr = ssh.exec_command(
            'systemctl restart nginx && systemctl status nginx'
        )
        if 'Started nginx' in stdout.readlines()[-1]:
            logging.info('Nginx server started successfully')
        chan = ssh.invoke_shell()
        chan.send(
            'nohup wrk -t2 -c 3000 -d {} http://{}/index.html &\n'.format(
                duration, vtaps_mgt_ip
            )
        )
        time.sleep(1)
        start_time = int(time.time())
        logging.info("Start constructing http traffic")
        for i in range(duration // 5):
            time.sleep(5)
            logging.info(
                "Constructing traffic, which has lasted {} seconds".format(
                    i * 5
                )
            )
        end_time = int(time.time())
        logging.info("End constructing http traffic")
        return start_time, end_time

    def vtaps_workloadv_create_tcp_flow_action(
        self, vtaps_mgt_ip, duration=300
    ):
        '''Login to workloadv vtaps by SSH to generate TCP big package
        '''
        username = common_config.ssh_username_default
        password = common_config.ssh_password_default
        ssh_port = common_config.ssh_port_default

        logging.info('Workloadv类型采集器准备开始打TCP流量')
        start_time = int(time.time())
        ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
        stdin, stdout, stderr = ssh.exec_command(
            'iperf3 -s -D && iperf3 -c {} -t {}s -b 5G -M 1400'.format(
                vtaps_mgt_ip, duration
            )
        )
        if 'iperf Done' in stdout.readlines()[-1]:
            logging.info('Workloadv类型采集器完成发送TCP流量')
        end_time = int(time.time())
        return start_time, end_time

    def vtaps_k8s_create_http_flow_action(self, vtaps_mgt_ip):
        '''Create pod and generate http flow,parameter description:
        vtaps_mgt_ip; required field,The ip of vtaps
        '''
        logging.info(
            "vtaps_k8s_create_http_flow_action::vtaps_mgt_ip ==> {}"
            .format(vtaps_mgt_ip)
        )
        pod_client_name, pod_client_ip, pod_server_name, pod_server_ip = self.linux_cmd.create_performance_pods(
            vtaps_mgt_ip
        )
        start_time, end_time = self.vtaps_k8s_create_http_flow(
            vtaps_mgt_ip=vtaps_mgt_ip, pod_client_name=pod_client_name,
            pod_server_ip=pod_server_ip, pod_server_name=pod_server_name
        )
        return start_time, end_time

    def vtaps_k8s_create_http_flow_action_arm(self, vtaps_mgt_ip):
        '''Create pod and generate http flow,parameter description:
        vtaps_mgt_ip; required field,The ip of vtaps
        '''
        logging.info(
            "vtaps_k8s_create_http_flow_action::vtaps_mgt_ip ==> {}"
            .format(vtaps_mgt_ip)
        )
        pod_client_name, pod_client_ip, pod_server_name, pod_server_ip = self.linux_cmd.create_performance_pods_arm(
            vtaps_mgt_ip
        )
        start_time, end_time = self.vtaps_k8s_create_http_flow(
            vtaps_mgt_ip=vtaps_mgt_ip, pod_client_name=pod_client_name,
            pod_server_ip=pod_server_ip, pod_server_name=pod_server_name
        )
        return start_time, end_time
