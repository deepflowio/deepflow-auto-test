#--coding:utf-8--

import logging
import requests
import json
from common import common_config

deployment_path = '/apis/apps/v1/namespaces/default/deployments'


def k8s_create_deployment(deployment_name, vtaps_mgt_ip, k8s_api_port):
    result = False
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    header = {'content-type': 'application/json'}
    url_path = url + deployment_path
    data = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "{}".format(deployment_name),
            "labels": {
                "app": "autodev-deployment-ldq"
            }
        },
        "spec": {
            "selector": {
                "matchLabels": {
                    "app": "{}".format(deployment_name)
                }
            },
            "replicas": 1,
            "template": {
                "metadata": {
                    "labels": {
                        "app": "{}".format(deployment_name)
                    }
                },
                "spec": {
                    "containers": [{
                        "name": "{}".format(deployment_name),
                        "image": "centos:7.5.1804",
                        "command": ["/usr/sbin/init", "-c", "--"],
                        "ports": [{
                            "containerPort": 3302,
                            "protocol": "TCP"
                        }]
                    }]
                }
            }
        }
    }
    data = json.dumps(data)
    res = requests.post(url=url_path, headers=header, data=data)
    try:
        if res.status_code == 201:
            result = True
            print(
                'create new deployment pod successfully in kubernetes, name is {}'
                .format(deployment_name)
            )
            logging.info(
                'create new deployment pod successfully in kubernetes, name is {}'
                .format(deployment_name)
            )
    except Exception as err:
        logging.error(
            'create new deployment pod failed in kubernetes, log info is {}'
            .format(err)
        )
    return result


def k8s_delete_deployment(deployment_name, vtaps_mgt_ip, k8s_api_port):
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    del_url = url + deployment_path + '/{}'.format(deployment_name)
    res = requests.delete(url=del_url)
    try:
        if res.status_code == 200:
            print('delete new deployment successfully in kubernetes')
            logging.info('delete new deployment successfully in kubernetes')
    except Exception as err:
        logging.error(
            'delete new deployment failed in kubernetes, log info is {}'
            .format(err)
        )

