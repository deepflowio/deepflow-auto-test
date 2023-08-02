#--coding:utf-8--

import os
import time

import paramiko
import requests
import json
import logging
from common import common_config
from common.ssh import ssh_pool

namespace_path = '/api/v1/namespaces'


def modify_database_max_connect_error(
    df_mgt_ip, username=common_config.ssh_username_default,
    password=common_config.ssh_password_default,
    ssh_port=common_config.ssh_port_default
):
    ssh = ssh_pool.get(df_mgt_ip, ssh_port, username, password)
    stdin, stdout, stderr = ssh.exec_command(
        'kubectl get pods -n deepflow|grep mysql'
    )
    mysql_pod_name = stdout.readlines()[0].split(' ')[0]
    chan = ssh.invoke_shell()
    chan.send(
        '''kubectl exec -ti {} -n deepflow bash\n
                 mysql -u root -pdeepflow\n
                 flush hosts;\n
                 set global max_connect_errors = 1000;\n'''
        .format(mysql_pod_name)
    )
    time.sleep(1)


def create_k8s_namespace(namespace_name, vtaps_mgt_ip, k8s_api_port):
    result = False
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    header = {'content-type': 'application/json'}
    data = {
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {
            'name': '{}'.format(namespace_name),
            'labels': {
                'name': '{}'.format(namespace_name)
            }
        }
    }
    data = json.dumps(data)
    res = requests.post(url=url + namespace_path, headers=header, data=data)
    try:
        if res.status_code == 200:
            result = True
            logging.info(
                'create new namespaces successfully in kubernetes, name is {}'
                .format(namespace_name)
            )
    except Exception as err:
        logging.error(
            'create new namespaces failed in kubernetes, log info is {}'
            .format(err)
        )
        assert False
    return result


def delete_k8s_namespaces(namespace_name, vtaps_mgt_ip, k8s_api_port):
    result = False
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    res = requests.delete(
        url=url + namespace_path + '/{}'.format(namespace_name)
    )
    try:
        if res.status_code == 200:
            result = True
            logging.info(
                'delete namespaces successfully in kubernetes, name is {}'
                .format(namespace_name)
            )
    except Exception as err:
        logging.error(
            'delete namespaces failed in kubernetes, log info is {}'
            .format(err)
        )
        assert False
    return result


def get_k8s_namespaces(vtaps_mgt_ip, k8s_api_port):
    result = ''
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    res = requests.get(url=url + namespace_path)
    try:
        if res.status_code == 200:
            logging.info('get namespaces list successfully in kubernetes')
            result = res.json()
    except Exception as err:
        logging.error(
            'get namepaces list failed in kubernetes, log info is {}'
            .format(err)
        )
    return result

