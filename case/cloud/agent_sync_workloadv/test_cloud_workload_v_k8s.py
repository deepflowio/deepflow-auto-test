# coding: utf-8

import logging
import time
import pytest

from common import aliyun_sdk
from common import common_config
from common.agent import Agent
from common.domain import Domain
from case.base import BaseCase
from case.cloud.agent_sync_workloadv.utils import AgentSync
from common.const import CASE_TYPE_MONOPOLIZE
from common.utils import step as allure_step
import allure

vm_name = 'automation-cloud_workload_v_test_k8s'
domain_agent_sync_name = 'agent_sync'
loop_counts = 15


class TestCloudWorkloadVK8S(BaseCase):

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
            # agent_sync_conf.domain_check_agent_sync_status()
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
            domain_name=domain_agent_sync_name
        )
        agent_sync_conf.delete_domain_by_lcuuid(
            domain_lcuuid=agent_sync_domain_lcuuid
        )
        with allure_step('step7: deleting instance by Aliyun SDK'):
            aliyun_sdk.release_instance_by_delpoy(
                uuid=common_config.pytest_uuid, instance_names=[cls.vm_name]
            )

    @allure.suite('resource')
    @allure.epic('resource docking test')
    @allure.feature('resource docking - agent synchronization Workload-v')
    @allure.title('采集器同步Workload-v附属K8s场景')
    @allure.description(
        'After resource synchronization,check region, subnet, instance, VPC'
    )
    @pytest.mark.medium
    def test_cloud_workload_v_k8s(self):
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
            self.common_utils.vtaps_install_k8s(vtaps_mgt_ip=vtap_mgt_ip)
            self.common_utils.k8s_vtaps_install_deepflow_agent(
                vtaps_mgt_ip=vtap_mgt_ip
            )
        with allure_step(
            'step4: check the vtaps is synchronized successfully'
        ):
            self.common_utils.loop_check_vtaps_list_by_ip(
                counts=loop_counts,
                vtaps_mgt_ip=self.vm_private_ip[self.vm_name]
            )
        with allure_step('step5: docking subdomain k8s'):
            subdomain = Domain(
                self.df_ce_info["mgt_ip"],
                self.df_ce_info["server_controller_port"]
            )
            vpc_lcuuid = subdomain.get_vpc_lcuuid_by_ip(
                vtap_mgt_ip=self.vm_private_ip[self.vm_name]
            )
            domain_lcuuid = subdomain.get_domain_lcuuid_by_name(
                domain_name=domain_agent_sync_name
            )
            subdomain.add_subdomain_agent_sync(
                vpc_lcuuid=vpc_lcuuid, domain_lcuuid=domain_lcuuid
            )
            cluster_id = subdomain.get_subdomain_cluster_id_by_name()

            agent.k8s_vtap_uninstall_deepflow_agent(
                vtap_mgt_ip=self.vm_private_ip[self.vm_name]
            )
            self.common_utils.k8s_vtaps_install_deepflow_agent(
                vtaps_mgt_ip=self.vm_private_ip[self.vm_name],
                cluster_id=cluster_id
            )
            agent.delete_vtaps_list_by_ip(
                vtap_mgt_ip=self.vm_private_ip[self.vm_name],
                df_mgt_ip=self.df_ce_info["mgt_ip"],
                df_server_controller_port=self
                .df_ce_info["server_controller_port"]
            )
            # vtaps list info
            self.common_utils.loop_check_vtaps_list_by_ip(
                counts=loop_counts,
                vtaps_mgt_ip=self.vm_private_ip[self.vm_name]
            )
        with allure_step('step6: check region, subnet, instance, VPC'):
            domain = Domain(
                self.df_ce_info["mgt_ip"],
                self.df_ce_info["server_controller_port"]
            )
            domain_lcuuid = domain.get_domain_lcuuid_by_name(
                domain_name=domain_agent_sync_name
            )
            agent_sync = AgentSync(self.df_ce_info["mgt_ip"])
            vtap_hostname_info = agent_sync.get_vtap_hostname(
                vtap_mgt_ip=self.vm_private_ip[self.vm_name]
            )
            agent_sync.modify_mysql_database_max_connect_error()
            agent_sync.check_pod_cluster_in_deepflow_database_by_subdomain_name(
                subdomain_name=domain_agent_sync_name
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
            agent_sync.check_az_in_deepflow_database_by_domain_lcuuid(
                domain_lcuuid=domain_lcuuid
            )
