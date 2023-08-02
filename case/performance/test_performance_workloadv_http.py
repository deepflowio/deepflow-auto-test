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
from common.ssh import ssh_pool
from perf_writer import Writer
from common.agent import Agent

# Customized variables
workloadv_vm_name = 'automation-workloadv-performance-http'
loop_num = 15


def vtaps_workloadv_create_http_flow_action(
    vtaps_mgt_ip, username=common_config.ssh_username_default,
    password=common_config.ssh_password_default,
    ssh_port=common_config.ssh_port_default
):
    '''Login to workloadv vtaps by SSH to generate HTTP flow
    '''
    ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
    stdin, stdout, stderr = ssh.exec_command(
        'systemctl restart nginx && systemctl status nginx'
    )
    if 'Started nginx' in stdout.readlines()[-1]:
        logging.info('nginx server started successfully')
    chan = ssh.invoke_shell()
    cmd = "ulimit -n 400000 && ./tcpclient 192.168.10.52,192.168.10.200,192.168.10.201,192.168.10.202,192.168.10.203,192.168.10.204,192.168.10.205 192.168.10.51,192.168.10.100,192.168.10.101,192.168.10.102,192.168.10.103,192.168.10.104,192.168.10.105 > tcpclient.log &\n"
    chan.send(cmd)
    time.sleep(1)
    start_time = int(time.time())
    logging.info('start generate http flow')
    time.sleep(300)
    end_time = int(time.time())
    logging.info('complete generate http flow')
    return start_time, end_time


def generate_dispatcher_http_result(
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
        "commit_id": utils.get_agent_commit_id(vtaps_mgt_ip, False),
        "time": common_config.current_timestamp -
        common_config.current_timestamp % 60
    }]
    format_point = utils.unit_format(point[0])
    perf_template = '''
    workload-v的linux环境-HTTP包测试结果
        运行环境信息：
        - IP：{}
        - 内核版本：4.19
        - 操作系统：centos7.9
        - 资源：2C4G
        采集器信息
        - 资源限制：1C768M
        打流命令：
        - 命令：wrk -t2 -c 3000 -d 300 http://X.X.X.X/index.html
        - 协议：HTTP
        - 并发: 3K
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
    return performance_result


class TestPerformanceWorkloadHttp(BaseCase):

    performance_result = None
    vm_id_info = None
    vm_private_ip = None
    workloadv_vm_name = None
    vtap_group_name = None

    @classmethod
    def _setup_class(cls):
        with allure_step('step 1: creating centos7 instance by Aliyun SDK'):
            cls.performance_result = ['']
            #if self.common_utils.check_aliyun_cloud_isexist() == False:
            #    self.common_utils.add_deepflow_server_dns()
            #    self.common_utils.add_aliyun_cloud_platform()
            #    self.common_utils.check_aliyun_cloud_status()
            cls.workloadv_vm_name = f"{workloadv_vm_name}-{common_config.pytest_uuid}"
            cls.vtap_group_name = f"vtap_group_workload_http_{common_config.pytest_uuid}"
            cls.vm_private_ip = aliyun_sdk.create_instances_by_deploy(
                uuid=common_config.pytest_uuid,
                instance_names=[cls.workloadv_vm_name], image_id=common_config
                .ali_image_centos7_agent_performance_nginx,
                instance_type=common_config.ali_instance_type_c6_2x_large
            )

    @classmethod
    def _teardown_class(cls):
        with allure_step('step 7: deleting centos7 instance by Aliyun SDK'):
            logging.info(
                'workload-v_performance_http test result in below\n{}'.format(
                    cls.performance_result[0]
                )
            )
            aliyun_sdk.release_instance_by_delpoy(
                uuid=common_config.pytest_uuid,
                instance_names=[cls.workloadv_vm_name]
            )
            cls.common_utils.delete_vtaps_list_by_name(
                vtaps_name=cls.workloadv_vm_name
            )
            logging.info(
                'workload-v_performance_http test result in below\n{}'.format(
                    cls.performance_result[0]
                )
            )
            agent = Agent(
                cls.df_ce_info["mgt_ip"],
                cls.df_ce_info["server_controller_port"], cls.common_utils
            )
            agent.group.delete_agent_group_by_name(name=cls.vtap_group_name)
            print(
                'workload-v_performance_http test result in below\n{}'.format(
                    cls.performance_result[0]
                )
            )

    @allure.suite('performance test')
    @allure.epic('Agent performance test')
    @allure.feature('Agent performance test - workloadv')
    @allure.title('workloadv采集器HTTP包性能测试')
    @allure.description(
        'workloadv vtaps deploy deepflow-agent, generate HTTP flow, outputs test results'
    )
    @pytest.mark.medium
    def test_performance_workloadv_http(self):
        case_id = "test_performance_workloadv_http_001"
        case_name = "Workload-V采集器的http流量"

        with allure_step('step2: init tcp server'):
            utils.init_high_concuerrency_server(
                self.vm_private_ip[self.workloadv_vm_name]
            )
        with allure_step('step3: workload-v vtaps deploy deepflow-agent'):
            self.common_utils.workloadv_vtaps_install_deepflow_agent(
                self.vm_private_ip[self.workloadv_vm_name]
            )

        with allure_step(
            'step4: check workload-v vtaps is synchronized successfully'
        ):
            vtap_lcuuid = self.common_utils.loop_check_vtaps_list_by_name(
                counts=loop_num, vtaps_name=self.workloadv_vm_name
            )
            agent = Agent(
                self.df_ce_info["mgt_ip"],
                self.df_ce_info["server_controller_port"], self.common_utils
            )
            agent.vm_ip = self.vm_private_ip[self.workloadv_vm_name]
            agent.vtap_lcuuid = vtap_lcuuid
            agent.config.add_group_with_exist_agent(
                group_name=self.vtap_group_name, vtap_lcuuid=agent.vtap_lcuuid
            )
            agent.config.add_advanced_group_config(
                agent_group_name=self.vtap_group_name,
            )
        with allure_step('step5: workload-v vtaps generate HTTP flow'):
            start_time, end_time = vtaps_workloadv_create_http_flow_action(
                vtaps_mgt_ip=self.vm_private_ip[self.workloadv_vm_name]
            )

        with allure_step('step6: view and generate test results'):
            self.performance_result[0] = generate_dispatcher_http_result(
                vtaps_mgt_ip=self.vm_private_ip[self.workloadv_vm_name],
                df_mgt_ip=self.df_ce_info["mgt_ip"], start_time=start_time,
                end_time=end_time, case_info=(case_id, case_name),
                common_utils=self.common_utils
            )


if __name__ == '__main__':
    test = TestPerformanceWorkloadHttp()
    test.test_performance_workloadv_http()
