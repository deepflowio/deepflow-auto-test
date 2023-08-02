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
from common.utils import CommonUtils
from common.ssh import ssh_pool
from deepflow_ce import DeployDeepflowCE
from common.querier_api_utils import QueryApi

helm_vm_name = 'automation-deepflow-ce-helm-pull-test'
loop_num = 15
lts_versions = ["6.1.8", "6.2.6"]


class TestDeepflowHelmPull(BaseCase):

    vm_private_ip = None
    deepflow_version = None
    helm_vm_name = None

    @classmethod
    def setup_class(cls):
        cls.deepflow_version = os.environ.get('DEEPFLOW_VERSION')
        cls.deploy = DeployDeepflowCE()
        with allure_step('The setup of the class'):
            cls.helm_vm_name = f"{helm_vm_name}-{common_config.pytest_uuid}"
            cls.vm_private_ip = aliyun_sdk.create_instances_by_deploy(
                uuid=common_config.pytest_uuid,
                instance_names=[cls.helm_vm_name],
                image_id=common_config.ali_image_centos7_deepflow_id,
                instance_type=common_config.ali_instance_type_c6_2x_large
            )
            cls.common_utils = CommonUtils(cls.vm_private_ip[cls.helm_vm_name])
            cls.start = time.time()

    @classmethod
    def teardown_class(cls):
        #time.sleep(12000)
        aliyun_sdk.release_instance_by_delpoy(
            uuid=common_config.pytest_uuid, instance_names=[cls.helm_vm_name]
        )

    def init_helm_repo(
        self, vtaps_mgt_ip, ssh_port=common_config.ssh_port_default,
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default
    ):
        helm_init_github = "helm repo add deepflow-github https://deepflowio.github.io/deepflow && helm repo update deepflow-github"
        helm_init_aliyun = "helm repo add deepflow-aliyun https://deepflow-ce.oss-cn-beijing.aliyuncs.com/chart/stable && helm repo update deepflow-aliyun"
        try:
            ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
            _, stdout, stderr = ssh.exec_command(helm_init_github)
            logs = stdout.readlines()
            logging.info(f"exec cmd: {helm_init_github} stdout: {logs}")
            err = stderr.readlines()
            if err:
                logging.error(f"stderr: {err}")
                assert False
            _, stdout, stderr = ssh.exec_command(helm_init_aliyun)
            logs = stdout.readlines()
            logging.info(f"exec cmd: {helm_init_aliyun} stdout: {logs}")
            err = stderr.readlines()
            if err:
                logging.error(f"stderr: {err}")
                assert False
        except Exception as e:
            logging.error(e)
            assert False

    def helm_pull_version(
        self, vtaps_mgt_ip, version="",
        ssh_port=common_config.ssh_port_default,
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default
    ):
        try:
            ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
            versions = lts_versions
            if version:
                versions += version.split(",")
            cmds = [
                "helm pull deepflow-github/deepflow --version ",
                "helm pull deepflow-github/deepflow-agent --version ",
                "helm pull deepflow-aliyun/deepflow --version ",
                "helm pull deepflow-aliyun/deepflow-agent --version ",
            ]
            for v in versions:
                for cmd in cmds:
                    cmd = f"{cmd}{v}"
                    _, stdout, stderr = ssh.exec_command(cmd)
                    logs = stdout.readlines()
                    logging.info(f"exec cmd: {cmd} stdout: {logs}")
                    err = stderr.readlines()
                    if err:
                        logging.error(f"stderr: {err}")
                        assert False
        except Exception as e:
            logging.error(e)
            assert False

    @allure.suite('deepflow helm ')
    @allure.epic('deepflow helm pull test')
    @allure.feature('')
    @allure.title('deepflow helm pull test')
    @allure.description('deepflow helm pull version')
    @pytest.mark.medium
    def test_deepflow_helm_pull_version(self):
        case_id = ""
        case_name = "test_deepflow_helm_pull_version"
        with allure_step('step1: init helm repo'):
            time.sleep(60)
            self.init_helm_repo(self.vm_private_ip[self.helm_vm_name])

        with allure_step('step2: helm pull lts'):
            self.helm_pull_version(self.vm_private_ip[self.helm_vm_name], )
