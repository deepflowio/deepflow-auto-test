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
from common.performance_data_collector import PerfDataCollect
from common.agent import Agent
from common.ssh import ssh_pool
from perf_writer import Writer

# Customized variables
k8s_vm_name = 'automation-performance-k8s-udp'
loop_num = 15
UDP_KPPS = 300


def vtaps_k8s_create_udp_flow(
    vtaps_mgt_ip, pod_client_name, pod_server_ip,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default,
    ssh_port=common_config.ssh_port_default
):
    '''Login to the vtaps by SSH, use POD to generate UDP small package flow,parameter description:
    vtaps_mgt_ip; required field,The ip of vtaps
    pod_client_name; required field,pod that generate UDP small package
    pod_server_name; required field,Name of the pod that receive UDP small package
    pod_server_ip; required field,Ip of the pod that receive UDP small package
    '''
    ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
    chan = ssh.invoke_shell()
    chan.send('kubectl exec -ti %s bash\n' % (pod_client_name))
    chan.send(
        f'cd /root && ./udp_flood -h {pod_server_ip} -t 15 -r 650000 -p 23456\n'
    )
    # for i in range(1, (UDP_KPPS // common_config.HPING3_FASTER_PPS) + 1):
    #     chan.send(
    #         'nohup hping3 -d 18 %s -2 -n -p 1004%s -s 1004%s -k --flood &\n' %
    #         (pod_server_ip, i, i + 1)
    #     )
    time.sleep(1)
    start_time = int(time.time())
    logging.info('start UDP small package')
    time.sleep(300)
    end_time = int(time.time())
    logging.info('complete UDP small package')
    return start_time, end_time


def vtaps_k8s_create_udp_flow_action(vtaps_mgt_ip):
    '''Create pod and generate UDP small package,parameter description:
    vtaps_mgt_ip; required field,The ip of vtaps
    '''
    pod_client_name, pod_client_ip, pod_server_name, pod_server_ip = utils.create_udp_performance_pods(
        vtaps_mgt_ip
    )
    start_time, end_time = vtaps_k8s_create_udp_flow(
        vtaps_mgt_ip=vtaps_mgt_ip, pod_client_name=pod_client_name,
        pod_server_ip=pod_server_ip
    )
    return start_time, end_time


def generate_dispatcher_udp_result(
    vtaps_mgt_ip, df_mgt_ip, start_time, end_time, case_info, common_utils
):
    cpu_usage, mem_usage, dispatcher_bps, dispatcher_pps, drop_pack, concurrent = utils.get_dispatcher_info_action(
        vtaps_mgt_ip, df_mgt_ip, start_time, end_time, common_utils
    )
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
    容器-v的linux环境-UDP小包测试结果
        运行环境信息：
        - IP：{}
        - 内核版本：4.19
        - 操作系统：centos7.9
        - 资源：8C16G
        采集器信息
        - 资源限制：1C768M
        打流命令：
        - 命令：hping3 -d 18 X.X.X.X -2 -p XXXXX-s XXXXX -k --flood
        - 协议：UDP
        - bps：--
        - pps：600Kpps
        - size：60
        性能结果：
        - CPU(Max): {}
        - 内存(Max): {}
        - 采集bps(Max): {}
        - 采集pps(Max): {}
        - 并发链接数：{}
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


class TestPerformancceK8sUdp(BaseCase):

    performance_result = None
    vm_id_info = None
    vm_private_ip = None
    k8s_vm_name = None
    vtap_group_name = None

    @classmethod
    def _setup_class(cls):
        with allure_step('step 1: creating centos7 instance by Aliyun SDK'):
            cls.performance_result = ['']
            vm_uuid = str(uuid.uuid4())
            cls.k8s_vm_name = f"{k8s_vm_name}-{vm_uuid[:7]}"
            cls.vtap_group_name = f"vtap_group_k8s_udp_{vm_uuid[:7]}"
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
            agent = Agent(
                cls.df_ce_info["mgt_ip"],
                cls.df_ce_info["server_controller_port"], cls.common_utils
            )
            agent.group.delete_agent_group_by_name(name=cls.vtap_group_name)
            logging.info(
                'k8s_performance_udp test result in below\n{}'.format(
                    cls.performance_result[0]
                )
            )
            print(
                'k8s_performance_udp test result in below\n{}'.format(
                    cls.performance_result[0]
                )
            )

    @allure.suite('performance test')
    @allure.epic('Agent performance test')
    @allure.feature('Agent performance test - k8s')
    @allure.title('容器采集器UDP小包性能测试')
    @allure.description(
        'deploy K8S deepflow-agent,generate UDP small package flow, outputs test results'
    )
    @pytest.mark.medium
    def test_performance_k8s_udp(self):
        case_id = "test_performance_k8s_udp_001"
        case_name = "容器-V采集器的udp流量"

        vm_private_ip = self.vm_private_ip
        with allure_step('step2: vtaps deploy k8s and deepflow-agent for k8s'):
            self.common_utils.vtaps_install_deepflow_action(
                vtaps_mgt_ip=vm_private_ip[self.k8s_vm_name]
            )
        with allure_step(
            'step3: check the vtaps is synchronized successfully'
        ):
            vtap_lcuuid = self.common_utils.loop_check_vtaps_list_by_name(
                counts=loop_num, vtaps_name=self.k8s_vm_name
            )
            agent = Agent(
                self.df_ce_info["mgt_ip"],
                self.df_ce_info["server_controller_port"], self.common_utils
            )
            agent.vm_ip = vm_private_ip[self.k8s_vm_name]
            agent.vtap_lcuuid = vtap_lcuuid
            # agent.check_vtaps_list_by_name()
            agent.config.add_group_with_exist_agent(
                group_name=self.vtap_group_name, vtap_lcuuid=agent.vtap_lcuuid
            )
            agent.config.set_group_config(
                agent_group_lcuuid=agent.config.agent_group_lcuuid,
                max_collect_pps=1500
            )
        with allure_step('step4: vtaps pod generate UDP small package flow'):
            start_time, end_time = vtaps_k8s_create_udp_flow_action(
                vtaps_mgt_ip=vm_private_ip[self.k8s_vm_name]
            )
        with allure_step('step5: view and generate test results'):
            performance_result = generate_dispatcher_udp_result(
                vtaps_mgt_ip=vm_private_ip[self.k8s_vm_name],
                df_mgt_ip=self.df_ce_info["mgt_ip"], start_time=start_time,
                end_time=end_time, case_info=(case_id, case_name),
                common_utils=self.common_utils
            )
            self.performance_result[0] = performance_result
