# coding: utf-8

import time
import paramiko
import uuid
import pytest
from common.utils import step as allure_step
import allure
import logging
from case.performance import utils
from case.base import BaseCase
from common import aliyun_sdk
from common import common_config
from common.ssh import ssh_pool
from common.performance_data_collector import PerfDataCollect
from perf_writer import Writer

# Customized variables
k8s_vm_name = 'automation-performance-k8s-tcp'
loop_num = 15


def vtaps_k8s_create_tcp_flow(
    vtaps_mgt_ip, pod_client_name, pod_server_name, pod_server_ip,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default,
    ssh_port=common_config.ssh_port_default
):
    '''Login to the vtaps by SSH, use POD to generate TCP big package flow,parameter description:
    vtaps_mgt_ip; required field,The ip of vtaps
    pod_client_name; required field,pod that generate TCP big package
    pod_server_name; required field,Name of the pod that receive TCP big package
    pod_server_ip; required field,Ip of the pod that receive TCP big package
    '''
    logging.info('start generate TCP big package')
    start_time = int(time.time())
    ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
    stdin, stdout, stderr = ssh.exec_command(
        "kubectl exec -it %s -- iperf3 -s -D && \
                                            kubectl exec -it %s -- iperf3 -c %s -t 300s -b %dG -M 1400"
        % (
            pod_server_name, pod_client_name, pod_server_ip,
            common_config.TCP_PERFORMANCE_K8S_BPS // 2
        )
    )
    if 'iperf Done' in stdout.readlines()[-1]:
        logging.info('complete generate TCP big package')
    end_time = int(time.time())
    return start_time, end_time


def vtaps_k8s_create_tcp_flow_action(vtaps_mgt_ip):
    '''Create pod and generate TCP big package,parameter description:
    vtaps_mgt_ip; required field,The ip of vtaps
    '''
    pod_client_name, pod_client_ip, pod_server_name, pod_server_ip = utils.create_performance_pods(
        vtaps_mgt_ip
    )
    start_time, end_time = vtaps_k8s_create_tcp_flow(
        vtaps_mgt_ip=vtaps_mgt_ip, pod_client_name=pod_client_name,
        pod_server_name=pod_server_name, pod_server_ip=pod_server_ip
    )
    return start_time, end_time


def generate_dispatcher_tcp_result(
    vtaps_mgt_ip, df_mgt_ip, start_time, end_time, case_info, common_utils
):
    performance_result = ''
    cpu_usage, mem_usage, dispatcher_bps, dispatcher_pps, drop_pack, concurrent = utils.get_dispatcher_info_action(
        vtaps_mgt_ip, df_mgt_ip, start_time, end_time, common_utils
    )
    if cpu_usage == None or mem_usage == None or dispatcher_bps == None or dispatcher_pps == None or drop_pack == None:
        logging.error(
            'cpu_usage/mem_usage/dispatcher_bps/dispatcher_pps/drop_pack is invalid'
        )
        assert False
    case_id, case_name = case_info
    point = [{
        "cpu_usage": cpu_usage,
        "mem_usage": mem_usage,
        "dispatcher_bps": dispatcher_bps,
        "dispatcher_pps": dispatcher_pps,
        "drop_pack": drop_pack,
        "concurrent": concurrent,
        "case_id": case_id,
        "case_name": case_name,
        "vtap_mgt_ip": vtaps_mgt_ip,
        "commit_id": utils.get_agent_commit_id(vtaps_mgt_ip),
        "time": common_config.current_timestamp -
        common_config.current_timestamp % 60
    }]
    format_point = utils.unit_format(point[0])
    perf_template = '''
    容器-v的linux环境-TCP大包测试结果
        运行环境信息：
        - IP：{}
        - 内核版本：4.19
        - 操作系统：centos7.9
        - 资源：2C4G
        采集器信息
        - 资源限制：1C768M
        打流命令：
        - 命令：iperf3 -c X.X.X.X -t X -b X -M 1400
        - 协议：TCP
        - bps：6Gbps
        - pps：--
        - size：1400
        性能结果：
        - CPU(Max): {}
        - 内存(Max): {}
        - 采集bps(Max): {}
        - 采集pps(Max): {}
        - 并发连接数：{}
        - 丢包: {}
    '''
    perf_template = perf_template.format(
        vtaps_mgt_ip, format_point["cpu_usage"], format_point["mem_usage"],
        format_point["dispatcher_bps"], format_point["dispatcher_pps"],
        format_point["concurrent"], format_point["drop_pack"]
    )
    logging.info(perf_template)
    wr = Writer()
    #wr.write_to(point)
    wr.save_markdown(format_point)
    return perf_template


class TestPerormanceK8sTcp(BaseCase):

    performance_result = None
    vm_private_ip = None
    k8s_vm_name = None

    @classmethod
    def _setup_class(cls):
        with allure_step('step 1: creating centos7 instance by Aliyun SDK'):
            cls.performance_result = ['']
            # if self.common_utils.check_aliyun_cloud_isexist() == False:
            #     self.common_utils.add_deepflow_server_dns()
            #     self.common_utils.add_aliyun_cloud_platform()
            #     self.common_utils.check_aliyun_cloud_status()
            cls.k8s_vm_name = f"{k8s_vm_name}-{common_config.pytest_uuid}"
            cls.vm_private_ip = aliyun_sdk.create_instances_by_deploy(
                uuid=common_config.pytest_uuid,
                instance_names=[cls.k8s_vm_name],
                image_id=common_config.ali_image_centos7_deepflow_id,
                instance_type=common_config.ali_instance_type_c6_2x_large
            )

    @classmethod
    def _teardown_class(cls):
        with allure_step('step 6: deleting centos7 instance by Aliyun SDK'):
            aliyun_sdk.release_instance_by_delpoy(
                uuid=common_config.pytest_uuid,
                instance_names=[cls.k8s_vm_name]
            )
            cls.common_utils.delete_vtaps_list_by_name(
                vtaps_name=cls.k8s_vm_name
            )
            cls.common_utils.delete_domain_list_by_ip(
                vtaps_mgt_ip=cls.vm_private_ip[cls.k8s_vm_name]
            )
            logging.info(
                'k8s_performance_tcp test result in below\n{}'.format(
                    cls.performance_result[0]
                )
            )
            print(
                'k8s_performance_tcp test result in below\n{}'.format(
                    cls.performance_result[0]
                )
            )

    @allure.suite('performance test')
    @allure.epic('Agent performance test')
    @allure.feature('Agent performance test - k8s')
    @allure.title('容器采集器TCP大包性能测试')
    @allure.description(
        'deploy K8S deepflow-agent,generate TCP big package flow, outputs test results'
    )
    @pytest.mark.medium
    def test_performance_k8s_tcp(self):
        case_id = "test_performance_k8s_tcp_001"
        case_name = "容器-V采集器的tcp流量"
        vm_private_ip = self.vm_private_ip
        with allure_step('step2: vtaps deploy k8s and deepflow-agent for k8s'):
            self.common_utils.vtaps_install_deepflow_action(
                vtaps_mgt_ip=vm_private_ip[self.k8s_vm_name]
            )

        with allure_step(
            'step3: check the vtaps is synchronized successfully'
        ):
            self.common_utils.loop_check_vtaps_list_by_ip(
                counts=loop_num, vtaps_mgt_ip=vm_private_ip[self.k8s_vm_name]
            )

        with allure_step('step4: vtaps pod generate TCP big package flow'):
            start_time, end_time = vtaps_k8s_create_tcp_flow_action(
                vtaps_mgt_ip=vm_private_ip[self.k8s_vm_name]
            )
        with allure_step('step5: view and generate test results'):
            performance_result = generate_dispatcher_tcp_result(
                vtaps_mgt_ip=vm_private_ip[self.k8s_vm_name],
                df_mgt_ip=self.df_ce_info["mgt_ip"], start_time=start_time,
                end_time=end_time, case_info=(case_id, case_name),
                common_utils=self.common_utils
            )
            self.performance_result[0] = performance_result


if __name__ == '__main__':
    test = TestPerormanceK8sTcp()
    test.test_performance_k8s_tcp()
