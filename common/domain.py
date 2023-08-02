# --coding:utf-8--
"""
author: danqing
date: 2022-12-15
desc: deepflow CE edition domain API
"""

import requests
import json
import paramiko
import time
import os
from common import common_config
from common import utils as common_utils
from common.ssh import ssh_pool
from common import logger

log = logger.getLogger()


class Domain(object):

    def __init__(self, df_mgt_ip, df_server_controller_port):
        self.df_mgt_ip = df_mgt_ip
        self.df_server_controller_port = df_server_controller_port
        self.domain_url_for_modify = 'http://{}:{}/v1/domains/'.format(
            self.df_mgt_ip, self.df_server_controller_port
        )
        self.domain_url_for_get = 'http://{}:{}/v2/domains/'.format(
            self.df_mgt_ip, self.df_server_controller_port
        )
        self.vpc_url_for_get = 'http://{}:{}/v2/vpcs/'.format(
            self.df_mgt_ip, self.df_server_controller_port
        )
        self.subdomain_url_for_get = 'http://{}:{}/v2/sub-domains/'.format(
            self.df_mgt_ip, self.df_server_controller_port
        )
        self.aliyun_domain_name = 'aliyun'
        self.aliyun_domain_lcuuid = None
        self.domain_lcuuid = None
        self.vpc_lcuuid = None
        self.subdomain_cluster_id = None
        self.subdomain_agent_sync_time = 900
        self.tencent_domain_name = 'tencent'
        self.domain_agent_sync_name = 'agent_sync'
        self.subdomain_agent_sync_name = 'subdomain_agent_sync'
        self.domain_type = {'aliyun': 9, 'agent_sync': 23}

    def get_domain_info_list(self):
        res = requests.get(url=self.domain_url_for_get)
        if res.status_code == 200:
            log.info('get_domain_list::get domain list successfully')
            domain_info_list = res.json()['DATA']
        else:
            assert False
        return domain_info_list

    def domain_platform_is_exist(self, expect_domain_type=None):
        if expect_domain_type is None:
            assert False
        is_exist = False
        domain_info = self.get_domain_info_list()
        for item in domain_info:
            if item['TYPE'] == self.domain_type[expect_domain_type]:
                log.info(
                    'domain_platform_is_exist::expect_domain_type in domain list, expect_domain_type is {}'
                    .format(self.domain_type[expect_domain_type])
                )
                is_exist = True
                break
        return is_exist

    def add_domain_agent_sync(self):
        data = {
            "TYPE": 23,
            "NAME": "{}".format(self.domain_agent_sync_name),
            "ICON_ID": -3,
            "CONFIG": {
                "region_uuid": "ffffffff-ffff-ffff-ffff-ffffffffffff",
                "controller_ip": "{}".format(self.df_mgt_ip)
            }
        }
        header = {'content-type': 'application/json'}
        data = json.dumps(data)
        res = requests.post(
            url=self.domain_url_for_modify, data=data, headers=header
        )
        if res.status_code == 200:
            log.info(
                'domain_add_agent_sync::add agent_sync successfully, agent sync name is {}'
                .format(self.domain_agent_sync_name)
            )
        else:
            resp = res.json()
            log.warning(
                f"domain_add_agent_sync::add agent_sync failed, response: {resp}"
            )
            if "exist" in resp["DESCRIPTION"]:
                return
            else:
                assert False

    def get_domain_lcuuid_by_hostname(self, vtap_hostname=None):
        if vtap_hostname is None:
            assert False
        domain_info = requests.get(url=self.domain_url_for_get)
        if domain_info.status_code == 200:
            for i in domain_info.json()['DATA']:
                if vtap_hostname in i['CONTROLLER_NAME']:
                    self.domain_lcuuid = i['LCUUID']
                    log.info(
                        'get_domain_lcuuid_by_hostname::domain lcuuid:{},hostname:{}'
                        .format(self.domain_lcuuid, vtap_hostname)
                    )
                    break
        else:
            assert False
        return self.domain_lcuuid

    def get_domain_lcuuid_by_name(self, domain_name=None):
        if domain_name is None:
            assert False
        domain_info = requests.get(url=self.domain_url_for_get)
        if domain_info.status_code == 200:
            log.info(f'get_domain_lcuuid_by_name: {domain_info.json()}')
            for i in domain_info.json()['DATA']:
                if i['NAME'] == domain_name:
                    self.domain_lcuuid = i['LCUUID']
                    log.info(
                        'get_domain_lcuuid_by_name::domain lcuuid:{},domain name:{}'
                        .format(self.domain_lcuuid, domain_name)
                    )
                    break
        else:
            assert False
        return self.domain_lcuuid

    def delete_domain_by_lcuuid(self, domain_lcuuid=None):
        if domain_lcuuid is None:
            assert False
        delete_domain_lcuuid_status = False
        res = requests.delete(
            url=self.domain_url_for_modify + '{}/'.format(domain_lcuuid)
        )
        if res.status_code == 200:
            log.info(
                'delete_domain_by_lcuuid::delete domain by lcuuid successfully, lcuuid:{}'
                .format(domain_lcuuid)
            )
            delete_domain_lcuuid_status = True
        else:
            assert False
        return delete_domain_lcuuid_status

    def domain_add_ext_dns_server(self):
        ssh = ssh_pool.get(
            self.df_mgt_ip, common_config.ssh_port_default,
            common_config.ssh_username_default,
            common_config.ssh_password_default
        )
        stdin, stdout, stderr = ssh.exec_command(
            '''kubectl get deployment deepflow-server -n deepflow -o yaml > df-server-dns.yaml && \
                                                        sed -i "/dnsPolicy: ClusterFirst/a\      dnsConfig:" df-server-dns.yaml && \
                                                        sed -i "/      dnsConfig:/a\         nameservers:" df-server-dns.yaml && \
                                                        sed -i "/         nameservers:/a\         - {}" df-server-dns.yaml &&\
                                                        kubectl apply -f df-server-dns.yaml'''
            .format(common_config.ext_dns_server)
        )
        logs = stdout.readlines()
        if logs is not None:
            for i in range(20):
                stdin, stdout, stderr = ssh.exec_command(
                    'kubectl get pods -n deepflow|grep deepflow-server'
                )
                deepflow_server_status = ''.join(stdout.readlines()[0])
                if 'Running' in deepflow_server_status:
                    log.info(
                        'domain_add_ext_dns_server::deepflow server status is running now, wait 10s'
                    )
                    #Wait for deepflow-server's working status to change to normal
                    time.sleep(10)
                    log.info(
                        'domain_add_ext_dns_server::deepflow server status is normal'
                    )
                    break
                else:
                    log.info(
                        'domain_add_ext_dns_server::deepflow server is pending now, wait for 10s'
                    )
                    time.sleep(5)

    def add_domain_aliyun(self):
        add_aliyun_status = False
        header = {'content-type': 'application/json'}
        data = {
            "TYPE": 9,
            "NAME": "{}".format(self.aliyun_domain_name),
            "ICON_ID": 8,
            "CONFIG": {
                "region_uuid": "ffffffff-ffff-ffff-ffff-ffffffffffff",
                "controller_ip": "{}".format(self.df_mgt_ip),
                "secret_id": "{}".format(os.getenv('ALICLOUD_ACCESS_KEY')),
                "secret_key": "{}".format(os.getenv('ALICLOUD_SECRET_KEY')),
                "include_regions": "华北2（北京）",
                "exclude_regions": "华南3（广州）,欧洲中部 1 (法兰克福),中东东部 1 (迪拜),英国 (伦敦),美国西部 1 (硅谷),美国东部 1 (弗吉尼亚),亚太南部 1 (孟买),亚太东南 3 (吉隆坡),亚太东南 5 (雅加达),亚太东南 2 (悉尼),亚太东南 1 (新加坡),亚太东北 1 (东京),香港,华北6（乌兰察布）,华东5（南京-本地地域）",
                "k8s_confs": ""
            }
        }
        data = json.dumps(data)
        res = requests.post(
            url=self.domain_url_for_modify, headers=header, data=data
        )
        if res.status_code == 200:
            log.info(
                'domain_add_aliyun::add aliyun cloud successfully, domain name:{}'
                .format(self.aliyun_domain_name)
            )
            add_aliyun_status = True
        else:
            assert False
        return add_aliyun_status

    @common_utils.time_out(900)
    def domain_check_aliyun_status(self):
        check_aliyun_status = False
        while True:
            res = requests.get(url=self.domain_url_for_get)
            if res.status_code == 200:
                res_json = res.json()['DATA']
                for i in res_json:
                    if i['NAME'] == self.aliyun_domain_name and i[
                        'TYPE'] == 9 and i['STATE'] == 1 and i[
                            'ENABLED'] == 1 and len(i['SYNCED_AT']) > 0:
                        log.info(
                            'domain_check_aliyun_status::aliyun cloud platform status is normal'
                        )
                        check_aliyun_status = True
                        break
            if check_aliyun_status:
                break
            else:
                log.info(
                    'domain_check_aliyun_status::wait for aliyun cloud sync, about 10s'
                )
                time.sleep(10)
        return check_aliyun_status

    @common_utils.time_out(900)
    def domain_check_agent_sync_status(self):
        check_agent_sync_status = False
        while True:
            res = requests.get(url=self.domain_url_for_get)
            if res.status_code == 200:
                res_json = res.json()['DATA']
                log.debug(res_json)
                for i in res_json:
                    if i['NAME'] == self.domain_agent_sync_name and i[
                        'TYPE'] == 23 and i['STATE'] == 1 and i[
                            'ENABLED'] == 1 and len(i['SYNCED_AT']) > 0:
                        log.info(
                            'domain_check_agent_sync_status::agent sync cloud platform status is normal'
                        )
                        check_agent_sync_status = True
                        break
            if check_agent_sync_status:
                break
            else:
                log.info(
                    'domain_check_agent_sync_status::wait for agent sync cloud sync, about 10s'
                )
                time.sleep(10)
        return check_agent_sync_status

    def get_vpc_info_list(self):
        res = requests.get(url=self.vpc_url_for_get)
        if res.status_code == 200:
            log.info('get_vpc_info_list::get vpc list successfully')
            vpc_info_list = res.json()['DATA']
        else:
            assert False
        return vpc_info_list

    def get_vpc_lcuuid_by_ip(self, vtap_mgt_ip):
        get_vpc_lcuuid_status = False
        vpc_info_list = None
        for k in range(self.subdomain_agent_sync_time // 10):
            vpc_info_list = self.get_vpc_info_list()
            for i in vpc_info_list:
                if vtap_mgt_ip in i['NAME']:
                    self.vpc_lcuuid = i['LCUUID']
                    log.info(
                        'get_vpc_lcuuid_by_ip::get vpc lcuuid by ip, lcuuid:{}'
                        .format(self.vpc_lcuuid)
                    )
                    get_vpc_lcuuid_status = True
                    break
            else:
                log.info(
                    'get_vpc_lcuuid_by_ip::vpc info is being synchronized, wait 10s'
                )
            if get_vpc_lcuuid_status:
                break
            time.sleep(10)
        if not get_vpc_lcuuid_status:
            log.error(
                f"get_vpc_lcuuid_by_ip error:: vpc_info_list:{vpc_info_list} vtap_mgt_ip: {vtap_mgt_ip}"
            )
        return self.vpc_lcuuid

    def get_subdomain_info_list(self):
        res = requests.get(url=self.subdomain_url_for_get)
        if res.status_code == 200:
            log.info(
                'get_subdomain_info_list::get subdomain list successfully'
            )
            subdomain_info_list = res.json()['DATA']
        else:
            assert False
        return subdomain_info_list

    def add_subdomain_agent_sync(self, vpc_lcuuid, domain_lcuuid):
        data = {
            "NAME": "{}".format(self.subdomain_agent_sync_name),
            "CONFIG": {
                "vpc_uuid": "{}".format(vpc_lcuuid),
                "pod_net_ipv4_cidr_max_mask": 16,
                "pod_net_ipv6_cidr_max_mask": 64,
                "port_name_regex": "^(cni|flannel|cali|vxlan.calico|tunl|en[ospx]|eth)"
            },
            "DOMAIN": "{}".format(domain_lcuuid)
        }
        data = json.dumps(data)
        header = {'content-type': 'application/json'}
        res = requests.post(
            url=self.subdomain_url_for_get, data=data, headers=header
        )
        if res.status_code == 200:
            log.info(
                'add_subdomain_agent_sync::add subdomain for agent sync successfully, vpc lcuuid:{}, domain lcuuid:{}'
                .format(vpc_lcuuid, domain_lcuuid)
            )
        else:
            assert False

    def get_subdomain_cluster_id_by_name(self):
        subdomain_info_list = self.get_subdomain_info_list()
        for i in subdomain_info_list:
            if i['NAME'] == self.subdomain_agent_sync_name:
                self.subdomain_cluster_id = i['CLUSTER_ID']
                log.info(
                    'get_subdomain_cluster_id_by_name::get cluster id in subdomain successfully, cluster id:{}'
                    .format(self.subdomain_cluster_id)
                )
                break
            else:
                assert False
        return self.subdomain_cluster_id

    def delete_subdomain_by_lcuuid(self, domain_lcuuid):
        delete_subdomain_url = self.subdomain_url_for_get + '{}/'.format(
            domain_lcuuid
        )
        res = requests.delete(url=delete_subdomain_url)
        if res.status_code == 200:
            log.info(
                'delete_subdomain_by_lcuuid::delete subdomain successfully, domain lcuuid:{}'
                .format(domain_lcuuid)
            )
        else:
            assert False

    def add_deepflow_ctl_cmd_latest(self):
        ssh = ssh_pool.get(
            self.df_mgt_ip, common_config.ssh_port_default,
            common_config.ssh_username_default,
            common_config.ssh_password_default
        )
        cmd_list = [
            "curl -o /usr/bin/deepflow-ctl https://deepflow-ce.oss-cn-beijing.aliyuncs.com/bin/ctl/latest/linux/$(arch | sed 's|x86_64|amd64|' | sed 's|aarch64|arm64|')/deepflow-ctl",
            "chmod a+x /usr/bin/deepflow-ctl",
        ]
        for cmd in cmd_list:
            ssh.exec_command(cmd)
            time.sleep(1)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        cmd_logs = stdout.readlines()
        if len(cmd_logs) == 0:
            log.info(
                'add_deepflow_ctl_cmd_latest::add deepflow-ctl cmd successfully'
            )
        else:
            assert False
