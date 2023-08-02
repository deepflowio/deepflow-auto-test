#--coding:utf-8--

import requests
import json
import logging
from common import common_config

rs_path = '/apis/apps/v1/namespaces/default/replicasets'


def k8s_create_replicaset(rs_name, vtaps_mgt_ip, k8s_api_port):
    result = False
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    header = {'content-type': 'application/json'}
    data = {
        "apiVersion": "apps/v1",
        "kind": "ReplicaSet",
        "metadata": {
            "name": "{}".format(rs_name),
            "namespace": "default"
        },
        "spec": {
            "replicas": 1,
            "selector": {
                "matchLabels": {
                    "app": "{}".format(rs_name)
                }
            },
            "template": {
                "metadata": {
                    "name": "{}".format(rs_name),
                    "labels": {
                        "app": "{}".format(rs_name)
                    }
                },
                "spec": {
                    "containers": [{
                        "name": "{}".format(rs_name),
                        "image": "centos:7.5.1804",
                        "command": ["/usr/sbin/init", "-c", "--"]
                    }]
                }
            }
        }
    }
    data = json.dumps(data)
    res = requests.post(url=url + rs_path, headers=header, data=data)
    try:
        if res.status_code == 200:
            result = True
            logging.info(
                'create new replicasets successfully in kubernetes, name is {}'
                .format(rs_name)
            )
    except Exception as err:
        logging.error(
            'create new replicasets failed in kubernetes, log info is {}'
            .format(err)
        )
        assert False
    return result


def k8s_delete_replicaset(rs_name, vtaps_mgt_ip, k8s_api_port):
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    del_url = url + rs_path + '/{}'.format(rs_name)
    res = requests.delete(url=del_url)
    try:
        if res.status_code == 200:
            logging.info('delete new replicasets successfully in kubernetes')
    except Exception as err:
        logging.error(
            'delete new replicasets failed in kubernetes, log info is {}'
            .format(err)
        )

