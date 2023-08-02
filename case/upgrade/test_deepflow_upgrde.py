# coding: utf-8
import time
import datetime
import pytest
from common.utils import step as allure_step
import allure
import os
import uuid
from case.performance_analysis import utils
from case.performance_analysis.analysis_writer import Writer
from case.base import BaseCase
from common import aliyun_sdk
from common import common_config
from common.utils import CommonUtils
from common.ssh import ssh_pool
from deepflow_ce import DeployDeepflowCE
from common.querier_api_utils import QueryApi
from common import logger

log = logger.getLogger()
upgrade_vm_name = 'automation-deepflow-ce-upgrade-test'
loop_num = 15


class TestDeepflowUpgrade(BaseCase):

    deepflow_server_image_tag = None
    deepflow_agent_image_tag = None

    @classmethod
    def setup_class(cls):
        cls.deepflow_server_image_tag = os.environ.get('DF_SERVER_IMAGE_TAG')
        cls.deepflow_agent_image_tag = os.environ.get('DF_AGENT_IMAGE_TAG')

    @classmethod
    def teardown_class(cls):
        pass
        #time.sleep(12000)

    @allure.suite('deepflow upgrade default')
    @allure.epic('deepflow upgrade default test')
    @allure.feature('')
    @allure.title('deepflow upgrade default test')
    @allure.description('deepflow upgrade server and agent to default')
    @pytest.mark.medium
    def test_deepflow_upgrade_default(self):
        case_id = ""
        case_name = "test_deepflow_upgrade_default"
        if self.deepflow_server_image_tag in [
            "v6.1", "v6.2"
        ] or self.deepflow_agent_image_tag in ["v6.1", "v6.2"]:
            pass
        else:
            self.deploy = DeployDeepflowCE()
            self.upgrade_vm_name = f"{upgrade_vm_name}-default-{common_config.pytest_uuid}"
            self.deploy_instance()
            self.deepflow_upgrade()
            self.release_instance()

    @allure.suite('deepflow upgrade v6.1')
    @allure.epic('deepflow upgrade v6.1 test')
    @allure.feature('')
    @allure.title('deepflow upgrade v6.1 test')
    @allure.description('deepflow upgrade server and agent to v6.1')
    @pytest.mark.medium
    def test_deepflow_upgrade_v61(self):
        case_id = ""
        case_name = "test_deepflow_upgrade_v61"
        self.deploy = DeployDeepflowCE()
        self.upgrade_vm_name = f"{upgrade_vm_name}-v61-{common_config.pytest_uuid}"
        self.deploy_instance()
        self.deepflow_upgrade("v6.1", "v6.1")
        self.release_instance()

    @allure.suite('deepflow upgrade v6.2')
    @allure.epic('deepflow upgrade v6.2 test')
    @allure.feature('')
    @allure.title('deepflow upgrade v6.2 test')
    @allure.description('deepflow upgrade server and agent to v6.2')
    @pytest.mark.medium
    def test_deepflow_upgrade_v62(self):
        case_id = ""
        case_name = "test_deepflow_upgrade_v61"
        if self.deepflow_server_image_tag in [
            "v6.1"
        ] or self.deepflow_agent_image_tag in ["v6.1"]:
            pass
        else:
            self.deploy = DeployDeepflowCE()
            self.upgrade_vm_name = f"{upgrade_vm_name}-v62-{common_config.pytest_uuid}"
            self.deploy_instance()
            self.deepflow_upgrade("v6.2", "v6.2")
            self.release_instance()

    def deepflow_upgrade(self, server_tag=None, agent_tag=None):
        with allure_step('step1: install stable deepflow_ce'):
            try:
                time.sleep(60)
                if self.deploy.install_deepflow_ce_latest(
                    self.vm_private_ip[self.upgrade_vm_name], server_tag,
                    agent_tag
                ) == True:
                    pass
            except Exception as e:
                log.error(f"deploy error:{e}")
                assert False
            self.deploy.check_first_data()
            if self.deploy.finished is False:
                log.error("check first data failed!")
                assert False
            self.common_utils.df_server_controller_port = self.deploy.server_controller_port
            self.common_utils.df_server_query_port = self.deploy.server_query_port
            self.deploy.add_aliyun_platform()

        with allure_step('step2: upgrade deepflow_ce'):
            try:
                if not self.deploy.upgrade_deepflow_ce(
                    self.vm_private_ip[self.upgrade_vm_name
                                       ], self.deepflow_server_image_tag,
                    self.deepflow_agent_image_tag
                ):
                    log.error("deploy deepflow ce failed")
                    assert False
            except Exception as e:
                log.error(f"upgrade error:{e}")
                assert False
            now = int(time.time())
            self.deploy.check_first_data(filters=f'where time >= {now}')

        with allure_step('step3: get first data'):
            api = QueryApi(
                self.deploy.server_ip, self.deploy.server_query_port
            )
            count = 0
            first_data_checked = False
            while not first_data_checked and count < 60:
                api.query_sql_api(
                    database="flow_metrics", sql_cmd=
                    f"select pod_node from vtap_flow_port where time >= {now} order by time limit 1",
                    data_precision="1s"
                )
                api.echo_debug_info()
                api.response_status_assert_success()
                if api.response_json["result"]["values"]:
                    first_data_checked = True
                else:
                    time.sleep(10)
                    count += 1
            if not first_data_checked:
                log.error("querier check first data error!")
                assert False

        with allure_step('step4: sync aliyun domain'):
            res = False
            deepflow_hostname_values = self.common_utils.get_deepflow_hostname(
            )
            try:
                for k in range(20):
                    domain_lists = self.common_utils.get_domains_list()
                    for i in domain_lists:
                        if 'k8s' in i['NAME'] and i[
                            'CONTROLLER_IP'] == self.deploy.server_ip and i[
                                'CONTROLLER_NAME'] == deepflow_hostname_values.lower(
                            ) and i['STATE'] == 1 and i[
                                'ENABLED'] == 1 and len(i['SYNCED_AT']) > 0:
                            log.info(
                                'DeepFlow domain sync success，name:{}'.format(
                                    i['NAME']
                                )
                            )
                            res = True
                            break
                        else:
                            time.sleep(30)
                            log.info('wait domain sync，wait 30s')
                    if res == True:
                        break
            except Exception as err:
                log.error('DeepFlow domain sync error: {}'.format(err))
                assert False

        with allure_step('step5: check agent sync'):
            res = False
            deepflow_hostname_values = self.common_utils.get_deepflow_hostname(
            )
            try:
                for k in range(20):
                    vtap_lists = self.common_utils.get_vtaps_list()
                    for i in vtap_lists:
                        if deepflow_hostname_values.lower() in i['NAME'] and i['SYNCED_CONTROLLER_AT'] is not None and i['SYNCED_ANALYZER_AT'] is not None\
                                and i['STATE'] == 1 and i['ENABLE'] == 1 and i['LAUNCH_SERVER'] == self.deploy.server_ip:
                            log.info(
                                'DeepFlow agent sync success，name:{}'.format(
                                    i['NAME']
                                )
                            )
                            res = True
                            break
                        else:
                            time.sleep(30)
                            log.info('wait agent sync，wait 30s')
                    if res == True:
                        break
            except Exception as err:
                log.error('DeepFlow agent sync error: {}'.format(err))
                assert False

    def deploy_instance(self):
        with allure_step('The setup of the class'):
            self.vm_private_ip = aliyun_sdk.create_instances_by_deploy(
                uuid=common_config.pytest_uuid,
                instance_names=[self.upgrade_vm_name],
                image_id=common_config.ali_image_centos7_deepflow_id,
                instance_type=common_config.ali_instance_type_c6_2x_large
            )
            self.common_utils = CommonUtils(
                self.vm_private_ip[self.upgrade_vm_name]
            )
            self.deploy.common_utils = self.common_utils
            self.deploy.server_ip = self.vm_private_ip[self.upgrade_vm_name]
            self.deploy.instance_name = self.upgrade_vm_name
            self.start = time.time()

    def release_instance(self):
        aliyun_sdk.release_instance_by_delpoy(
            uuid=common_config.pytest_uuid,
            instance_names=[self.upgrade_vm_name]
        )
