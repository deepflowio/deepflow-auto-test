# coding: utf-8

import pytest
import allure
import logging
import paramiko
from case.compatibility import utils
from common import aliyun_sdk
from common import common_config
from case.compatibility.base import CompatibilityBaseCase
from common.utils import step as allure_step
from common.ssh import ssh_pool

#  Customized variables
vm_name = 'automation-compatibility-ubuntu14'
loop_num = 90
vtaps_name = 'NAME'
dst_ip = '114.114.114.114'


class TestCompatibilityAgentUbuntu14(CompatibilityBaseCase):

    vm_name = ""

    @classmethod
    def _setup_class(cls):
        cls.vm_name = f"{vm_name}-{common_config.pytest_uuid}"
        with allure_step('step 1: creating ubuntu14 instance by Aliyun SDK'):
            cls.vm_private_ip = aliyun_sdk.create_instances_by_deploy(
                uuid=common_config.pytest_uuid, instance_names=[cls.vm_name],
                image_id=common_config.ali_image_ubuntu14_415_id
            )

    @classmethod
    def _teardown_class(cls):
        with allure_step('step 7: deleting ubuntu14 instance by Aliyun SDK'):
            aliyun_sdk.release_instance_by_delpoy(
                uuid=common_config.pytest_uuid, instance_names=[cls.vm_name]
            )

    @allure.suite('compatibility test')
    @allure.epic('Agent compatibility test')
    @allure.feature('Agent compatibility ubuntu14')
    @allure.title('ubuntu14采集器deepflow-agent类型兼容性测试')
    @allure.description(
        'ubuntu14 system agent deepflow-agent deployment, checking logs, checking flows'
    )
    @pytest.mark.medium
    def test_compatibility_agent_ubuntu14(self):
        with allure_step(
            'step2: ubuntu14 system instance deploy the latest version of deepflow-agent'
        ):
            self.install_cgroup(vm_ip=self.vm_private_ip[self.vm_name])
            self.common_utils.vtaps_install_deepflow_agent_lastest_rpm(
                vtaps_mgt_ip=self.vm_private_ip[self.vm_name]
            )
        with allure_step('step3: checking ubuntu14 agent on DF vtaps list'):
            utils.loop_check_vtaps_list_info(
                count=loop_num, df_mgt_ip=self.df_ce_info["mgt_ip"],
                vtaps_data=utils.get_vtaps_list_info,
                vtaps_content=self.vm_name, vtaps_value=vtaps_name
            )
        with allure_step('step4: checking ubuntu14 agent flow info'):
            utils.vtaps_send_icmp_flow(
                vtaps_mgt_ip=self.vm_private_ip[self.vm_name], dst_ip=dst_ip
            )
            utils.check_vtaps_deepflow_agent_flow(
                df_mgt_ip=self.df_ce_info["mgt_ip"],
                vtaps_mgt_ip=self.vm_private_ip[self.vm_name]
            )
        with allure_step('step5: ubuntu14 agent abnormal restart scene'):
            utils.workload_v_force_kill_agent_action(
                vtaps_mgt_ip=self.vm_private_ip[self.vm_name]
            )
        with allure_step('step6: ubuntu14 agent check deepflow-agent logs'):
            utils.check_vtaps_deepflow_agent_logs(
                vtaps_mgt_ip=self.vm_private_ip[self.vm_name]
            )

    def install_cgroup(
        self, vm_ip, username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default
    ):
        ssh = ssh_pool.get(vm_ip, ssh_port, username, password)
        stdin, stdout, stderr = ssh.exec_command(
            '''apt-get update&&apt-get install cgroup-bin -y'''
        )
        logging.info(
            f"install cgroup: {stdout.readlines()}, err:{stderr.readlines()}"
        )
