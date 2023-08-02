#--coding:utf-8--

import time
import paramiko
import requests
import logging
import re
from common import common_config
from common import url
from common.ssh import ssh_pool


def k8s_enable_proxy(
    vtaps_mgt_ip, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    '''enable poroxy in kubernetes; parameter
    vtap_mgt_ip; required, vtap ip addr
    '''
    proxy_port = 8001
    ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
    chan = ssh.invoke_shell()
    chan.send(
        '''nohup kubectl proxy --address='0.0.0.0'  --accept-hosts='^*$' & \n'''
    )
    time.sleep(1)
    return proxy_port


def get_mysql_extport(
    df_mgt_ip, username=common_config.ssh_username_default,
    password=common_config.ssh_password_default,
    ssh_port=common_config.ssh_port_default
):
    ssh = ssh_pool.get(df_mgt_ip, ssh_port, username, password)
    stdin, stdout, stderr = ssh.exec_command(
        'kubectl get svc -n deepflow|grep mysql'
    )
    logs = stdout.readlines()[0]
    mysql_ext_port = re.findall(r"\d.*:(\d.*)\/TCP", logs)[0]
    return int(mysql_ext_port)


def get_domains_lcuuid_by_ip(
    vtaps_mgt_ip, df_mgt_ip, df_server_controller_port
):
    '''get domains lcuuid on DF by API, Parameter description.
    df_mgt_ip; required filed, Ip of the deepflow
    '''
    domain_lcuuid = ''
    get_domain_url = url.protocol + df_mgt_ip + ':' + str(
        df_server_controller_port
    ) + url.domains_api_prefix
    try:
        res = requests.get(url=get_domain_url)
        json_str = res.json()['DATA']
        for i in json_str:
            if i['VTAP_CTRL_IP'] == vtaps_mgt_ip:
                domain_lcuuid = i['LCUUID']
                break
    except Exception as err:
        logging.error(err)
    return domain_lcuuid


def load_centos_images(
    vtaps_mgt_ip, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
    stdin, stdout, stderr = ssh.exec_command(
        '''cat /dev/null > /etc/resolv.conf &&\
                                                echo "nameserver 10.1.0.1" > /etc/resolv.conf &&\
                                                curl -O http://nexus.yunshan.net/repository/tools/automation/images/centos7.tar &&\
                                                nerdctl load -i centos7.tar'''
    )
    logs = stdout.readlines()[0]
    if 'done' in logs:
        logging.info('load centos images successfully')
    else:
        logging.error('load centos images failed')
