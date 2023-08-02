#--coding:utf-8--

import requests
import json
import logging
from common import common_config

pod_path = '/api/v1/namespaces/default/pods'


def create_k8s_pod(pod_name, vtaps_mgt_ip, k8s_api_port):
    result = False
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    header = {'content-type': 'application/json'}
    data = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "{}".format(pod_name),
            "labels": {
                "app": "{}".format(pod_name)
            }
        },
        "spec": {
            "containers": [{
                "name": "{}".format(pod_name),
                "image": "centos:7.5.1804",
                "command": ["/usr/sbin/init", "-c", "--"]
            }]
        }
    }
    data = json.dumps(data)
    res = requests.post(url=url + pod_path, headers=header, data=data)
    try:
        if res.status_code == 200:
            result = True
            logging.info(
                'create new pods successfully in kubernetes, name is {}'
                .format(pod_name)
            )
    except Exception as err:
        logging.error(
            'create new pods failed in kubernetes, log info is {}'.format(err)
        )
        assert False
    return result


def delete_k8s_pod(pod_name, vtaps_mgt_ip, k8s_api_port):
    result = False
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    res = requests.delete(url=url + pod_path + '/{}'.format(pod_name))
    try:
        if res.status_code == 200:
            result = True
            logging.info(
                'delete pod successfully in kubernetes, name is {}'
                .format(pod_name)
            )
    except Exception as err:
        logging.error(
            'delete pod failed in kubernetes, log info is {}'.format(err)
        )
        assert False
    return result


def get_k8s_pod_list(vtaps_mgt_ip, k8s_api_port):
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    result = ''
    res = requests.get(url=url + pod_path)
    try:
        if res.status_code == 200:
            logging.info('get pods list successfully in kubernetes')
            result = res.json()
    except Exception as err:
        logging.error(
            'get pods list failed in kubernetes, log info is {}'.format(err)
        )
    return result

