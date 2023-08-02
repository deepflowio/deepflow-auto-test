#--coding:utf-8--

import requests
import json
import logging
from common import common_config

svc_path = '/api/v1/namespaces/default/services'

data = {
    "apiVersion": "v1",
    "kind": "Service",
    "metadata": {
        "name": "autodev-service-test",
        "labels": {
            "app": "autodev-service-test"
        }
    },
    "spec": {
        "ports": [{
            "port": 3302,
            "targetPort": 3302
        }],
        "selector": {
            "app": "autodev-deployment-test"
        }
    }
}


def k8s_create_services(vtaps_mgt_ip, k8s_api_port, svc_name, pod_name):
    result = False
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    header = {'content-type': 'application/json'}
    data = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": "{}".format(svc_name),
            "labels": {
                "app": "{}".format(svc_name)
            }
        },
        "spec": {
            "ports": [{
                "port": 3302,
                "targetPort": 3302
            }],
            "selector": {
                "app": "{}".format(pod_name)
            }
        }
    }
    data = json.dumps(data)
    res = requests.post(url=url + svc_path, headers=header, data=data)
    try:
        if res.status_code == 201:
            result = True
            print(
                'create new services successfully in kubernetes, name is autodev-service-test'
            )
            logging.info(
                'create new services successfully in kubernetes, name is autodev-service-test'
            )
    except Exception as err:
        logging.error(
            'create new services failed in kubernetes, log info is {}'
            .format(err)
        )
        assert False
    return result


def k8s_delete_services(vtaps_mgt_ip, k8s_api_port, svc_name):
    result = False
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    res = requests.delete(url=url + svc_path + '/{}'.format(svc_name))
    try:
        if res.status_code == 200:
            result = True
            print(
                'delete services successfully in kubernetes, name is {}'
                .format(svc_name)
            )
            logging.info(
                'delete services successfully in kubernetes, name is {}'
                .format(svc_name)
            )
    except Exception as err:
        logging.error(
            'delete services failed in kubernetes, log info is {}'.format(err)
        )
        assert False
    return result


def get_k8s_services_list(vtaps_mgt_ip, k8s_api_port):
    result = ''
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    res = requests.get(url=url + svc_path)
    try:
        if res.status_code == 200:
            logging.info('get services list successfully in kubernetes')
            result = res.json()
    except Exception as err:
        logging.error(
            'get services list failed in kubernetes, log info is {}'
            .format(err)
        )
    return result

