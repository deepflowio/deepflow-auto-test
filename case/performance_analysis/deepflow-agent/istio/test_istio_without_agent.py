# coding: utf-8
import time
import datetime
import uuid
import pytest
from common.utils import step as allure_step
import allure
import os
import logging
from case.performance_analysis import utils
from case.performance_analysis.analysis_writer import Writer
from case.base import BaseCase
from common import aliyun_sdk
from common import common_config

k8s_vm_name_istio = 'automation-performance-agent-istio-without-agent'
loop_num = 15


class TestIstioWithoutAgent(BaseCase):

    vm_id_info = None
    vm_private_ip = None
    k8s_vm_name_istio = None

    @classmethod
    def _setup_class(cls):
        cls.k8s_vm_name_istio = f"{k8s_vm_name_istio}-{common_config.pytest_uuid}"
        cls.vm_id_info = {}
        cls.vm_private_ip = {}

    @classmethod
    def _teardown_class(cls):
        pass

    @allure.suite('performance analysis')
    @allure.epic('Agent performance analysis')
    @allure.feature('')
    @allure.title('Agent性能分析-istio-无agent')
    @allure.description('Agent performance analysis - istio without agent')
    @pytest.mark.medium
    def test_performance_agent_istio_without_agent(self):
        case_id = ""
        case_name = "agent_performance_analysis_istio_without_agent"
        time_end = common_config.current_timestamp - common_config.current_timestamp % 60
        with allure_step('step1: create aliyun instance'):
            self.vm_private_ip = aliyun_sdk.create_instances_by_deploy(
                uuid=common_config.pytest_uuid,
                instance_names=[self.k8s_vm_name_istio], image_id=common_config
                .ali_image_centos7_agent_performance_istio,
                instance_type=common_config.ali_instance_type_c6_2x_large
            )
            logging.info(self.vm_private_ip)
            self.common_utils.vtaps_install_k8s(
                vtaps_mgt_ip=self.vm_private_ip[self.k8s_vm_name_istio]
            )
            utils.upload_tools(self.vm_private_ip[self.k8s_vm_name_istio])

        with allure_step('step2: install istio'):
            utils.update_wrk_rate(self.vm_private_ip[self.k8s_vm_name_istio])
            utils.install_istio(self.vm_private_ip[self.k8s_vm_name_istio])
            utils.init_istio(self.vm_private_ip[self.k8s_vm_name_istio])
            utils.update_productpage_ip(
                self.vm_private_ip[self.k8s_vm_name_istio]
            )

        with allure_step('step3: run analysis without agent'):
            utils.run_istio_analysis(
                self.vm_private_ip[self.k8s_vm_name_istio], with_agent=False
            )

        with allure_step('step4: get analysis result and write'):
            result = utils.get_analysis_result(
                istio_ip=self.vm_private_ip[self.k8s_vm_name_istio],
                time_end=time_end, with_agent=False
            )
            logging.info(f"Analysis Result: {result}")
            deepflow_agent_image_tag = os.environ.get(
                'DEEPFLOW_AGENT_IMAGE_TAG'
            )
            case_id = f"istio_{(datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%m-%d-%H-%M')}_{deepflow_agent_image_tag}"
            meta = {
                "case_id": {
                    "type": "tag",
                    "value": case_id
                },
            }
            Writer(meta).write_to(result)

        with allure_step('step5: delete aliyun instance'):
            aliyun_sdk.release_instance_by_delpoy(
                uuid=common_config.pytest_uuid,
                instance_names=[self.k8s_vm_name_istio]
            )
            self.common_utils.delete_vtaps_list_by_name(
                vtaps_name=self.k8s_vm_name_istio
            )
            self.common_utils.delete_domain_list_by_ip(
                vtaps_mgt_ip=self.vm_private_ip[self.k8s_vm_name_istio]
            )
