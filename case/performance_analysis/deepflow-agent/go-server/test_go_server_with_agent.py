# coding: utf-8
import time
import datetime
import pytest
from common.utils import step as allure_step
import allure
import os
import uuid
import logging
from case.performance_analysis import utils
from case.performance_analysis.analysis_writer import Writer
from case.base import BaseCase
from common import aliyun_sdk
from common import common_config
from common.agent import Agent

k8s_vm_name_go_server = 'automation-performance-agent-go-server-with-agent'
loop_num = 15


class TestGoServerWithAgent(BaseCase):

    vm_id_info = None
    vm_private_ip = None
    k8s_vm_name_go_server = None
    vtap_group_name = None

    @classmethod
    def _setup_class(cls):
        cls.k8s_vm_name_go_server = f"{k8s_vm_name_go_server}-{common_config.pytest_uuid}"
        cls.vtap_group_name = f"vtap_group_goserver_{common_config.pytest_uuid}"
        cls.vm_id_info = {}
        cls.vm_private_ip = {}

    @classmethod
    def _teardown_class(cls):
        pass

    @allure.suite('performance analysis')
    @allure.epic('Agent performance analysis')
    @allure.feature('')
    @allure.title('Agent性能分析-go-server')
    @allure.description('Agent performance analysis - go-server')
    @pytest.mark.medium
    def test_performance_agent_go_server(self):
        case_id = ""
        case_name = "agent_performance_analysis_go_server"
        time_end = common_config.current_timestamp - common_config.current_timestamp % 60
        with allure_step('step1: create aliyun instance'):
            self.vm_private_ip = aliyun_sdk.create_instances_by_deploy(
                uuid=common_config.pytest_uuid,
                instance_names=[self.k8s_vm_name_go_server],
                image_id=common_config
                .ali_image_centos7_agent_performance_goserver,
                instance_type=common_config.ali_instance_type_c6_2x_large
            )
            logging.info(self.vm_private_ip)
            utils.upload_tools(self.vm_private_ip[self.k8s_vm_name_go_server])

        with allure_step('step2: install go server'):
            utils.update_wrk_rate(
                self.vm_private_ip[self.k8s_vm_name_go_server]
            )
            time.sleep(10)
            utils.init_go_server(
                self.vm_private_ip[self.k8s_vm_name_go_server]
            )

        with allure_step('step3: install deepflow-agent and check sync info'):
            self.common_utils.vtaps_install_deepflow_agent_lastest_rpm(
                vtaps_mgt_ip=self.vm_private_ip[self.k8s_vm_name_go_server]
            )
            vtap_lcuuid = self.common_utils.loop_check_vtaps_list_by_ip(
                counts=loop_num,
                vtaps_mgt_ip=self.vm_private_ip[self.k8s_vm_name_go_server]
            )
            go_server_agent_commit_id = utils.get_agent_commit_id(
                self.vm_private_ip[self.k8s_vm_name_go_server], is_pod=False
            )
            agent = Agent(
                self.df_ce_info["mgt_ip"],
                self.df_ce_info["server_controller_port"], self.common_utils
            )
            agent.vm_ip = self.vm_private_ip[self.k8s_vm_name_go_server]
            agent.vtap_lcuuid = vtap_lcuuid
            # agent.check_vtaps_list_by_name()
            agent.config.add_group_with_exist_agent(
                group_name=self.vtap_group_name, vtap_lcuuid=agent.vtap_lcuuid
            )
            agent.config.add_advanced_group_config(
                agent_group_name=self.vtap_group_name,
            )

        with allure_step('step4: run analysis with agent'):
            utils.run_go_server_analysis(
                self.vm_private_ip[self.k8s_vm_name_go_server], with_agent=True
            )

        with allure_step('step5: get analysis result and write'):
            result = utils.get_analysis_result(
                go_server_ip=self.vm_private_ip[self.k8s_vm_name_go_server],
                time_end=time_end, with_agent=True
            )
            logging.info(f"Analysis Result: {result}")
            deepflow_agent_image_tag = os.environ.get(
                'DEEPFLOW_AGENT_IMAGE_TAG'
            )
            case_id = f"go_server_{(datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%m-%d-%H-%M')}_{deepflow_agent_image_tag}"
            meta = {
                "case_id": {
                    "type": "tag",
                    "value": case_id
                },
                "commit_id": {
                    "type": "tag",
                    "value": go_server_agent_commit_id
                },
                "annotation_commit_id": {
                    "type": "tag",
                    "value": f"CommitID={go_server_agent_commit_id}"
                }
            }
            Writer(meta).write_to(result)

        with allure_step('step6: delete aliyun instance'):
            aliyun_sdk.release_instance_by_delpoy(
                uuid=common_config.pytest_uuid,
                instance_names=[self.k8s_vm_name_go_server]
            )
            self.common_utils.delete_vtaps_list_by_name(
                vtaps_name=self.k8s_vm_name_go_server
            )
            self.common_utils.delete_domain_list_by_ip(
                vtaps_mgt_ip=self.vm_private_ip[self.k8s_vm_name_go_server]
            )
