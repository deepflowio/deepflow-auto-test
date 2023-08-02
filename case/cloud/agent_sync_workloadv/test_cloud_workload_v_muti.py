# coding: utf-8

import pytest
import logging
import allure
from common import aliyun_sdk
from common import common_config
from common.agent import Agent
from common.domain import Domain
from case.base import BaseCase
from case.cloud.agent_sync_workloadv.utils import AgentSync
from common.const import CASE_TYPE_MONOPOLIZE
from common.utils import step as allure_step

vm1_name = 'automation-cloud_workload_v_test1'
vm2_name = 'automation-cloud_workload_v_test2'
vm3_name = 'automation-cloud_workload_v_test3'
loop_counts = 15


class TestCloudWorkloadVMuti(BaseCase):

    vm1_name = None
    vm2_name = None
    vm3_name = None
    vm1_private_ip = None
    vm2_private_ip = None
    vm3_private_ip = None
    CASE_TYPE = CASE_TYPE_MONOPOLIZE

    @classmethod
    def _setup_class(cls):
        cls.vm1_name = f"{vm1_name}-{common_config.pytest_uuid}"
        cls.vm2_name = f"{vm2_name}-{common_config.pytest_uuid}"
        cls.vm3_name = f"{vm3_name}-{common_config.pytest_uuid}"
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
            cls.vm1_private_ip = aliyun_sdk.create_instances_by_deploy(
                uuid=common_config.pytest_uuid, instance_names=[cls.vm1_name],
                image_id=common_config.ali_image_centos7_deepflow_id
            )
            cls.vm2_private_ip = aliyun_sdk.create_instances_by_deploy(
                uuid=common_config.pytest_uuid, instance_names=[cls.vm2_name],
                image_id=common_config.ali_image_centos7_deepflow_id
            )
            cls.vm3_private_ip = aliyun_sdk.create_instances_by_deploy(
                uuid=common_config.pytest_uuid, instance_names=[cls.vm3_name],
                image_id=common_config.ali_image_centos7_deepflow_id
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
                uuid=common_config.pytest_uuid,
                instance_names=[cls.vm1_name, cls.vm2_name, cls.vm3_name]
            )

    @allure.suite('resource')
    @allure.epic('resource docking test')
    @allure.feature('resource docking - agent synchronization Workload-v')
    @allure.title('采集器同步Workload-v多个采集器场景')
    @allure.description(
        'After resource synchronization, check region,subnet,instance,VPC'
    )
    @pytest.mark.medium
    def test_cloud_workload_v_muti(self):
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
            vtap1_mgt_ip = self.vm1_private_ip[self.vm1_name]
            vtap2_mgt_ip = self.vm2_private_ip[self.vm2_name]
            vtap3_mgt_ip = self.vm3_private_ip[self.vm3_name]
            agent = Agent(
                self.df_ce_info["mgt_ip"],
                self.df_ce_info["server_controller_port"], self.common_utils
            )
            agent.workloadv_install_deepflow_agent(vtaps_mgt_ip=vtap1_mgt_ip)
            agent.workloadv_install_deepflow_agent(vtaps_mgt_ip=vtap2_mgt_ip)
            agent.workloadv_install_deepflow_agent(vtaps_mgt_ip=vtap3_mgt_ip)
        with allure_step(
            'step4: check the vtaps is synchronized successfully'
        ):
            self.common_utils.loop_check_vtaps_list_by_ip(
                counts=loop_counts,
                vtaps_mgt_ip=self.vm1_private_ip[self.vm1_name]
            )
            self.common_utils.loop_check_vtaps_list_by_ip(
                counts=loop_counts,
                vtaps_mgt_ip=self.vm2_private_ip[self.vm2_name]
            )
            self.common_utils.loop_check_vtaps_list_by_ip(
                counts=loop_counts,
                vtaps_mgt_ip=self.vm3_private_ip[self.vm3_name]
            )
        with allure_step('step5: check region, subnet, instance, VPC'):
            agent_sync = AgentSync(self.df_ce_info["mgt_ip"])
            vtap1_hostname_info = agent_sync.get_vtap_hostname(
                vtap_mgt_ip=self.vm1_private_ip[self.vm1_name]
            )
            vtap2_hostname_info = agent_sync.get_vtap_hostname(
                vtap_mgt_ip=self.vm2_private_ip[self.vm2_name]
            )
            vtap3_hostname_info = agent_sync.get_vtap_hostname(
                vtap_mgt_ip=self.vm3_private_ip[self.vm3_name]
            )
            agent_sync.modify_mysql_database_max_connect_error()
            agent_sync.check_vms_in_deepflow_database_by_hostname(
                vtap_hostname=vtap1_hostname_info
            )
            agent_sync.check_vms_in_deepflow_database_by_hostname(
                vtap_hostname=vtap2_hostname_info
            )
            agent_sync.check_vms_in_deepflow_database_by_hostname(
                vtap_hostname=vtap3_hostname_info
            )
            agent_sync.check_vpc_in_deepflow_database_by_ip(
                vtap_mgt_ip=self.vm1_private_ip[self.vm1_name]
            )
            agent_sync.check_vpc_in_deepflow_database_by_ip(
                vtap_mgt_ip=self.vm2_private_ip[self.vm2_name]
            )
            agent_sync.check_vpc_in_deepflow_database_by_ip(
                vtap_mgt_ip=self.vm3_private_ip[self.vm3_name]
            )
            agent_sync.check_subnet_in_deepflow_database_by_ip(
                vtap_mgt_ip=self.vm1_private_ip[self.vm1_name]
            )
            agent_sync.check_subnet_in_deepflow_database_by_ip(
                vtap_mgt_ip=self.vm2_private_ip[self.vm2_name]
            )
            agent_sync.check_subnet_in_deepflow_database_by_ip(
                vtap_mgt_ip=self.vm3_private_ip[self.vm3_name]
            )
