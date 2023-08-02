#--coding:utf-8--

import requests
import json
import logging

ingress_path = '/apis/networking.k8s.io/v1/namespaces/default/ingresses'


def k8s_create_ingress(ingress_name, vtaps_mgt_ip, k8s_api_port):
    result = False
    header = {'content-type': 'application/json'}
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    ingress_data = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": "{}".format(ingress_name),
            "annotations": {
                "kubernetes.io/ingress.class": "nginx"
            }
        },
        "spec": {
            "rules": [{
                "host": "autodev.deepflow.com",
                "http": {
                    "paths": [{
                        "path": "/",
                        "pathType": "Prefix",
                        "backend": {
                            "service": {
                                "name": "{}".format(ingress_name),
                                "port": {
                                    "number": 80
                                }
                            }
                        }
                    }]
                }
            }]
        }
    }
    ingress_data = json.dumps(ingress_data)
    ingress_host_name = json.loads(ingress_data)['spec']['rules'][0]['host']
    res = requests.post(
        url=url + ingress_path, headers=header, data=ingress_data
    )
    try:
        if res.status_code == 201:
            result = True
            logging.info(
                'create new ingress successfully in kubernetes, name is {}'
                .format(ingress_name)
            )
    except Exception as err:
        logging.error(
            'create new ingress failed in kubernetes, log info is {}'
            .format(err)
        )
        assert False
    return result, ingress_host_name


def delete_k8s_ingress(ingress_name, vtaps_mgt_ip, k8s_api_port):
    result = False
    url = 'http://{}:{}'.format(vtaps_mgt_ip, k8s_api_port)
    res = requests.delete(url=url + ingress_path + '/{}'.format(ingress_name))
    try:
        if res.status_code == 200:
            result = True
            logging.info(
                'delete services successfully in kubernetes, name is {}'
                .format(ingress_name)
            )
    except Exception as err:
        logging.error(
            'delete services failed in kubernetes, log info is {}'.format(err)
        )
        assert False
    return result

