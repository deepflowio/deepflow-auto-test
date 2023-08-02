# coding: utf-8

import logging
import time
import pytest
import allure

from common import aliyun_sdk
from common import common_config
from common.domain import Domain
from common.agent import Agent
from case.base import BaseCase
from case.cloud.agent_sync_workloadv.utils import AgentSync
from common.const import CASE_TYPE_MONOPOLIZE
from common.utils import step as allure_step

vm_name = 'automation-cloud_workload_v_test'
loop_counts = 15


class TestCloudWorkloadVSingle(BaseCase):

    vm_name = None
    vm_private_ip = None
    CASE_TYPE = CASE_TYPE_MONOPOLIZE

    @classmethod
    def _setup_class(cls):
        cls.vm_name = f"{vm_name}-{common_config.pytest_uuid}"
        agent_sync_conf = Domain(
            cls.df_ce_info["mgt_ip"], cls.df_ce_info["server_controller_port"]
        )
        if not agent_sync_conf.domain_platform_is_exist(
            expect_domain_type=common_config.domain_agent_sync_name_default
        ):
            agent_sync_conf.add_deepflow_ctl_cmd_latest()
            agent_sync_conf.add_domain_agent_sync()
            logging.info('add_domain_agent_sync::agent sync add success')
        else:
            agent_sync_conf.add_deepflow_ctl_cmd_latest()
            logging.info('add_domain_agent_sync::agent sync is exist')
        with allure_step('step1: creating instance by Aliyun SDK'):
            cls.vm_private_ip = aliyun_sdk.create_instances_by_deploy(
                uuid=common_config.pytest_uuid,
                instance_names=[cls.vm_name],
                image_id=common_config.ali_image_centos7_deepflow_id,
            )

    @classmethod
    def _teardown_class(cls):
        agent_sync_conf = Domain(
            cls.df_ce_info["mgt_ip"], cls.df_ce_info["server_controller_port"]
        )
        agent_sync_domain_lcuuid = agent_sync_conf.get_domain_lcuuid_by_name(
            domain_name=common_config.domain_agent_sync_name_default
        )
        print(f"domain lcuuid: {agent_sync_domain_lcuuid}")
        agent_sync_conf.delete_domain_by_lcuuid(
            domain_lcuuid=agent_sync_domain_lcuuid
        )
        with allure_step('step6: deleting instance by Aliyun SDK'):
            aliyun_sdk.release_instance_by_delpoy(
                uuid=common_config.pytest_uuid, instance_names=[cls.vm_name]
            )

    @allure.suite('resource')
    @allure.epic('resource docking test')
    @allure.feature('resource docking - agent synchronization Workload-v')
    @allure.title('采集器同步Workload-v单个采集器场景')
    @allure.description(
        'After resource synchronization, check region,subnet,instance,VPC'
    )
    @pytest.mark.medium
    def test_cloud_workload_v_single(self):
        with allure_step(
            'step2: enable resource synchronization for the agent default group'
        ):
            agent = Agent(
                self.df_ce_info["mgt_ip"],
                self.df_ce_info["server_controller_port"], self.common_utils
            )
            # agent.group.get_all_agent_group_list()
            agent.group.update_agent_group_according_name()
            agent.config.try_delete_group_config()
            agent.config.set_group_config(
                agent_group_lcuuid=agent.group.agent_group_lcuuid,
                PLATFORM_ENABLED=1
            )
        with allure_step(
            'step3: instance deploy the latest version of deepflow-agent'
        ):
            vtap_mgt_ip = self.vm_private_ip[self.vm_name]
            agent = Agent(
                self.df_ce_info["mgt_ip"],
                self.df_ce_info["server_controller_port"], self.common_utils
            )
            agent.workloadv_install_deepflow_agent(vtaps_mgt_ip=vtap_mgt_ip)
        with allure_step(
            'step4: check the vtaps is synchronized successfully'
        ):
            self.common_utils.loop_check_vtaps_list_by_ip(
                counts=loop_counts,
                vtaps_mgt_ip=self.vm_private_ip[self.vm_name]
            )
        with allure_step('step5: check region, subnet, instance, VPC'):
            domain = Domain(
                self.df_ce_info["mgt_ip"],
                self.df_ce_info["server_controller_port"]
            )
            domain_lcuuid = domain.get_domain_lcuuid_by_name(
                domain_name=common_config.domain_agent_sync_name_default
            )
            agent_sync = AgentSync(self.df_ce_info["mgt_ip"])
            vtap_hostname_info = agent_sync.get_vtap_hostname(
                vtap_mgt_ip=self.vm_private_ip[self.vm_name]
            )
            agent_sync.modify_mysql_database_max_connect_error()
            agent_sync.check_az_in_deepflow_database_by_domain_lcuuid(
                domain_lcuuid=domain_lcuuid
            )
            agent_sync.check_vms_in_deepflow_database_by_hostname(
                vtap_hostname=vtap_hostname_info
            )
            agent_sync.check_vpc_in_deepflow_database_by_ip(
                vtap_mgt_ip=self.vm_private_ip[self.vm_name]
            )
            agent_sync.check_subnet_in_deepflow_database_by_ip(
                vtap_mgt_ip=self.vm_private_ip[self.vm_name]
            )
