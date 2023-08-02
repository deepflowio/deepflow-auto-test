# coding: utf-8
"""
author: danqing
date: 2022-09-29
desc: 脚本中常用的函数
"""
import json
import os
import time
import re
import requests
import threading
import allure
import common.url
import traceback

from scp import SCPClient
from functools import wraps

from common import common_config
from common import url
from common import logger
from .ssh import ssh_pool
from .exceptions import BadRequestException, InternalServerErrorException

log = logger.getLogger()


def step(title):
    log.info(title)
    return allure.step(title)


def callback_func():
    log.info('timeout callback')


def exception_decorate(function):

    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)

        except BadRequestException as e:
            log.error(e)
            return json_response(
                status=e.status, description=str(e), wait_callback=False
            ), 400

        except InternalServerErrorException as e:
            log.error(traceback.format_exc())
            return json_response(
                status=e.status, description=str(e), wait_callback=False
            ), 500

        except Exception as e:
            log.error(traceback.format_exc())
            return json_response(
                status="SERVER_ERROR", description=str(e), wait_callback=False
            ), 500

    return wrapper


    # todo logo ...
def time_out(interval, callback=None):

    def decorator(func):

        def wrapper(*args, **kwargs):
            t = threading.Thread(target=func, args=args, kwargs=kwargs)
            # The main to end and the sub-thread to end immediately
            t.setDaemon(True)
            t.start()
            # The main thread blocks and waits for interval seconds
            t.join(interval)
            if t.is_alive() and callback:
                # Immediate execution of callback functions
                return threading.Timer(0, callback).start()
            else:
                return

        return wrapper

    return decorator


def dict_response(
    status="SUCCESS", description=None, data=None, type=None,
    wait_callback=False, task=None, page=None, flag=None, error_message=None
):
    if description is None:
        description = ''
    if task is not None:
        wait_callback = True
    info = {
        'OPT_STATUS': status,
        'WAIT_CALLBACK': wait_callback,
        'TASK': task,
        'DESCRIPTION': description
    }
    if type is None and data is not None:
        if isinstance(data, list):
            if data:
                type = data[0].__class__.__name__
            else:
                type = None
        else:
            type = data.__class__.__name__
    if type is not None:
        info['TYPE'] = type
    if data is not None:
        info['DATA'] = data
    if page is not None:
        info['PAGE'] = page
    if flag is not None:
        info['FLAG'] = flag
    if error_message is not None:
        info['ERROR_MESSAGE'] = error_message
    return info


def json_response(
    status="SUCCESS", description=None, data=None, type=None,
    wait_callback=False, task=None, page=None, flag=None, error_message=None
):
    '''Generate json data for API response

    :param status: response status, HTTP status or specific status
    :param description:
    :param data: resource data
    :types data: list or dict
    :param type:
    :param wait_callback: task synchronization or asynchronous
    :param task:
    :param page:
    :param flag:
    :return:
    '''
    if task is not None:
        wait_callback = True
    data = dict_response(
        status, description, data, type, wait_callback, task, page, flag,
        error_message
    )

    return json.JSONEncoder().encode(data)


class CommonUtils(object):

    def __init__(
        self, df_mgt_ip=None, df_server_controller_port=None,
        df_server_query_port=None, deepflow_server_image_tag=None,
        deepflow_agent_image_tag=None
    ):
        self.df_mgt_ip = df_mgt_ip
        self.df_server_controller_port = df_server_controller_port
        self.df_server_query_port = df_server_query_port
        self.deepflow_server_image_tag = deepflow_server_image_tag
        self.deepflow_agent_image_tag = deepflow_agent_image_tag

    def vtaps_install_k8s(
        self, vtaps_mgt_ip, username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default
    ):
        '''Login to the vtaps by SSH,vtaps Deployment K8S. parameter:
        vtaps_mgt_ip; The ip of vtaps
        username; login username
        password; login password
        ssh_port; port
        '''
        try:
            res = False
            ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
            cmd = '''sealos run localhost/labring/kubernetes:v1.25.0 localhost/calico:v3.24.1 --single && \
                                                        kubectl taint node node-role.kubernetes.io/control-plane- --all'''
            log.info(f"exec cmd: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            logs = stdout.readlines()
            log.info(logs)
            while 30:
                cmd = "kubectl get nodes"
                log.info(f"exec cmd: {cmd}")
                stdin, stdout, stderr = ssh.exec_command(cmd)
                err = stderr.readlines()
                if len(err) > 0:
                    log.error(f'Install K8S Error: {err}, wait about 5s')
                    time.sleep(5)
                else:
                    log.info(stdout.readlines())
                    res = True
                    break
        except Exception as err:
            log.error(
                'vtaps install kubernetes unsuccessful or the cluster status is abnormal, log info is {}'
                .format(err)
            )
            assert False
        if res is False:
            assert False

    def k8s_vtaps_install_deepflow_agent(
        self, vtaps_mgt_ip, cluster_id="",
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default
    ):
        '''Login to the vtaps by SSH,vtaps deployment of deepflow-agent for K8S. parameter:
        vtaps_mgt_ip; The ip of vtaps
        cluster_id; The CLUSTER_ID of domain
        username; login username
        password; login password
        ssh_port; port
        '''
        version = self.deepflow_agent_image_tag if self.deepflow_agent_image_tag else "latest"
        ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
        ssh.exec_command(f"sed -i '2i\  tag: {version}' deepflow-agent.yaml")
        cmd_list = [
            "helm repo add deepflow-agent https://deepflow-ce.oss-cn-beijing.aliyuncs.com/chart/stable",
            "helm repo update deepflow-agent",
            "DEEPFLOW_SERVER_NODE_IPS={}".format(self.df_mgt_ip),
        ]
        if cluster_id:
            cmd_list.append("CLUSTER_ID={}".format(cluster_id))
            cmd_list.append(
                "helm install deepflow-agent -n deepflow deepflow-agent/deepflow-agent --create-namespace --set deepflowServerNodeIPS={$DEEPFLOW_SERVER_NODE_IPS} --set deepflowK8sClusterID=$CLUSTER_ID -f deepflow-agent.yaml"
            )
        else:
            cmd_list.append(
                "helm install deepflow-agent -n deepflow deepflow-agent/deepflow-agent --create-namespace --set deepflowServerNodeIPS={$DEEPFLOW_SERVER_NODE_IPS}  -f deepflow-agent.yaml"
            )
        cmd = " && ".join(cmd_list)
        log.info(f"Vtap Install Exec CMD: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        logs = stdout.readlines()
        err = stderr.readlines()
        if err:
            log.error(f"k8s install agent error: {err}")
            assert False
        log.info(logs)
        try:
            if 'deepflow-agent Host listening port:' in logs[-1]:
                log.info(
                    'Deploy the deepflow-agent successfully in kubernetes'
                )
                stdin, stdout, stderr = ssh.exec_command(
                    'kubectl get pods -n deepflow'
                )
                logs = stdout.readlines()
                log.info(logs)
        except Exception as err:
            log.error(err)
        #ssh.close()

    # def k8s_vtaps_install_deepflow_agent_with_cluster_id(
    #     self, vtaps_mgt_ip="", cluster_id="",
    #     username=common_config.ssh_username_default,
    #     password=common_config.ssh_password_default,
    #     ssh_port=common_config.ssh_port_default
    # ):
    #     version = self.deepflow_agent_image_tag if self.deepflow_agent_image_tag else "latest"
    #     ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
    #     ssh.exec_command(f"sed -i '2i\  tag: {version}' deepflow-agent.yaml")
    #     cmd_list = [
    #         "helm repo add deepflow-agent https://deepflow-ce.oss-cn-beijing.aliyuncs.com/chart/stable",
    #         "helm repo update deepflow-agent",
    #         "DEEPFLOW_SERVER_NODE_IPS={}".format(self.df_mgt_ip),
    #         "CLUSTER_ID={}".format(cluster_id),
    #         "helm install deepflow-agent -n deepflow deepflow-agent/deepflow-agent --create-namespace --set deepflowServerNodeIPS={$DEEPFLOW_SERVER_NODE_IPS} --set deepflowK8sClusterID=$CLUSTER_ID -f deepflow-agent.yaml"
    #     ]
    #     cmd = " && ".join(cmd_list)
    #     _, stdout, stderr = ssh.exec_command(cmd)
    #     log.info(f"k8s install agent with cluster id:{stdout.readlines()}")
    #     err = stderr.readlines()
    #     if err:
    #         log.error(f"k8s install agent with cluster id error: {err}")
    #         assert False

    def vtaps_install_deepflow_action(self, vtaps_mgt_ip):
        '''Create k8s on DF and deploy the latest version of deepflow-agent on k8s, parameters:
        vtaps_mgt_ip; the ip of vtaps
        '''
        self.vtaps_install_k8s(vtaps_mgt_ip=vtaps_mgt_ip)
        self.k8s_vtaps_install_deepflow_agent(vtaps_mgt_ip=vtaps_mgt_ip)
        return True

    def vm_install_unzip(
        self, vm_ip, ssh_port=common_config.ssh_port_default,
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default
    ):
        ssh = ssh_pool.get(vm_ip, ssh_port, username, password)
        stdin, stdout, stderr = ssh.exec_command(
            '''cat /dev/null > /etc/resolv.conf && echo 'nameserver {}' >> /etc/resolv.conf && \
                curl -O http://nexus.yunshan.net/repository/tools/automation/offline/unzip/unzip-6.0-24.el7_9.x86_64.rpm &&\
                rpm -ivh unzip-6.0-24.el7_9.x86_64.rpm'''.format(
                common_config.ali_dns_ip
            )
        )
        err = stderr.readlines()
        if err:
            log.error(err)
            assert False
        log.info(stdout.readlines)

    def workloadv_vtaps_install_deepflow_agent(
        self, vtaps_mgt_ip, ssh_port=common_config.ssh_port_default,
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default
    ):
        '''Login to the vtaps by SSH,workloadv type vtaps deployment of deepflow-agent. parameter:
        vtaps_mgt_ip; The ip of deepflow
        username; login username
        password; login password
        ssh_port; port
        '''
        version = self.deepflow_agent_image_tag if self.deepflow_agent_image_tag else "latest"
        ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
        stdin, stdout, stderr = ssh.exec_command(
            '''cat /dev/null > /etc/resolv.conf &&\
                                                    echo 'nameserver {}' >> /etc/resolv.conf &&\
                                                    curl -O https://deepflow-ce.oss-cn-beijing.aliyuncs.com/rpm/agent/{}/linux/amd64/deepflow-agent-rpm.zip &&\
                                                    unzip deepflow-agent-rpm.zip &&\
                                                    rpm -ivh x86_64/deepflow-agent-1*.rpm &&\
                                                    sed -i 's/  - 127.0.0.1/  - {}/g' /etc/deepflow-agent.yaml &&\
                                                    systemctl restart deepflow-agent && systemctl status deepflow-agent'''
            .format(common_config.ali_dns_ip, version, self.df_mgt_ip)
        )
        try:
            if bool(
                re.search('active \(running\)', "".join(stdout.readlines()))
            ) == True:
                log.info(
                    'centos7采集器deepflow-agent部署成功且进行正常,采集器的IP地址是{}'
                    .format(vtaps_mgt_ip)
                )
        except Exception as err:
            log.info(err)

    def loop_check_vtaps_list_by_name(self, counts, vtaps_name):
        '''Loop to check if vtaps_list contains vtap by name of vtaps. parameter:
        counts; required, number of checks
        vtaps_name; name of vtaps
        '''
        vtaps_full_name = ''
        lcuuid = ''
        for i in range(counts):
            log.info('Wait for vtaps synchronization, about 60s')
            time.sleep(60)
            vtaps_url = url.protocol + self.df_mgt_ip + ':' + str(
                self.df_server_controller_port
            ) + url.vtaps_list_api_prefix
            res = requests.get(url=vtaps_url)
            for i in res.json()['DATA']:
                if vtaps_name in i['NAME']:
                    vtaps_full_name = i['NAME']
                    lcuuid = i['LCUUID']
                    break
            if len(vtaps_full_name) > 0:
                log.info(
                    'The vtap was synchronized successfully, the name of is%s'
                    % (vtaps_full_name)
                )
                break
        if not vtaps_full_name:
            log.error(f'vtaps synchronization failure, the nameof is{vtaps_name}')
            assert False
        return lcuuid

    def loop_check_vtaps_list_by_ip(self, counts, vtaps_mgt_ip):
        '''Loop to check if vtaps_list contains vtap by ip of vtaps. parameter:
        counts; required, number of checks
        vtaps_name; name of vtaps
        '''
        res = 0
        lcuuid = None
        for i in range(counts):
            log.info('Wait for vtaps synchronization, about 60s')
            time.sleep(60)
            vtaps_url = url.protocol + self.df_mgt_ip + ':' + str(
                self.df_server_controller_port
            ) + url.vtaps_list_api_prefix
            res = requests.get(url=vtaps_url)
            for i in res.json()['DATA']:
                if vtaps_mgt_ip == i['LAUNCH_SERVER']:
                    res = 1
                    lcuuid = i['LCUUID']
                    break
            try:
                if res == 1:
                    log.info(
                        'The vtap was synchronized successfully, the ip of is%s'
                        % (vtaps_mgt_ip)
                    )
                    break
            except Exception as err:
                log.info(err)
        if not lcuuid:
            log.error(f'vtaps synchronization failure, the ip of is {vtaps_mgt_ip}')
            assert False
        return lcuuid

    def delete_vtaps_list_by_name(self, vtaps_name):
        '''Delete vtaps by the partial name of the vtaps,
        vtaps_name;required, The partial name of vtaps
        '''
        vtaps_lcuuid = ''
        vtaps_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.df_server_controller_port
        ) + url.vtaps_list_api_prefix
        res = requests.get(url=vtaps_url)
        for i in res.json()['DATA']:
            if vtaps_name in i['NAME']:
                vtaps_lcuuid = i['LCUUID']
                break
        vtaps_url_lcuuid = url.protocol + self.df_mgt_ip + ':' + str(
            self.df_server_controller_port
        ) + url.vtaps_list_api_prefix + '/%s/' % (
            vtaps_lcuuid
        )
        res = requests.delete(url=vtaps_url_lcuuid)
        try:
            if res.status_code == 200:
                log.info('The vtap was successfully removed')
        except Exception as err:
            log.info(err)

    def delete_domain_list_by_name(self, vtaps_name):
        '''Delete domain by the partial name of the vtaps,
        vtaps_name;required, The partial name of vtaps
        '''
        domain_lcuuid = ''
        domain_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.df_server_controller_port
        ) + url.v1_domains_api_prefix
        res = requests.get(url=domain_url)
        for i in res.json()['DATA']:
            if vtaps_name in i['NAME']:
                domain_lcuuid = i['LCUUID']
                break
        domain_url_lcuuid = url.protocol + self.df_mgt_ip + ':' + str(
            self.df_server_controller_port
        ) + url.vtaps_list_api_prefix + '/%s/' % (
            domain_lcuuid
        )
        res = requests.delete(url=domain_url_lcuuid)
        try:
            if res.status_code == 200:
                log.info('The domain was successfully removed')
        except Exception as err:
            log.info(err)

    def delete_domain_list_by_ip(self, vtaps_mgt_ip):
        '''Delete domain by the ip of the vtaps,
        vtaps_mgt_ip;required, The ip of vtaps
        '''
        domain_lcuuid = ''
        domain_id = ''
        domain_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.df_server_controller_port
        ) + url.domains_api_prefix
        try:
            res = requests.get(url=domain_url)
            for i in res.json()['DATA']:
                if vtaps_mgt_ip == i['VTAP_CTRL_IP']:
                    domain_lcuuid = i['LCUUID']
                    domain_id = i['ID']
                    break
            domain_url_lcuuid = url.protocol + self.df_mgt_ip + ':' + str(
                self.df_server_controller_port
            ) + url.vtaps_list_api_prefix + '/{}/'.format(domain_lcuuid)
            res = requests.delete(url=domain_url_lcuuid)
            if res.status_code == 200:
                log.info(
                    'domain has been deleted by deepflow, domain id is {}'
                    .format(domain_id)
                )
        except Exception as err:
            log.error('delete domain failed, log info is {}'.format(err))

    def get_domain_name_by_vtap_ip(self, vtaps_mgt_ip):
        domain_name = ''
        domain_list = self.get_domains_list()
        for i in domain_list:
            if i['VTAP_CTRL_IP'] == vtaps_mgt_ip:
                domain_name = i['NAME']
                break
        return domain_name

    def get_vtaps_name_by_name(self, vtaps_name):
        '''Get vtap_full_name by the partial name of the vtaps, parameter:
        vtaps_name; required, The partial name of vtaps
        self.df_mgt_ip; optional, The ip of deepflow
        '''
        vtap_name = ''
        vtaps_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.df_server_controller_port
        ) + url.vtaps_list_api_prefix
        res = requests.get(url=vtaps_url)
        try:
            if res.status_code == 200:
                json_str = res.json()['DATA']
                for i in json_str:
                    if vtaps_name in i['NAME']:
                        vtap_name = i['NAME']
                        break
                return vtap_name
        except Exception as err:
            log.error(err)
            assert False

    def get_vtaps_full_name_by_ip(self, vtaps_mgt_ip):
        '''Get vtap_full_name by the ip of the vtaps, parameter:
        vtaps_mgt_ip; required, The ip of vtaps
        self.df_mgt_ip; optional, The ip of deepflow
        '''
        vtap_full_name = ''
        vtaps_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.df_server_controller_port
        ) + url.vtaps_list_api_prefix
        res = requests.get(url=vtaps_url)
        try:
            if res.status_code == 200:
                json_str = res.json()['DATA']
                for i in json_str:
                    if vtaps_mgt_ip == i['LAUNCH_SERVER']:
                        vtap_full_name = i['NAME']
                        break
        except Exception as err:
            log.error(
                'get vtap{} name failed, log info is {}'.format(
                    vtaps_mgt_ip, err
                )
            )
            assert False
        if not vtap_full_name:
            log.error(
                'get vtap{} name failed, res {}'.format(
                    vtaps_mgt_ip, res.content
                )
            )
            assert False
        return vtap_full_name

    def get_domains_list(self):
        '''Get domains information on DeepFlow by API, parameter:
        self.df_mgt_ip; The ip of deepflow
        return responsion data
        '''
        get_domain_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.df_server_controller_port
        ) + url.domains_api_prefix
        loop_num = 30
        while loop_num:
            try:
                res = requests.get(url=get_domain_url)
                if res.status_code == 200:
                    json_str = res.json()['DATA']
                    log.info(
                        f"get_domains_list url: {get_domain_url} response:{json_str} "
                    )
                    return json_str
            except Exception as err:
                log.info(err)
                time.sleep(10)
                loop_num -= 1
        assert False

    def get_vtaps_list(self):
        '''Get vtaps information on DeepFlow by API, parameter:
        self.df_mgt_ip; The ip of deepflow
        '''
        get_vtap_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.df_server_controller_port
        ) + url.vtaps_list_api_prefix
        res = requests.get(url=get_vtap_url)
        try:
            if res.status_code == 200:
                json_str = res.json()['DATA']
                if not json_str:
                    return []
                return json_str
            else:
                log.error(
                    f'Get Vtap List Error: {res.status_code} {res.json()}'
                )
                return []
        except Exception as err:
            log.error(err)

    def get_vtaps_group_list(self):
        '''Get vtaps group information on DeepFlow by API, parameter:
        self.df_mgt_ip; The ip of deepflow
        '''
        get_vtap_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.df_server_controller_port
        ) + url.vtaps_group_list_api_prefix
        res = requests.get(url=get_vtap_url)
        try:
            if res.status_code == 200:
                json_str = res.json()['DATA']
                if not json_str:
                    log.warning(f'Get Vtap List None: {res.json()}')
                    return []
                return json_str
            else:
                log.error(
                    f'Get Vtap Group List Error: {res.status_code} {res.json()}'
                )
                return []
        except Exception as err:
            log.error(err)

    def loop_check_domain_sync_info(
        self, count, domains_data, domain_content, domains_value
    ):
        '''Repeatedly view the contents of domains information by the DF's API. parameter:
        count: Number of check
        self.df_mgt_ip; The ip of deepflow
        domains_data; All information about domain
        domain_content; Fields for checking judgments
        domains_value; name of the field to be checked
        '''
        sync_info = ''
        for i in range(count):
            log.info('DF is synchronizing with domain. Wait 60s.')
            time.sleep(60)
            domains_info = domains_data(self.df_mgt_ip)
            for k in domains_info:
                if domain_content == k['{}'.format(domains_value)]:
                    sync_info = k['SYNCED_AT']
                    break
            if len(sync_info) > 0:
                log.info('DF Synchronization domain Success')
                break

    def del_k8s_domains(self, lcuuid):
        '''Remove domain information on DeepFlow based on lcuuid, parameter:
        lcuuid; The lcuuid value of the domains
        self.df_mgt_ip; The ip of deepflow
        '''
        del_domain_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.df_server_controller_port
        ) + url.v1_domains_api_prefix + '%s/' % (
            lcuuid
        )
        try:
            res = requests.delete(url=del_domain_url)
            if res.status_code == 200:
                result = True
                log.info(
                    'Deleting the k8s domain was successful and the lcuuid was%s'
                    % (lcuuid)
                )
                return result
        except Exception as err:
            log.info(err)

    def get_query_port(
        self, username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default
    ):
        '''Login to the deepflow by SSH, Deepflow gets query_port, parameter:
        self.df_mgt_ip; The ip of deepflow
        username; login username
        password; login password
        ssh_port; port
        '''
        ssh = ssh_pool.get(self.df_mgt_ip, ssh_port, username, password)
        query_api_port = None
        while True:
            try:
                stdin, stdout, stderr = ssh.exec_command(
                    '''kubectl get svc -n deepflow|grep -o "20416:[0-9]*" | cut -d ":" -f 2
                '''
                )
                query_api_port = stdout.readlines()[0]
                break
            except:
                time.sleep(3)
                continue
        return query_api_port

    def get_controller_port(
        self, username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default
    ):
        '''Login to the deepflow by SSH, Deepflow gets controller_port, parameter:
        self.df_mgt_ip; The ip of deepflow
        username; login username
        password; login password
        ssh_port; port
        '''
        ssh = ssh_pool.get(self.df_mgt_ip, ssh_port, username, password)
        controller_api_port = None
        while True:
            try:
                stdin, stdout, stderr = ssh.exec_command(
                    '''kubectl get svc -n deepflow|grep -o "20417:[0-9]*" | cut -d ":" -f 2
                '''
                )
                controller_api_port = stdout.readlines()[0]
                break
            except:
                time.sleep(3)
                continue
        return controller_api_port

    def add_deepflow_server_dns(
        self, dns_server=common_config.ext_dns_server,
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default
    ):
        '''add dns server for deepflow_server, parameter;
        dns_server; default, type is string
        username; default, type is string
        password; default, type is string
        ssh_port; default, type is string
        self.df_mgt_ip; default, type is string
        '''
        ssh = ssh_pool.get(self.df_mgt_ip, ssh_port, username, password)
        stdin, stdout, stderr = ssh.exec_command(
            '''kubectl get deployment deepflow-server -n deepflow -o yaml > deepflow-server-dns.yaml && \
                                                    sed -i "/dnsPolicy: ClusterFirst/a\      dnsConfig:" deepflow-server-dns.yaml && \
                                                    sed -i "/      dnsConfig:/a\         nameservers:" deepflow-server-dns.yaml && \
                                                    sed -i "/         nameservers:/a\         - {}" deepflow-server-dns.yaml &&\
                                                    kubectl apply -f deepflow-server-dns.yaml'''
            .format(dns_server)
        )
        logs = stdout.readlines()
        if logs is not None:
            for i in range(20):
                stdin, stdout, stderr = ssh.exec_command(
                    'kubectl get pods -n deepflow|grep deepflow-server'
                )
                deepflow_server_status = ''.join(stdout.readlines()[0])
                if 'Running' in deepflow_server_status:
                    log.info('deepflow server status is running now, wait 30s')
                    time.sleep(30)
                    log.info('deepflow server status is normal')
                    break
                else:
                    log.info('deepflow server is pending now, wait for 10s')
                    time.sleep(10)

    def check_aliyun_cloud_isexist(self):
        '''determine whether Aliyun Cloud platform exists, parameter;
        self.df_mgt_ip; default, type is string
        '''
        result = False
        domain_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.df_server_controller_port
        ) + url.domains_api_prefix
        loop_num = 30
        while loop_num:
            try:
                res = requests.get(url=domain_url)
                if res.status_code == 200:
                    res_json = res.json()['DATA']
                    for i in res_json:
                        if i['TYPE'] == 9:
                            result = True
                            log.info('aliyun cloud is exist')
                            break
                        else:
                            log.info("aliyun cloud doesn't exist")
                break
            except Exception as e:
                loop_num -= 1
                log.error(f"get domain error: {e}")
                time.sleep(10)
        return result

    @time_out(900)
    def check_aliyun_cloud_status(
        self, cloud_name=common_config.ali_name_default
    ):
        '''check aliyun cloud status, parameter;
        cloud_name, required, type is string
        self.df_mgt_ip, default, type is string
        '''
        result = False
        loop_num = 30
        while loop_num:
            try:
                domain_url = url.protocol + self.df_mgt_ip + ':' + str(
                    self.df_server_controller_port
                ) + url.domains_api_prefix
                res = requests.get(url=domain_url)
                if res.status_code == 200:
                    res_json = res.json()['DATA']
                    log.info(f'aliyun domain info: {res_json}')
                    for i in res_json:
                        if i['NAME'] == cloud_name and i['TYPE'] == 9 and i[
                            'STATE'] == 1 and i['ENABLED'] == 1 and len(
                                i['SYNCED_AT']
                            ) > 0:
                            log.info('aliyun cloud platform status is normal')
                            result = True
                            break
                if result:
                    break
                else:
                    log.info('wait for aliyun cloud sync, about 10s')
                    time.sleep(10)
                    loop_num -= 1
            except Exception as e:
                log.error(f'aliyun cloud sync error: {e}')
                time.sleep(10)
                loop_num -= 1
        return result

    def install_deepflow_ctl(
        self, ssh_port=common_config.ssh_port_default,
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default
    ):
        cmds = [
            "curl -o /usr/bin/deepflow-ctl https://deepflow-ce.oss-cn-beijing.aliyuncs.com/bin/ctl/stable/linux/$(arch | sed 's|x86_64|amd64|' | sed 's|aarch64|arm64|')/deepflow-ctl",
            "chmod a+x /usr/bin/deepflow-ctl",
            "deepflow_server_pod_ip=$(kubectl -n deepflow get pods -o wide | grep deepflow-server | awk '{print $6}')",
            "deepflow-ctl -i $deepflow_server_pod_ip ingester profiler on"
        ]
        ssh = ssh_pool.get(self.df_mgt_ip, ssh_port, username, password)
        for cmd in cmds:
            _, stdout, stderr = ssh.exec_command(cmd)
            err = stderr.readlines()
            if err:
                log.error(err)
            log.info(stdout.readlines())
        return

    def save_df_server_log(
        self,
        local_filename="",
        ssh_port=common_config.ssh_port_default,
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
    ):

        try:
            ssh = ssh_pool.get(self.df_mgt_ip, ssh_port, username, password)
            cmd = "kubectl logs $(kubectl get pod -n deepflow|grep server|awk 'NR==1'|awk '{print $1}') -n deepflow > df-server.log"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            err = stderr.readlines()
            if err:
                log.error(f"get log error: {err}")
            scpclient = SCPClient(ssh.get_transport(), socket_timeout=15.0)
            scpclient.get("/root/df-server.log", f"test_logs/{local_filename}")
        except Exception as e:
            log.error(f"save log error: {e}")
            assert False

    def restart_deepflow_server(
        self,
        ssh_port=common_config.ssh_port_default,
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
    ):
        try:
            ssh = ssh_pool.get(self.df_mgt_ip, ssh_port, username, password)
            cmd = "kubectl delete pod $(kubectl get pod -n deepflow|grep server|awk 'NR==1'|awk '{print $1}') -n deepflow"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            err = stderr.readlines()
            if err:
                log.error(f"restart server error: {err}")
            time.sleep(300)
        except Exception as e:
            log.error(f"restart server exception: {e}")
            assert False

    def add_aliyun_cloud_platform(
        self, cloud_name=common_config.ali_name_default
    ):
        '''add aliyun cloud platform, parameter;
        cloud_name, default, type is string
        '''
        result = False
        loop_num = 30
        while loop_num:
            try:
                domain_url = url.protocol + self.df_mgt_ip + ':' + str(
                    self.df_server_controller_port
                ) + url.v1_domains_api_prefix
                header = {'content-type': 'application/json'}
                data = {
                    "TYPE": 9,
                    "NAME": "{}".format(cloud_name),
                    "ICON_ID": 8,
                    "CONFIG": {
                        "region_uuid": "ffffffff-ffff-ffff-ffff-ffffffffffff",
                        "controller_ip": "{}".format(self.df_mgt_ip),
                        "secret_id": "{}".format(
                            os.getenv('ALICLOUD_ACCESS_KEY')
                        ),
                        "secret_key": "{}".format(
                            os.getenv('ALICLOUD_SECRET_KEY')
                        ),
                        "include_regions": "华北2（北京）",
                        "exclude_regions": "华南3（广州）,欧洲中部 1 (法兰克福),中东东部 1 (迪拜),英国 (伦敦),美国西部 1 (硅谷),美国东部 1 (弗吉尼亚),亚太南部 1 (孟买),亚太东南 3 (吉隆坡),亚太东南 5 (雅加达),亚太东南 2 (悉尼),亚太东南 1 (新加坡),亚太东北 1 (东京),香港,华北6（乌兰察布）,华东5（南京-本地地域）",
                        "k8s_confs": ""
                    }
                }
                data = json.dumps(data)
                res = requests.post(url=domain_url, headers=header, data=data)
                if res.status_code == 200:
                    log.info('add aliyun cloud successfully')
                    result = True
                    break
            except Exception as err:
                log.error(
                    'add aliyun cloud failed, log info is {}'.format(err)
                )
                time.sleep(10)
                loop_num -= 1
        return result

    def delete_aliyun_cloud_platform(self):
        '''delete aliyun cloud platform, parameter;
        self.df_mgt_ip, default, type is string
        '''
        try:
            domain_url = url.protocol + self.df_mgt_ip + ':' + str(
                self.df_server_controller_port
            ) + url.domains_api_prefix
            lcuuid = ''
            res = requests.get(url=domain_url)
            if res.status_code == 200:
                res_json = res.json()['DATA']
                for i in res_json:
                    if i['TYPE'] == 9:
                        lcuuid = i['LCUUID']
                        break
            delete_domain_url = url.protocol + self.df_mgt_ip + ':' + str(
                self.df_server_controller_port
            ) + url.v1_domains_api_prefix + '{}/'.format(lcuuid)
            res = requests.delete(url=delete_domain_url)
            if res.status_code == 200:
                log.info('delete aliyun cloud successfully')
        except Exception as err:
            log.error('delete aliyun cloud failed, log info is {}'.format(err))

    def delete_vtaps_list_by_ip(self, vtaps_mgt_ip):
        vtaps_lcuuid = None
        vtaps_list_info = self.get_vtaps_list()
        for i in vtaps_list_info:
            if i['LAUNCH_SERVER'] == vtaps_mgt_ip:
                vtaps_lcuuid = i['LCUUID']
                break
        delete_vtap_url = f"http://{self.df_mgt_ip}:{self.df_server_controller_port}{common.url.vtaps_list_api_prefix}/{vtaps_lcuuid}/"
        res = requests.delete(url=delete_vtap_url)
        if res.status_code == 200:
            pass
        else:
            assert False

    def get_deepflow_hostname(
        self,
        ssh_port=common_config.ssh_port_default,
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
    ):
        '''Login to the deepflow by SSH,Get the hostname of deepflow
        deepflow_mgt_ip; The ip of deepflow
        ssh_port; port
        username; login username
        password; login password
        '''
        ssh = ssh_pool.get(self.df_mgt_ip, ssh_port, username, password)
        stdin, stdout, stderr = ssh.exec_command('hostname')
        deepflow_hostname = stdout.readlines()[0].split('\n')[0]
        return deepflow_hostname

    def get_agent_and_server_commit_id(
        self, is_pod=True, ssh_port=common_config.ssh_port_default,
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default
    ) -> dict:
        commit_ids = {}
        component_names = ["server", "agent"]
        if is_pod:
            cmd = "kubectl exec -it $(kubectl get pod -n deepflow|grep {component_name}|awk '{{print $1}}') -n deepflow -- deepflow-{component_name} -v |grep CommitI| awk '{{print $2}}'"
        else:
            cmd = "deepflow-{component_name} -v|grep CommitI| awk '{{print $2}}'"
        for name in component_names:
            log.info(
                f"exec get {name} commit id cmd: {cmd.format(component_name=name)}"
            )
            ssh = ssh_pool.get(self.df_mgt_ip, ssh_port, username, password)
            stdin, stdout, stderr = ssh.exec_command(
                cmd.format(component_name=name)
            )
            logs = stdout.readlines()
            log.info(logs)
            if not logs:
                err = stderr.readlines()
                log.error(f"get {name} commit id error: {err}")
                commit_ids[name] = ""
                continue
            commit_ids[name] = logs[-1].strip('\n')[:8]
        return commit_ids

    def install_unzip(
        self, vm_ip, username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default
    ):
        ssh = ssh_pool.get(vm_ip, ssh_port, username, password)
        _, stdout, stderr = ssh.exec_command("unzip -hh")
        err = stderr.readlines()
        if err:
            log.info("vtap install unzip")
            stdin, stdout, stderr = ssh.exec_command(
                "curl -O http://nexus.yunshan.net/repository/tools/automation/offline/unzip/unzip-6.0-24.el7_9.x86_64.rpm && \
                    rpm -ivh unzip-6.0-24.el7_9.x86_64.rpm"
            )
            err = stderr.readlines()
            if err:
                log.error(f"vtap install unzip error: {err}")

    def vtaps_install_deepflow_agent_lastest_rpm(
        self, vtaps_mgt_ip, username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default, system_platform='linux',
        cluster_id=''
    ):
        '''Login to the vtaps by SSH,Deploy and start the latest version of deepflow-agent. parameter:
        vtaps_mgt_ip; The ip of vtaps
        username; login username
        password; login password
        ssh_port; port
        '''
        ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
        stdin, stdout, stderr = ssh.exec_command(
            '''cat /dev/null > /etc/resolv.conf && echo "nameserver %s" > /etc/resolv.conf && cat /etc/issue '''
            % (common_config.ali_dns_ip)
        )
        system_version = stdout.readlines()[0]
        version = self.deepflow_agent_image_tag if self.deepflow_agent_image_tag else "latest"
        if system_platform == 'linux' and '\S' in system_version:
            self.install_unzip(vtaps_mgt_ip)
            rpm_url = common_config.deepflow_agent_rpm_lastest_url.replace(
                "latest", version
            )
            stdin, stdout, stderr = ssh.exec_command(
                '''curl -O %s &&\
                                                     unzip deepflow-agent-rpm.zip &&\
                                                     rpm -ivh x86_64/deepflow-agent-1*.rpm &&\
                                                     sed -i 's/  - 127.0.0.1/  - %s/g' /etc/deepflow-agent.yaml &&\
                                                     systemctl restart deepflow-agent && systemctl status deepflow-agent'''
                % (rpm_url, self.df_mgt_ip)
            )
            if bool(
                re.search('active \(running\)', "".join(stdout.readlines()))
            ) == True:
                log.info(
                    'centos7 deployed deepflow-agent successfully and running normally, vtap ip addres is {}'
                    .format(vtaps_mgt_ip)
                )
                #ssh.close()
            else:
                log.error(
                    'centos7 failed to deploy deepflow-agent, vtap ip addr is {}, err: {}'
                    .format(vtaps_mgt_ip, stderr.readlines())
                )
                #ssh.close()
                assert False
        elif system_platform == 'linux' and 'Ubuntu' in system_version and int(
            system_version.split(' ')[1].split('.')[0]
        ) == 14:
            deb_url = common_config.deepflow_agent_deb_lastest_url.replace(
                "latest", version
            )
            stdin, stdout, stderr = ssh.exec_command(
                '''curl -O %s &&\
                                                        curl -O http://nexus.yunshan.net/repository/tools/automation/offline/unzip/unzip_6.0-9ubuntu1.5_amd64.deb &&\
                                                        dpkg -i unzip_6.0-9ubuntu1.5_amd64.deb &&\
                                                        unzip deepflow-agent-deb.zip &&\
                                                        dpkg -i x86_64/deepflow-agent-*.upstart.deb &&\
                                                        sed -i 's/  - 127.0.0.1/  - %s/g' /etc/deepflow-agent.yaml &&\
                                                        service deepflow-agent restart && service deepflow-agent status'''
                % (deb_url, self.df_mgt_ip)
            )
            if bool(
                re.search(
                    'deepflow-agent start/running',
                    "".join(stdout.readlines())
                )
            ) == True:
                log.info(
                    '{} deployed deepflow-agent successfully and running normally, vtap ip addr is {}'
                    .format(
                        system_version.split(' ')[0] +
                        system_version.split(' ')[1], vtaps_mgt_ip
                    )
                )
                #ssh.close()
            else:
                log.error(
                    '{} failed to deploy deepflow-agent, vtap ip addr is {}'
                    .format(
                        system_version.split(' ')[0] +
                        system_version.split(' ')[1], vtaps_mgt_ip
                    )
                )
                #ssh.close()
                assert False
        elif system_platform == 'linux' and 'Ubuntu' in system_version and int(
            system_version.split(' ')[1].split('.')[0]
        ) >= 14:
            ubuntu_url = common_config.deepflow_agent_deb_lastest_url.replace(
                "latest", version
            )
            stdin, stdout, stderr = ssh.exec_command(
                '''curl -O %s &&\
                                                        curl -O http://nexus.yunshan.net/repository/tools/automation/offline/unzip/unzip_6.0-9ubuntu1.5_amd64.deb &&\
                                                        dpkg -i unzip_6.0-9ubuntu1.5_amd64.deb &&\
                                                        unzip deepflow-agent-deb.zip &&\
                                                        dpkg -i x86_64/deepflow-agent-*.systemd.deb &&\
                                                        sed -i 's/  - 127.0.0.1/  - %s/g' /etc/deepflow-agent.yaml  &&\
                                                        systemctl restart deepflow-agent && systemctl status deepflow-agent'''
                % (ubuntu_url, self.df_mgt_ip)
            )
            if bool(
                re.search('active \(running\)', "".join(stdout.readlines()))
            ) == True:
                log.info(
                    '{} deployed deepflow-agent successfully and running normally, vtap ip addr is {}'
                    .format(
                        system_version.split(' ')[0] +
                        system_version.split(' ')[1], vtaps_mgt_ip
                    )
                )
                #ssh.close()
            else:
                log.error(
                    '{} failed to deploy deepflow-agent, vtap ip addr is {}'
                    .format(
                        system_version.split(' ')[0] +
                        system_version.split(' ')[1], vtaps_mgt_ip
                    )
                )
                #ssh.close()
                assert False
        elif system_platform == 'linux' and 'Debian' in system_version:
            debian_url = common_config.deepflow_agent_deb_lastest_url.replace(
                "latest", version
            )
            stdin, stdout, stderr = ssh.exec_command(
                '''curl -O %s &&\
                                                        curl -O http://nexus.yunshan.net/repository/tools/automation/offline/unzip/unzip_6.0-9ubuntu1.5_amd64.deb &&\
                                                        dpkg -i unzip_6.0-9ubuntu1.5_amd64.deb &&\
                                                        unzip deepflow-agent-deb.zip &&\
                                                        dpkg -i x86_64/deepflow-agent-*.systemd.deb &&\
                                                        sed -i 's/  - 127.0.0.1/  - %s/g' /etc/deepflow-agent.yaml  &&\
                                                        systemctl restart deepflow-agent && systemctl status deepflow-agent'''
                % (debian_url, self.df_mgt_ip)
            )
            if bool(
                re.search('active \(running\)', "".join(stdout.readlines()))
            ) == True:
                log.info(
                    '{} deployed deepflow-agent successfully and running normally, vtap ip addr is {}'
                    .format(
                        system_version.split(' ')[0] +
                        system_version.split(' ')[2], vtaps_mgt_ip
                    )
                )
                print(
                    '{} deployed deepflow-agent successfully and running normally, vtap ip addr is {}'
                    .format(
                        system_version.split(' ')[0] +
                        system_version.split(' ')[2], vtaps_mgt_ip
                    )
                )
                #ssh.close()
            else:
                log.error(
                    '{} failed to deploy deepflow-agent, vtap ip addr is {}'
                    .format(
                        system_version.split(' ')[0] +
                        system_version.split(' ')[1], vtaps_mgt_ip
                    )
                )
                print(
                    '{} failed to deploy deepflow-agent, vtap ip addr is {}'
                    .format(
                        system_version.split(' ')[0] +
                        system_version.split(' ')[1], vtaps_mgt_ip
                    )
                )
                #ssh.close()
                assert False
        elif system_platform == 'arm':
            arm_url = f"https://deepflow-ce.oss-cn-beijing.aliyuncs.com/rpm/agent/{version}/linux/$(arch | sed 's|x86_64|amd64|' | sed 's|aarch64|arm64|')/deepflow-agent-rpm.zip"
            stdin, stdout, stderr = ssh.exec_command(
                '''curl -O %s &&\
                                                        unzip deepflow-agent*.zip &&\
                                                        rpm -ivh aarch64/deepflow-agent-1*.rpm &&\
                                                        sed -i 's/  - 127.0.0.1/  - %s/g' /etc/deepflow-agent.yaml &&\
                                                        systemctl restart deepflow-agent && systemctl status deepflow-agent
                                                        ''' %
                (arm_url, self.df_mgt_ip)
            )
            if bool(
                re.search('active \(running\)', "".join(stdout.readlines()))
            ) == True:
                log.info(
                    'arm deployed deepflow-agent successfully and running normally, vtap ip addr is {}'
                    .format(vtaps_mgt_ip)
                )
                #ssh.close()
            else:
                log.error(
                    'arm failed to deploy deepflow-agent, vtap ip addr is {}'
                    .format(vtaps_mgt_ip)
                )
                #ssh.close()
                assert False


class ASSERT(object):

    def __init__(self):
        pass

    @classmethod
    def assert_real_equal_except(cls, real_value, except_value):
        if real_value != except_value:
            log.info("real_value ==> {}".format(real_value))
            log.info("except_value ==> {}".format(except_value))
            assert False

    @classmethod
    def assert_real_not_equal_except(cls, real_value, except_value):
        if real_value == except_value:
            log.info("real_value ==> {}".format(real_value))
            log.info("except_value ==> {}".format(except_value))
            assert False

    @classmethod
    def assert_real_in_except(cls, real_value, except_value):
        if real_value not in except_value:
            log.info("real_value ==> {}".format(real_value))
            log.info("except_value ==> {}".format(except_value))
            assert False

    @classmethod
    def assert_real_not_in_except(cls, real_value, except_value):
        if real_value in except_value:
            log.info("real_value ==> {}".format(real_value))
            log.info("except_value ==> {}".format(except_value))
            assert False

    @classmethod
    def assert_real_include_except(cls, real_value, except_value):
        if except_value not in real_value:
            log.info("real_value ==> {}".format(real_value))
            log.info("except_value ==> {}".format(except_value))
            assert False

    @classmethod
    def assert_real_not_include_except(cls, real_value, except_value):
        if except_value in real_value:
            log.info("real_value ==> {}".format(real_value))
            log.info("except_value ==> {}".format(real_value))
