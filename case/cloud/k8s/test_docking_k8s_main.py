#--coding:utf-8--

import logging
import time
from common.utils import step as allure_step
import allure
import pytest
import pymysql

from common import common_config
from common import aliyun_sdk
from common.ssh import ssh_pool
from common.const import CASE_TYPE_MONOPOLIZE
from case.cloud.k8s import utils as docking_utils
from case.cloud.k8s import k8s_namespaces
from case.cloud.k8s import k8s_ingress
from case.cloud.k8s import k8s_deployment
from case.cloud.k8s import k8s_services
from case.cloud.k8s import k8s_replicaset
from case.cloud.k8s import k8s_nodes
from case.base import BaseCase

k8s_vm_name = 'automation-resource-k8s'
k8s_namespaces_name = 'automation-deepflow-namespace-testa'
k8s_ingress_name = 'autodev-ingress-deepflow'
k8s_svc_name = 'automation-deepflow-svc'
k8s_deployment_pod_name = 'autodev-deployment-pod'
k8s_cluster_name = 'automation-deepflow-cluster'
k8s_node_vm_name = 'automation-deepflow-node-node'

loop_counts = 60


class TestDockingK8s(BaseCase):

    k8s_vm_name = None
    k8s_node_vm_name = None
    vm_private_ip = None
    k8s_api_port = None
    mysql_ext_port = None
    domain_lcuuid = None
    mysql_conn = None
    CASE_TYPE = CASE_TYPE_MONOPOLIZE

    def modify_auto_increment_increment(
        self, ssh_port=common_config.ssh_port_default,
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default
    ):

        try:
            conn = self.connect_mysql()
            with conn.cursor() as cur:
                sql = "set global auto_increment_increment = 2;"
                logging.info(f"Exec Sql: {sql}")
                cur.execute(sql)
                conn.commit()
            # modify the k8s configmap resource
            cmds = [
                "kubectl get cm -n deepflow deepflow -o yaml > deepflow-cm.yaml",
                "sed -i '/mysql:/a \ \ \ \ \ \ \ \ auto_increment_increment: 2' deepflow-cm.yaml",
                "kubectl apply -f deepflow-cm.yaml"
            ]
            cmd = "&&".join(cmds)
            ssh = ssh_pool.get(
                self.df_ce_info["mgt_ip"], ssh_port, username, password
            )
            stdin, stdout, stderr = ssh.exec_command(cmd)
            err = stderr.readlines()
            if err:
                logging.error(f"edit server configmap error: {err}")
        except Exception as e:
            logging.error(f"edit server configmap exception: {e}")
            assert False

    @classmethod
    def _setup_class(cls):
        cls.k8s_vm_name = f"{k8s_vm_name}-{common_config.pytest_uuid}"
        cls.k8s_node_vm_name = f"{k8s_node_vm_name}-{common_config.pytest_uuid}"
        cls.ingress_hostname = ['']
        with allure_step(
            'step1: create vm by aliyun SDK and deployed deepflow-agent'
        ):
            logging.info(
                'TestDockingK8s create vm by aliyun SDK and deployed deepflow-agent'
            )
            cls.vm_private_ip = aliyun_sdk.create_instances_by_deploy(
                uuid=common_config.pytest_uuid,
                instance_names=[cls.k8s_vm_name],
                image_id=common_config.ali_image_centos7_deepflow_id,
                instance_type=common_config.ali_instance_type_c1m2_large
            )
            # deploy k8s
            cls.common_utils.vtaps_install_k8s(
                cls.vm_private_ip[cls.k8s_vm_name]
            )
            # deploy deepflow-agent
            cls.common_utils.k8s_vtaps_install_deepflow_agent(
                cls.vm_private_ip[cls.k8s_vm_name]
            )
            try:
                res = False
                domain_list = None
                for i in range(loop_counts):
                    logging.info(
                        f'Wait for kubernetes platform docking, about {10*i}s'
                    )
                    time.sleep(10)
                    domain_list = cls.common_utils.get_domains_list()
                    for k in range(len(domain_list)):
                        if domain_list[k]['VTAP_CTRL_IP'] == cls.vm_private_ip[
                            cls.k8s_vm_name
                        ] and domain_list[k]['SYNCED_AT'] is not None:
                            res = True
                            break
                    if res == True:
                        cls.k8s_api_port = docking_utils.k8s_enable_proxy(
                            vtaps_mgt_ip=cls.vm_private_ip[cls.k8s_vm_name]
                        )
                        cls.mysql_ext_port = docking_utils.get_mysql_extport(
                            df_mgt_ip=cls.df_ce_info["mgt_ip"]
                        )
                        cls.domain_lcuuid = docking_utils.get_domains_lcuuid_by_ip(
                            cls.vm_private_ip[cls.k8s_vm_name],
                            cls.df_ce_info["mgt_ip"],
                            cls.df_ce_info["server_controller_port"]
                        )
                        k8s_namespaces.modify_database_max_connect_error(
                            df_mgt_ip=cls.df_ce_info["mgt_ip"]
                        )
                        docking_utils.load_centos_images(
                            vtaps_mgt_ip=cls.vm_private_ip[cls.k8s_vm_name]
                        )
                        logging.info(
                            'kubernetes platform docking successfully'
                        )
                        break
                if res is False:
                    logging.error(
                        f"kubernetes docking failed, domain_list: {domain_list}"
                    )
                    assert False
            except Exception as err:
                logging.error(
                    'kubernetes docking failed, log info is {}'.format(err)
                )
                assert False

    @classmethod
    def _teardown_class(cls):
        with allure_step(
            'step n: delete vm by aliyun SDK and delete k8s platform in deepflow'
        ):
            aliyun_sdk.release_instance_by_delpoy(
                uuid=common_config.pytest_uuid,
                instance_names=[cls.k8s_vm_name]
            )
            cls.common_utils.del_k8s_domains(cls.domain_lcuuid)

    def _delete_resource(self):
        k8s_deployment.k8s_delete_deployment(
            deployment_name=k8s_deployment_pod_name,
            vtaps_mgt_ip=self.vm_private_ip[self.k8s_vm_name],
            k8s_api_port=self.k8s_api_port
        )
        time.sleep(1)
        k8s_services.k8s_delete_services(
            svc_name=k8s_svc_name,
            vtaps_mgt_ip=self.vm_private_ip[self.k8s_vm_name],
            k8s_api_port=self.k8s_api_port
        )
        k8s_ingress.delete_k8s_ingress(
            ingress_name=k8s_ingress_name,
            vtaps_mgt_ip=self.vm_private_ip[self.k8s_vm_name],
            k8s_api_port=self.k8s_api_port
        )
        k8s_namespaces.delete_k8s_namespaces(
            namespace_name=k8s_namespaces_name,
            vtaps_mgt_ip=self.vm_private_ip[self.k8s_vm_name],
            k8s_api_port=self.k8s_api_port
        )
        k8s_nodes.k8s_delete_node(
            master_mgt_ip=self.vm_private_ip[self.k8s_vm_name],
            node_mgt_ip=self.k8s_node_vm_private_ip[self.k8s_node_vm_name]
        )
        aliyun_sdk.release_instance_by_delpoy(
            uuid=common_config.pytest_uuid,
            instance_names=[self.k8s_node_vm_name]
        )

    def _create_resource(self):
        k8s_deployment.k8s_create_deployment(
            deployment_name=k8s_deployment_pod_name,
            vtaps_mgt_ip=self.vm_private_ip[self.k8s_vm_name],
            k8s_api_port=self.k8s_api_port
        )
        time.sleep(2)
        k8s_services.k8s_create_services(
            vtaps_mgt_ip=self.vm_private_ip[self.k8s_vm_name],
            k8s_api_port=self.k8s_api_port, svc_name=k8s_svc_name,
            pod_name=k8s_deployment_pod_name
        )
        # create a ingress for k8s
        _, self.ingress_hostname[0] = k8s_ingress.k8s_create_ingress(
            ingress_name=k8s_ingress_name,
            vtaps_mgt_ip=self.vm_private_ip[self.k8s_vm_name],
            k8s_api_port=self.k8s_api_port
        )
        # create a namespace for k8s
        k8s_namespaces.create_k8s_namespace(
            namespace_name=k8s_namespaces_name,
            vtaps_mgt_ip=self.vm_private_ip[self.k8s_vm_name],
            k8s_api_port=self.k8s_api_port
        )
        # create a node for k8s
        self.k8s_node_vm_private_ip = aliyun_sdk.create_instances_by_deploy(
            uuid=common_config.pytest_uuid,
            instance_names=[self.k8s_node_vm_name],
            image_id=common_config.ali_image_centos7_deepflow_id,
            instance_type=common_config.ali_instance_type_c1m2_large
        )
        k8s_nodes.k8s_add_node(
            self.vm_private_ip[self.k8s_vm_name],
            self.k8s_node_vm_private_ip[self.k8s_node_vm_name]
        )

    def _docking_k8s_add_cluster(self):
        with allure_step('step16: check new cluster in deepflow'):
            try:
                res = False
                for i in range(loop_counts):
                    domain_list = self.common_utils.get_domains_list()
                    for k in range(len(domain_list)):
                        if domain_list[k][
                            'VTAP_CTRL_IP'] == self.k8s_cluster_private_ip[
                                k8s_cluster_name] and domain_list[k][
                                    'SYNCED_AT'] is not None:
                            res = True
                            break
                    if res == True:
                        self.cluster_name = self.common_utils.get_domain_name_by_vtap_ip(
                            self.k8s_cluster_private_ip[k8s_cluster_name]
                        )
                        break
                    logging.info(
                        'Wait for kubernetes platform docking, about 10s'
                    )
                    time.sleep(10)
            except Exception as err:
                logging.error(err)
            for i in range(loop_counts):
                if k8s_nodes.check_cluster_in_deepflow(
                    cluster_name=self.cluster_name, includes='yes',
                    conn=self.connect_mysql()
                ) == True:
                    logging.info('new cluster in deepflow')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False

    def _docking_k8s_del_cluster(self):
        with allure_step('step17: check cluster resource after deleted'):
            for i in range(loop_counts):
                if k8s_nodes.check_cluster_in_deepflow(
                    cluster_name=self.cluster_name, includes=False,
                    conn=self.connect_mysql()
                ) == True:
                    logging.info('new cluster has been deleted in deepflow')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False

    @classmethod
    def connect_mysql(cls):
        if cls.mysql_conn:
            cls.mysql_conn.close()
        logging.info(f"Connect Mysql: {cls.df_ce_info['mgt_ip']}")
        cls.mysql_conn = pymysql.connect(
            host=cls.df_ce_info["mgt_ip"],
            user=common_config.deepflow_ce_mysql_user,
            passwd=common_config.deepflow_ce_mysql_passwd,
            db=common_config.deepflow_ce_mysql_db, port=cls.mysql_ext_port
        )
        return cls.mysql_conn

    def check_data_in_deepflow(self, conn, **filters) -> bool:
        '''Check deepflow mysql for specific data, need to add filter field,Return None means have sql error

        database; optional, The name of database,If there is db in the conn, you don't need to add it.
        table; required, The table where the data is located.
        limit; optional, Number of data to query, default is 1.

        filters:
            Support % _ inside value of the variable, for mysql LIKE .
            Supports "is null" or "is not null" inside value of the variable .
        e.g: check_data_in_deepflow(table="my_table",id="1_",limit="2",name="is not null")
        '''
        try:
            database = ""
            table = ""
            limit = "1"
            conditions = []
            select_fild = []
            for key, value in filters.items():
                if key == "database":
                    database = value
                elif key == "table":
                    table = value
                elif key == "limit":
                    limit = value
                else:
                    select_fild.append(key)
                    if "%" in str(value) or "_" in str(value):
                        conditions.append(f"`{key}` LIKE '{value}'")
                    elif "null" in str(value).lower():
                        conditions.append(f"`{key}` {value}")
                    else:
                        conditions.append(f"`{key}` = '{value}'")
            with conn.cursor() as cursor:
                # Constructing SQL query
                if database:
                    sql = f"SELECT * FROM `{database}`.`{table}` WHERE "
                else:
                    sql = f"SELECT * FROM `{table}` WHERE "
                sql += " AND ".join(conditions)
                if not conditions:
                    if database:
                        sql = f"SELECT * FROM `{database}`.`{table}` "
                    else:
                        sql = f"SELECT * FROM `{table}` "
                sql += f" LIMIT {limit}"
                sql = sql.replace("*", " , ".join(select_fild))
                # exec sql
                logging.info(f"Exec Sql: {sql}")
                cursor.execute(sql)
                datas = cursor.fetchall()
                # Returns True if the number of data returned is the same as the limit.
                if int(limit) == len(datas):
                    logging.info(f"Specific data has been queried: {datas}")
                    return True
                logging.info(f'Data does not exist or is incomplete')
                return False
        except pymysql.Error as e:
            logging.error(f"Error: {e}")
            return None

    @allure.suite('cloud test')
    @allure.epic('cloud test - k8s docking')
    @allure.feature('')
    @allure.title('k8s资源学习')
    @allure.description
    @pytest.mark.medium
    def test_docking_k8s(self):
        '''test by querying deepflow's mysql database for reasonable data
        '''
        self.modify_auto_increment_increment()
        self.common_utils.restart_deepflow_server()
        # check the docking results of DF after k8s creates resources
        self._create_resource()
        time.sleep(60)
        with allure_step('step2: check new pod resource'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod",
                    domain=self.domain_lcuuid,
                    name=f"%{k8s_deployment_pod_name}%"
                )
                assert status is not None
                if status:
                    logging.info('new pod in deepflow')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step('step3: check new service resource'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_service",
                    domain=self.domain_lcuuid, name=f"%{k8s_svc_name}%"
                )
                assert status is not None
                if status:
                    logging.info('new service in deepflow')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step('step4: check new rs resource'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_rs",
                    domain=self.domain_lcuuid,
                    name=f"%{k8s_deployment_pod_name}%"
                )
                assert status is not None
                if status:
                    logging.info('new rs in deepflow')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step('step5: check new pod group resource'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_group",
                    domain=self.domain_lcuuid,
                    name=f"%{k8s_deployment_pod_name}%"
                )
                assert status is not None
                if status:
                    logging.info('new pod group in deepflow')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step('step6: check new ingress resource'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_ingress",
                    domain=self.domain_lcuuid, name=f"%{k8s_ingress_name}%"
                )
                assert status is not None
                if status:
                    logging.info('new ingress in deepflow')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step('step7: check new ingress_rule resource'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_ingress_rule",
                    host=self.ingress_hostname[0]
                )
                assert status is not None
                if status:
                    logging.info('new ingress rule in deepflow')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step('step8: check new namespace resource'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_namespace",
                    domain=self.domain_lcuuid, name=f"%{k8s_namespaces_name}%"
                )
                assert status is not None
                if status:
                    logging.info('new namespace in deepflow')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step('step9: check new node resource'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_node",
                    ip=self.k8s_node_vm_private_ip[self.k8s_node_vm_name]
                )
                assert status is not None
                if status:
                    logging.info('new node in deepflow')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        self._delete_resource()
        time.sleep(60)
        # check the docking results of DF after k8s deletes resources
        with allure_step('step10: check pod after deleted pod'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod",
                    domain=self.domain_lcuuid,
                    name=f"%{k8s_deployment_pod_name}%",
                    deleted_at="is not null"
                )
                assert status is not None
                if status:
                    logging.info('the pod in deepflow has been deleted')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step('step11: check service after deleted services'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_service",
                    domain=self.domain_lcuuid, name=f"%{k8s_svc_name}%",
                    deleted_at="is not null"
                )
                assert status is not None
                if status:
                    logging.info('the service in deepflow has been deleted')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step('step12: check rs after deleted rs'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_rs",
                    domain=self.domain_lcuuid,
                    name=f"%{k8s_deployment_pod_name}%",
                    deleted_at="is not null"
                )
                assert status is not None
                if status:
                    logging.info('the rs in deepflow has been deleted')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step('step13: check pod group after deleted pod group'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_group",
                    domain=self.domain_lcuuid,
                    name=f"%{k8s_deployment_pod_name}%",
                    deleted_at="is not null"
                )
                assert status is not None
                if status:
                    logging.info('the pod group in deepflow has been deleted')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step('step14: check ingress after deleted ingress'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_ingress",
                    domain=self.domain_lcuuid, name=f"%{k8s_ingress_name}%",
                    deleted_at="is not null"
                )
                assert status is not None
                if status:
                    logging.info('the ingress in deepflow has been deleted')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step(
            'step15: check ingress_rule after deleted ingress_rule'
        ):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_ingress_rule",
                    host=self.ingress_hostname[0]
                )
                assert status is not None
                if not status:
                    logging.info(
                        'the ingress rule in deepflow has been deleted'
                    )
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step('step16: check namespace after deleted namespace'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_namespace",
                    domain=self.domain_lcuuid, name=f"%{k8s_namespaces_name}%",
                    deleted_at="is not null"
                )
                assert status is not None
                if status:
                    logging.info('the namespace in deepflow has been deleted')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
        with allure_step('step17: check node after deleted node'):
            for i in range(loop_counts):
                status = self.check_data_in_deepflow(
                    self.connect_mysql(), table="pod_node",
                    ip=self.k8s_node_vm_private_ip[self.k8s_node_vm_name],
                    deleted_at="is not null"
                )
                assert status is not None
                if status:
                    logging.info('the node in deepflow has been deleted')
                    break
                logging.info('Waiting for data updates, about 10s')
                time.sleep(10)
            else:
                assert False
