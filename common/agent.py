# coding: utf-8
import requests
from urllib.parse import urlencode
import json
import time
import re
import requests
import json
from urllib.parse import urlencode
from common import common_config
from common import url
from common.utils import CommonUtils
from common.utils import time_out
from common.tool.linux_cmd import LinuxCmd
from common.ssh import ssh_pool
from common import logger
from datetime import datetime
from scp import SCPClient

log = logger.getLogger()


class Agent(object):

    def __init__(self, df_mgt_ip, df_server_controller_port, common_utils):
        self.vtap_lcuuid = None
        self.config = Config(df_mgt_ip, df_server_controller_port)
        self.group = Group(df_mgt_ip, df_server_controller_port)
        self.linux_cmd = LinuxCmd()

        self.query_port = df_server_controller_port
        self.vtaps_name = None
        self.vtap_full_name = None
        self.vtaps_mgt_ip = None
        self.detail = None  # information about agent
        self.boot_time = None  # agent startup time
        self.start_time = None  # the time start to construction flow
        self.end_time = None  # the time finish the construction flow
        self.df_mgt_ip = df_mgt_ip
        self.common_utils = common_utils

    def setter(self, **kwargs):
        for key, value in kwargs.items():
            if key == "query_port":
                self.query_port = value
            elif key == "vtaps_name":
                self.vtaps_name = value
            elif key == "start_time":
                self.start_time = value
            elif key == "end_time":
                self.end_time = value
            elif key == "vtaps_mgt_ip":
                self.vtaps_mgt_ip = value
            elif key == "vtap_lcuuid":
                self.vtap_lcuuid = value
            elif key == "vtap_full_name":
                self.vtap_full_name = value
            elif key == "vm_ip":
                self.vm_ip = value

    def get_vtaps_max_cpu_usage(self):
        '''Maximum CPU usage of the agent on DF by API. Parameter description:
        query_port; required field, Query the port of the interface
        vtap_full_name; required field, Name of vtaps
        start_time; required field, Start time for filtering data
        end_time; required field, End time for filtering data
        self.df_mgt_ip; required field, The ip of DF
        '''
        query_port = self.query_port
        vtap_full_name = self.vtap_full_name
        start_time = self.start_time
        end_time = self.end_time
        log.info(
            "get_vtaps_max_cpu_usage::query_port ==> {}".format(query_port)
        )
        log.info(
            "get_vtaps_max_cpu_usage::vtap_full_name ==> {}"
            .format(vtap_full_name)
        )
        log.info(
            "get_vtaps_max_cpu_usage::start_time ==> {}".format(start_time)
        )
        log.info("get_vtaps_max_cpu_usage::end_time ==> {}".format(end_time))
        max_cpu_list = list()
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'db': 'deepflow_system',
            'sql': '''select Avg(`metrics.cpu_percent`) AS RSS,time(time, 60) AS time_interval,`tag.host` from \
                deepflow_agent_monitor where `tag.host` IN ('%s') AND time>=%s \
                AND time<=%s group by time_interval,`tag.host` limit 100''' %
            (vtap_full_name, start_time, end_time)
        }
        log.info("get_vtaps_max_cpu_usage::data ==> {}".format(data))
        data = urlencode(data, encoding='gb2312')
        res = requests.post(
            url='http://%s:%s/v1/query/' % (self.df_mgt_ip, query_port),
            headers=headers, data=data
        )
        log.info("get_vtaps_max_cpu_usage::res.json ==> {}".format(res.json()))
        for i in res.json()['result']['values']:
            max_cpu_list.append(round(round(i[-1], 2)))
        log.info(
            "get_vtaps_max_cpu_usage::max(max_cpu_list) ==> {}".format(
                max(max_cpu_list)
            )
        )
        return max(max_cpu_list)

    def get_vtaps_max_mem_usage(self):
        '''Maximum memory usage of the agent on DF by API. Parameter description:
        query_port; required field, Query the port of the interface
        vtaps_name; required field, Name of vtaps
        start_time; required field, Start time for filtering data
        end_time; required field, End time for filtering data
        df_mgt_ip; required field, The ip of DF
        '''
        query_port = self.query_port
        vtap_full_name = self.vtap_full_name
        start_time = self.start_time
        end_time = self.end_time
        log.info(
            "get_vtaps_max_cpu_usage::query_port ==> {}".format(query_port)
        )
        log.info(
            "get_vtaps_max_cpu_usage::vtap_full_name ==> {}"
            .format(vtap_full_name)
        )
        log.info(
            "get_vtaps_max_cpu_usage::start_time ==> {}".format(start_time)
        )
        log.info("get_vtaps_max_cpu_usage::end_time ==> {}".format(end_time))

        max_mem_list = list()
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'db': 'deepflow_system',
            'sql': '''select Avg(`metrics.memory`) AS RSS,time(time, 60) AS time_interval,`tag.host` from \
                deepflow_agent_monitor where `tag.host` IN ('%s') AND time>=%s \
                AND time<=%s group by time_interval,`tag.host` limit 100''' %
            (vtap_full_name, start_time, end_time)
        }
        log.info("get_vtaps_max_mem_usage::data ==> {}".format(data))
        data = urlencode(data, encoding='gb2312')
        res = requests.post(
            url='http://%s:%s/v1/query/' % (self.df_mgt_ip, query_port),
            headers=headers, data=data
        )
        log.info("get_vtaps_max_mem_usage::res.json ==> {}".format(res.json()))

        for i in res.json()['result']['values']:
            max_mem_list.append(round(i[-1] / 1000000))
        log.info(
            "get_vtaps_max_mem_usage::max(max_cpu_list) ==> {}".format(
                max(max_mem_list)
            )
        )
        return max(max_mem_list)

    def workloadv_install_deepflow_agent(
        self, vtaps_mgt_ip="", username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default, system_platform='x86',
        cluster_id=''
    ):
        '''Login to the vtaps by SSH, Deploy and start the latest version of deepflow-agent. parameter descriptions:
        vtaps_mgt_ip; The ip of vtaps
        username; login username
        password; login password
        ssh_port; port
        '''

        def check_agent_whether_running(
            stdout_ipt, key_word="running", success_log="", fail_log=""
        ):
            keys = "{}".format(key_word)
            stdout = "".join(stdout_ipt.readlines())
            if bool(re.search(keys, stdout)) == True:
                log.info(success_log)
            else:
                log.error(f"key: {keys} stdout: {stdout}")
                log.error(fail_log)
                assert False

        vtaps_mgt_ip = self.vm_ip if vtaps_mgt_ip == "" else vtaps_mgt_ip
        ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
        stdin, stdout, stderr = ssh.exec_command(
            '''cat /dev/null > /etc/resolv.conf && echo "nameserver %s" > /etc/resolv.conf && cat /etc/issue '''
            % (common_config.ali_dns_ip)
        )
        system_version = stdout.readlines()[0]
        if system_platform == 'x86' and '\S' in system_version:
            #self.common_utils.vm_install_unzip(vtaps_mgt_ip)
            self.common_utils.workloadv_vtaps_install_deepflow_agent(
                vtaps_mgt_ip
            )
            ''' cmd = ""
            cmd_list = [
                "curl -O {}".format(
                    common_config.deepflow_agent_rpm_lastest_url
                ),
                "echo nameserver 10.1.0.1 > /etc/resolv.conf"
                "curl -O http://nexus.yunshan.net/repository/tools/automation/offline/unzip/unzip-6.0-24.el7_9.x86_64.rpm",
                "rpm -ivh unzip-6.0-24.el7_9.x86_64.rpm",
                "unzip deepflow-agent-rpm.zip",
                "rpm -ivh x86_64/deepflow-agent-1*.rpm",
                "sed -i 's/  - 127.0.0.1/  - {}/g' /etc/deepflow-agent.yaml"
                .format(self.df_mgt_ip),
                "systemctl restart deepflow-agent",
                "systemctl status deepflow-agent",
            ]
            for cmd in cmd_list:
                ssh.exec_command(cmd)
                time.sleep(1)

            stdin, stdout, stderr = ssh.exec_command(cmd)
            err = stderr.readlines()
            if err:
                log.error(err) '''
            stdin, stdout, stderr = ssh.exec_command(
                '''systemctl status deepflow-agent'''
            )
            check_agent_whether_running(
                stdout, key_word='running', success_log=
                'centos7 deployed deepflow-agent successfully and running normally, vtap ip addres is {}'
                .format(vtaps_mgt_ip), fail_log=
                'centos7 failed to deploy deepflow-agent, vtap ip addr is {}'
                .format(vtaps_mgt_ip)
            )

        elif system_platform == 'x86' and 'Ubuntu' in system_version and int(
            system_version.split(' ')[1].split('.')[0]
        ) == 14:
            stdin, stdout, stderr = ssh.exec_command(
                '''curl -O %s &&\
                                                        curl -O http://nexus.yunshan.net/repository/tools/automation/offline/unzip/unzip_6.0-9ubuntu1.5_amd64.deb &&\
                                                        dpkg -i unzip_6.0-9ubuntu1.5_amd64.deb &&\
                                                        unzip deepflow-agent-deb.zip &&\
                                                        dpkg -i x86_64/deepflow-agent-*.upstart.deb &&\
                                                        sed -i 's/  - 127.0.0.1/  - %s/g' /etc/deepflow-agent.yaml &&\
                                                        service deepflow-agent restart && service deepflow-agent status'''
                %
                (common_config.deepflow_agent_deb_lastest_url, self.df_mgt_ip)
            )
            if bool(
                re.search(
                    'deepflow-agent start/running',
                    "".join(stdout.readlines())
                )
            ) == True:
                log.info(
                    '{} deployed deepflow-agent successfully and running normally, vtap ip addr is {}'
                    .format(
                        system_version.split(' ')[0] +
                        system_version.split(' ')[1], vtaps_mgt_ip
                    )
                )
                #ssh.close()
            else:
                log.error(
                    '{} failed to deploy deepflow-agent, vtap ip addr is {}'
                    .format(
                        system_version.split(' ')[0] +
                        system_version.split(' ')[1], vtaps_mgt_ip
                    )
                )
                #ssh.close()
                assert False
        elif system_platform == 'x86' and 'Ubuntu' in system_version and int(
            system_version.split(' ')[1].split('.')[0]
        ) >= 14:
            stdin, stdout, stderr = ssh.exec_command(
                '''curl -O %s &&\
                                                        curl -O http://nexus.yunshan.net/repository/tools/automation/offline/unzip/unzip_6.0-9ubuntu1.5_amd64.deb &&\
                                                        dpkg -i unzip_6.0-9ubuntu1.5_amd64.deb &&\
                                                        unzip deepflow-agent-deb.zip &&\
                                                        dpkg -i x86_64/deepflow-agent-*.systemd.deb &&\
                                                        sed -i 's/  - 127.0.0.1/  - %s/g' /etc/deepflow-agent.yaml  &&\
                                                        systemctl restart deepflow-agent && systemctl status deepflow-agent'''
                %
                (common_config.deepflow_agent_deb_lastest_url, self.df_mgt_ip)
            )
            if bool(
                re.search('active \(running\)', "".join(stdout.readlines()))
            ) == True:
                log.info(
                    '{} deployed deepflow-agent successfully and running normally, vtap ip addr is {}'
                    .format(
                        system_version.split(' ')[0] +
                        system_version.split(' ')[1], vtaps_mgt_ip
                    )
                )
                #ssh.close()
            else:
                log.error(
                    '{} failed to deploy deepflow-agent, vtap ip addr is {}'
                    .format(
                        system_version.split(' ')[0] +
                        system_version.split(' ')[1], vtaps_mgt_ip
                    )
                )
                #ssh.close()
                assert False
        elif system_platform == 'arm':
            cmd_list = [
                "curl -O https://deepflow-ce.oss-cn-beijing.aliyuncs.com/rpm/agent/latest/linux/$(arch | sed 's|x86_64|amd64|' | sed 's|aarch64|arm64|')/deepflow-agent-rpm.zip",
                "unzip deepflow-agent*.zip",
                "rpm -ivh aarch64/deepflow-agent-1*.rpm",
                "sed -i 's/  - 127.0.0.1/  - %s/g' /etc/deepflow-agent.yaml"
                .format(self.df_mgt_ip),
                "systemctl restart deepflow-agent && systemctl status deepflow-agent"
            ]
            for cmd in cmd_list:
                ssh.exec_command(cmd)
                time.sleep(1)

            stdin, stdout, stderr = ssh.exec_command(cmd)
            check_agent_whether_running(
                stdout, key_word='running', success_log=
                'centos7 deployed deepflow-agent successfully and running normally, vtap ip addres is {}'
                .format(vtaps_mgt_ip), fail_log=
                'centos7 failed to deploy deepflow-agent, vtap ip addr is {}'
                .format(vtaps_mgt_ip)
            )

    def k8s_install_k8s_and_agent_x86(self, vtaps_mgt_ip=""):
        '''Create k8s on DF and deploy the latest version of deepflow-agent on k8s, parameters:
        vtaps_mgt_ip; required, The ip of vtaps
        '''
        if vtaps_mgt_ip == "":
            vtaps_mgt_ip = self.vm_ip
        self.common_utils.vtaps_install_k8s(
            vtaps_mgt_ip
        )  # TODO  X86的镜像的仓库和Arm的仓库位置不一样，所以这里暂时使用self.common_utils下的代码
        # self.vtap_install_k8s(vtaps_mgt_ip)  # TODO 以后统一代码，用这行代码，使X86和arm的一致
        self.common_utils.k8s_vtaps_install_deepflow_agent(vtaps_mgt_ip)

    def k8s_install_k8s_and_agent_arm(self, vtaps_mgt_ip=""):
        '''Create k8s on DF and deploy the latest version of deepflow-agent on k8s, parameters:
        vtaps_mgt_ip; required, The ip of vtaps
        '''
        if vtaps_mgt_ip == "":
            vtaps_mgt_ip = self.vm_ip
        self.common_utils.vtaps_install_k8s(vtaps_mgt_ip)
        self.common_utils.k8s_vtaps_install_deepflow_agent(vtaps_mgt_ip)

    def k8s_vtap_uninstall_deepflow_agent(self, vtap_mgt_ip=""):
        '''Login to the vtaps by SSH, vtaps uninstalling deepflow-agent on K8S, paraneters
        vtaps_mgt_ip; The ip of vtaps
        return uninstallation status
        '''
        deepflow_agent_deploy_status = False
        vtap_mgt_ip = self.vm_ip if vtap_mgt_ip == "" else vtap_mgt_ip
        cmd_list = ["helm uninstall deepflow-agent -n deepflow", "sleep 15"]
        cmd = " && ".join(cmd_list)
        self.linux_cmd.setter(vm_ip=vtap_mgt_ip)
        self.linux_cmd.exec_cmd(cmd)
        deepflow_agent_deploy_status = True
        return deepflow_agent_deploy_status

    def wait_agent_discovered_successfully(self, duration=600):
        is_discovered = False
        start_time = int(time.time())
        for _ in range(duration):
            status = self.check_agent_registration_status(
                expect_status_registered=True, assertion_required=False
            )
            if status:
                is_discovered = True
                break

            time.sleep(1)
            time_consumed = int(time.time()) - start_time
            log.info(
                "wait_agent_discovered_successfully::It has lasted for {} seconds"
                .format(time_consumed)
            )

        assert is_discovered

    def check_agent_registration_status(
        self, agent_ip="", expect_status_registered=True,
        assertion_required=True
    ):
        '''
        func: Check the registration status of the agent and make assertions or returns according to the incoming expected values

        expect_status_registered: Incoming True indicates that the expectation has been registered
        assertion_required: Whether an assertion is required, if any, it will be asserted according to the expectation;
            otherwise, whether the expected result is met will be returned
        '''
        vtap_full_name = None

        if agent_ip == "":
            agent_ip = self.vm_ip

        vtaps_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.query_port
        ) + url.vtaps_list_api_prefix
        vtap_list = requests.get(url=vtaps_url).json()["DATA"]
        for item in vtap_list:
            if item["LAUNCH_SERVER"] == agent_ip:
                log.info(
                    "check_agent_registration_status::item ==> {}"
                    .format(item)
                )
                self.detail = item
                self.boot_time = item[
                    "BOOT_TIME"
                ]  #When the agent is discovered, boot_time is not generated. The later code takes the time point found by the agent as boot_ time

                vtap_full_name = item['NAME']  #
                vtap_lcuuid = item['LCUUID']

                self.setter(
                    vtap_lcuuid=vtap_lcuuid, vtap_full_name=vtap_full_name
                )
                self.config.setter(vtap_lcuuid=vtap_lcuuid)

                log.info(
                    "check_agent_registration_status::vtap_full_name ==> {}"
                    .format(self.vtap_full_name)
                )
                log.info(
                    "check_agent_registration_status::vtap_lcuuid ==> {}"
                    .format(self.vtap_lcuuid)
                )
                log.info(
                    "check_agent_registration_status::boot_time ==> {}".format(
                        self.boot_time
                    )
                )
                log.info(
                    "check_agent_registration_status::detail ==> {}".format(
                        self.detail
                    )
                )
                system_time_now = time.time()
                self.boot_time = system_time_now
                log.info(
                    "check_agent_registration_status::boot_time ==> {}".format(
                        self.boot_time
                    )
                )

        if vtap_full_name:
            is_agent_registered = True
        else:
            is_agent_registered = False

        if assertion_required:
            assert expect_status_registered == is_agent_registered
        else:
            return expect_status_registered == is_agent_registered

    def delete_vtaps_list_by_name(self, vtap_name=None):
        if vtap_name is None:
            vtap_name = self.vtap_full_name
        log.info(
            "delete_vtaps_list_by_name::vtap_name ==> {}".format(vtap_name)
        )
        self.common_utils.delete_vtaps_list_by_name(vtaps_name=vtap_name)
        log.info("delete_vtaps_list_by_name::done")

    def delete_vtaps_list_by_ip(
        self, vtap_mgt_ip, df_mgt_ip, df_server_controller_port
    ):
        if vtap_mgt_ip is None:
            assert False
        log.info(
            "delete_vtaps_list_by_ip::vtap_mgt_ip ==> {}".format(vtap_mgt_ip)
        )
        self.common_utils.delete_vtaps_list_by_ip(vtap_mgt_ip)
        log.info("delete_vtaps_list_by_ip::done")

    def patch_yaml_to_limits_resource_for_k8s(self, cpu=1, mem=130):
        self.linux_cmd.setter(vm_ip=self.vm_ip)
        edit_cpu = """kubectl -n deepflow patch ds deepflow-agent -p '{"spec":{"template":{"spec":{"containers":[{"name": "deepflow-agent", "resources":{"limits":{"cpu":"%s"}}}]}}}}'""" % (
            cpu
        )
        edit_mem = """kubectl -n deepflow patch ds deepflow-agent -p '{"spec":{"template":{"spec":{"containers":[{"name": "deepflow-agent", "resources":{"limits":{"memory":"%sMi"}}}]}}}}'""" % (
            mem
        )
        self.linux_cmd.exec_cmd_except_keyword(cmd=edit_cpu, keyword="patched")
        self.linux_cmd.exec_cmd_except_keyword(cmd=edit_mem, keyword="patched")
        time.sleep(
            30
        )  # After about 30 seconds, the POD can change to the running state. Here, wait for 60 seconds

    def get_agent_boot_time(self, agent_ip="", agent_name=""):
        vtaps_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.query_port
        ) + url.vtaps_list_api_prefix
        log.info("get_agent_boot_time::vtaps_url ==> {}".format(vtaps_url))
        vtap_list = requests.get(url=vtaps_url).json()["DATA"]
        log.info("get_agent_boot_time::vtap_list ==> {}".format(vtap_list))

        agent_boot_time = 0
        for item in vtap_list:
            if item["CTRL_IP"] == agent_ip or item["NAME"] == agent_name:
                agent_boot_time = item["BOOT_TIME"]
                log.info("get_agent_boot_time::detail ==> {}".format(item))
                break

        log.info(
            "get_agent_boot_time::agent_boot_time ==> {}"
            .format(agent_boot_time)
        )
        return agent_boot_time

    def update_agent_boot_time(self, agent_ip="", agent_name=""):
        self.boot_time = self.get_agent_boot_time()
        log.info(
            "update_agent_boot_time::boot_time ==> {}".format(self.boot_time)
        )

    def assert_agent_restarted(self):
        log.info("assert_agent_restarted::vm_ip ==> {}".format(self.vm_ip))
        latest_boot_time = self.get_agent_boot_time(self.vm_ip)
        log.info(
            "assert_agent_restarted::latest_boot_time ==> {}"
            .format(latest_boot_time)
        )
        log.info(
            "assert_agent_restarted::self.boot_time ==> {}".format(
                self.boot_time
            )
        )
        assert latest_boot_time - self.boot_time > 10  # It is assumed that after the agent discovery is completed, it will not go back to restart until at least 10 seconds later

    def delete_history_agent_list_by_ip(self, agent_ip=None):
        '''
        This function deletes the agent according to the incoming IP information.
        That is, if the IP address of any agent is specified by the incoming parameter, it will be deleted

        Parameters:
          agent_ip - It supports the transfer of a single IP or IP list. If not, it defaults to the agent IP

        Returns:
        Raises:
        '''
        if agent_ip is None:  # If this parameter is not transferred, it defaults to the IP address of the agent
            agent_ip_list = [self.vm_ip]
        elif isinstance(
            agent_ip, str
        ):  # If the parameter passed in is a single IP, convert it to a list
            agent_ip_list = [agent_ip]
        elif isinstance(agent_ip, list):
            agent_ip_list = agent_ip
        else:
            log.error(
                "delete_history_agent_list_by_ip::This parameter transfer is not supported temporarily"
            )
            assert False

        vtaps_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.query_port
        ) + url.vtaps_list_api_prefix
        log.info(
            "delete_history_agent_list_by_ip::vtaps_url ==> {}"
            .format(vtaps_url)
        )

        vtap_list = requests.get(url=vtaps_url).json()["DATA"]
        log.info(
            "delete_history_agent_list_by_ip::vtap_list ==> {}"
            .format(vtap_list)
        )

        agent_name_list = []
        for item in vtap_list:
            if item["CTRL_IP"] in agent_ip_list:
                agent_name_list.append(item["NAME"])

        log.info(
            "delete_history_agent_list_by_ip::agent_name_list ==> {}"
            .format(agent_name_list)
        )
        for agent_name in agent_name_list:
            self.delete_vtaps_list_by_name(agent_name)

        log.info("delete_history_agent_list_by_ip::done!")

    def get_all_agent_info_list(self):
        vtaps_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.query_port
        ) + url.vtaps_list_api_prefix
        log.info("get_all_agent_info_list::vtaps_url ==> {}".format(vtaps_url))
        vtap_list = requests.get(url=vtaps_url).json()["DATA"]
        return vtap_list

    def get_all_agent_ip_list(self):
        agent_ip_list = []
        vtap_list = self.get_all_agent_info_list()
        for item in vtap_list:
            ip = item["CTRL_IP"]
            agent_ip_list.append(ip)
        return agent_ip_list

    def get_agent_name_by_ip(self, ip):
        agent_name = ""
        vtap_list = self.get_all_agent_info_list()
        for item in vtap_list:
            if item["CTRL_IP"] == ip:
                agent_name = item["NAME"]
                break
        if agent_name == "":
            log.error("get_agent_name_by_ip::can not get agent_name")

        return agent_name


class Config(object):

    def __init__(
        self, df_mgt_ip, df_server_controller_port, version="community"
    ):
        '''the config of the agent

        use for edit the config of the group

        '''
        self.server_ip = df_mgt_ip
        self.server_port = df_server_controller_port
        self.access_token = None
        self.cpu_threshold = 99
        self.mem_theeshold = 768
        self.default_version = version
        self.vtap_lcuuid = None

        self.agent_group_lcuuid = None
        self.agent_group_name = "autotest_" + str(int(time.time()))
        self.linux_cmd = LinuxCmd()

    def setter(self, **kwargs):
        for key, value in kwargs.items():
            if key == "vtap_lcuuid":
                self.vtap_lcuuid = value

    def get_token(self):
        headers = {'Content-Type': 'application/json'}
        data = {
            "account_type": "deepflow",
            "grant_type": "password",
            "password": "admin",
            "email": "x@yunshan.net.cn",
        }
        data = json.dumps(data)
        url = "http://{}/api/fauths/login".format(self.server_ip),
        print("url", url)
        self.response = requests.post(
            url="http://{}/api/fauths/login".format(self.server_ip),
            headers=headers,
            data=data,
        )
        self.response_json = self.response.json()
        if self.response_json["OPT_STATUS"] == "SUCCESS":
            self.access_token = self.response_json["DATA"]["access_token"]

    def add_group_with_exist_agent(self, group_name="", vtap_lcuuid=""):
        '''Move the agent to the specified group
        return: LCUUID
        '''
        log.info(
            "add_group_with_exist_agent::vtap_lcuuid ==> {}"
            .format(vtap_lcuuid)
        )

        headers = {'Content-Type': 'application/json'}
        if self.default_version != "community":
            headers.update({"Authorization": "Bearer " + self.access_token})
        # url = "http://{}/api/deepflow-server/v1/vtap-groups/".format(self.server_ip)  # this url is for close source
        url = "http://{}:{}/v1/vtap-groups/".format(
            self.server_ip, self.server_port
        )
        data = {"NAME": "{}".format(group_name), "VTAP_LCUUIDS": [vtap_lcuuid]}
        log.info("add_group_with_exist_agent::data ==> {}".format(data))
        data = json.dumps(data)
        self.response = requests.post(
            url=url,
            headers=headers,
            data=data,
        )
        self.response_json = self.response.json()
        log.info(
            "add_group_with_exist_agent::response_json ==> {}".format(
                self.response_json
            )
        )
        self.agent_group_lcuuid = self.response_json["DATA"]["LCUUID"]
        log.info(
            "add_group_with_exist_agent::agent_group_lcuuid ==> {}".format(
                self.agent_group_lcuuid
            )
        )
        response_status = self.response_json["OPT_STATUS"]
        if response_status == "SUCCESS":
            self.lcuuid = self.response_json["DATA"]["LCUUID"]
        else:
            assert False

    def try_delete_group_config(self, agent_group_config_name="default"):
        self.linux_cmd.setter(vm_ip=self.server_ip)
        try:
            cmd = """deepflow-ctl agent-group-config delete $(deepflow-ctl agent-group-config list | grep %s | awk 'NR==1{print $2}')""" % (
                agent_group_config_name
            )
            log.info("try_delete_group_config::cmd ==> {}".format(cmd))
            self.linux_cmd.exec_cmd(cmd)

        except Exception as e:
            log.error(f"try_delete_group_config error: {e}")

    def try_delete_agent_group(self, agent_group_name="default"):
        self.linux_cmd.setter(vm_ip=self.server_ip)
        try:
            cmd = """deepflow-ctl agent-group delete %s""" % agent_group_name
            log.info("try_delete_agent_group::cmd ==> {}".format(cmd))
            self.linux_cmd.exec_cmd(cmd)

        except Exception as e:
            log.error(f"try_delete_agent_group::error ==> {e}")

    def create_group_config(
        self, agent_group_id, filename: str,
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default
    ):
        ssh = ssh_pool.get(self.server_ip, ssh_port, username, password)
        scpclient = SCPClient(ssh.get_transport(), socket_timeout=15.0)
        scpclient.put(
            "/root/df-test/common/tool/files/agent_group_config.yaml",
            f"/root/{filename}"
        )
        cmd = f"sed -i 's/vtap_group_id:/vtap_group_id: {agent_group_id}/g' {filename} && deepflow-ctl agent-group-config create -f {filename}"
        _, stdout, stderr = ssh.exec_command(cmd)
        log.info(
            f"create group config exec cmd ==> {cmd} output: {stdout.readlines()}"
        )
        err = stderr.readlines()
        if err:
            log.error(err)
            assert False
        time.sleep(120)

    def add_advanced_group_config(
        self, agent_group_name, config="",
        username=common_config.ssh_username_default,
        password=common_config.ssh_password_default,
        ssh_port=common_config.ssh_port_default
    ):
        filename = f"{agent_group_name}.yaml"
        ssh = ssh_pool.get(self.server_ip, ssh_port, username, password)
        cmd = "deepflow-ctl agent-group list |  grep %s | awk 'NR==1{print $2}'" % (
            agent_group_name
        )
        _, stdout, stderr = ssh.exec_command(cmd)
        agent_group_id = stdout.readlines()
        if not agent_group_id:
            assert False
        agent_group_id = agent_group_id[0].replace("\n", "")
        cmd = "deepflow-ctl agent-group-config list | grep %s | awk 'NR==1{print $2}'" % (
            agent_group_name
        )
        _, stdout, stderr = ssh.exec_command(cmd)
        agent_group_config_id = stdout.readlines()
        if not agent_group_config_id:
            self.create_group_config(agent_group_id, filename)
        if config:
            cmd = "deepflow-ctl agent-group-config list %s -o yaml > %s && sed -i '$a %s' %s && deepflow-ctl agent-group-config update -f %s" % (
                agent_group_id, filename, config, filename, filename
            )
            log.info(f"add advenced group config exec cmd ==> {cmd}")
            _, stdout, stderr = ssh.exec_command(cmd)
            err = stderr.readlines()
            if err:
                log.error(err)
                assert False
            log.info(stdout.readlines())
        cmd = "deepflow-ctl agent-group-config list %s -o yaml" % (
            agent_group_id
        )
        _, stdout, stderr = ssh.exec_command(cmd)
        group_config = stdout.readlines()
        log.info(f"vtap advance group config: {group_config}")
        return

    def set_group_config(self, agent_group_lcuuid=None, **kwargs):
        '''edit the config of the group
        If we need to modify the resource limit of the agent, we need to move the agent into a group first
        '''

        if agent_group_lcuuid is None:
            agent_group_lcuuid = self.agent_group_lcuuid

        headers = {'Content-Type': 'application/json'}
        if self.default_version != "community":
            headers.update({"Authorization": "Bearer " + self.access_token})

        null = None
        data = {
            "VTAP_GROUP_LCUUID": agent_group_lcuuid,
            "MAX_MEMORY": null,
            "SYS_FREE_MEMORY_LIMIT": null,
            "MAX_CPUS": null,
            "MAX_NPB_BPS": null,
            "MAX_COLLECT_PPS": null,
            "BANDWIDTH_PROBE_INTERVAL": null,
            "MAX_TX_BANDWIDTH": null,
            "LOG_THRESHOLD": null,
            "LOG_LEVEL": null,
            "LOG_FILE_SIZE": null,
            "THREAD_THRESHOLD": null,
            "PROCESS_THRESHOLD": null,
            "TAP_INTERFACE_REGEX": ".*",
            "CAPTURE_BPF": null,
            "CAPTURE_PACKET_SIZE": null,
            "CAPTURE_SOCKET_TYPE": null,
            "DECAP_TYPE": [2],
            "IF_MAC_SOURCE": null,
            "VM_XML_PATH": null,
            "SYNC_INTERVAL": null,
            "MAX_ESCAPE_SECONDS": null,
            "MTU": null,
            "OUTPUT_VLAN": null,
            "NAT_IP_ENABLED": null,
            "LOG_RETENTION": null,
            "PROXY_CONTROLLER_PORT": null,
            "ANALYZER_PORT": null,
            "COLLECTOR_SOCKET_TYPE": null,
            "COMPRESSOR_SOCKET_TYPE": null,
            "HTTP_LOG_PROXY_CLIENT": null,
            "HTTP_LOG_TRACE_ID": null,
            "HTTP_LOG_SPAN_ID": null,
            "HTTP_LOG_X_REQUEST_ID": null,
            "L7_LOG_PACKET_SIZE": null,
            "L4_LOG_COLLECT_NPS_THRESHOLD": null,
            "L7_LOG_COLLECT_NPS_THRESHOLD": null,
            "NPB_SOCKET_TYPE": null,
            "NPB_VLAN_MODE": null,
            "PLATFORM_ENABLED": null,
            "RSYSLOG_ENABLED": null,
            "NTP_ENABLED": null,
            "DOMAINS": [],
            "POD_CLUSTER_INTERNAL_IP": null,
            "COLLECTOR_ENABLED": null,
            "INACTIVE_SERVER_PORT_ENABLED": null,
            "INACTIVE_IP_ENABLED": null,
            "L4_PERFORMANCE_ENABLED": null,
            "L7_METRICS_ENABLED": null,
            "VTAP_FLOW_1S_ENABLED": null,
            "L4_LOG_TAP_TYPES": [],
            "L7_LOG_STORE_TAP_TYPES": [],
            "EXTERNAL_AGENT_HTTP_PROXY_ENABLED": null,
            "EXTERNAL_AGENT_HTTP_PROXY_PORT": null,
            "NPB_DEDUP_ENABLED": null
        }

        log.info("================================")
        log.info(kwargs)
        for key, value in kwargs.items():
            if key.upper() in data.keys():
                data_key = key.upper()
                log.info("+++++++++++++++++++++++++")
                log.info(data_key)
                data[data_key] = value

            # update resource threshold
            if key.upper() == "MAX_CPUS":
                self.cpu_threshold = value
            elif key.upper() == "MAX_MEMORY":
                self.mem_threshold = value
            else:
                pass

        data = json.dumps(data)
        url = "http://{}:{}/v1/vtap-group-configuration/".format(
            self.server_ip, self.server_port
        )
        log.info("set_group_config::url ==> {}".format(url))
        log.info("set_group_config::headers ==> {}".format(headers))
        log.info("set_group_config::data ==> {}".format(data))
        self.response = requests.post(
            url=url,
            headers=headers,
            data=data,
        )
        self.response_json = self.response.json()
        log.info(
            "set_group_config::response_json ==> {}".format(
                self.response_json
            )
        )
        response_status = self.response_json["OPT_STATUS"]
        response_description = self.response_json["DESCRIPTION"]
        if 'exist' in response_description:
            return
        if response_status != "SUCCESS":
            assert False


class Group(object):

    def __init__(self, df_mgt_ip, df_server_controller_port):
        self.linux_cmd = LinuxCmd()
        self.agent_group_name = None
        self.agent_group_uuid = None
        self.df_mgt_ip = df_mgt_ip
        self.df_server_controller_port = df_server_controller_port

    def setter(self, **kwargs):
        for key, value in kwargs.items():
            if key == "agent_group_name":
                self.agent_group_name = value
            else:
                log.error(
                    "Currently, no other keys are supported. There may be a serious error ==> {}"
                    .format(key)
                )

    def delete_agent_group_by_name(self, name=None):
        if name is None:
            name = self.agent_group_name
        self.linux_cmd.setter(vm_ip=self.df_mgt_ip)
        self.linux_cmd.exec_cmd_except_keyword(
            cmd="deepflow-ctl agent-group delete {}".format(name)
        )
        log.info("delete_agent_group_by_name::done")

    def get_all_agent_group_list(self):
        get_vtap_url = url.protocol + self.df_mgt_ip + ':' + str(
            self.df_server_controller_port
        ) + url.vtaps_group_list_api_prefix
        log.info(
            "get_all_agent_group_list::get_vtap_url ==> {}"
            .format(get_vtap_url)
        )
        # get_vtap_url = 'http://10.1.19.240:30417/v1/vtap-groups/'
        res = requests.get(url=get_vtap_url)
        if res.status_code == 200:
            agent_group_list = res.json()['DATA']
            log.info(
                "get_all_agent_group_list::agent_group_list ==> {}"
                .format(agent_group_list)
            )
            return agent_group_list
        else:
            log.error("get_all_agent_group_list::get agent group failed!")

    def get_agent_group_lcuuid_by_name(self, agent_group_name="default"):
        agent_group_list = self.get_all_agent_group_list()
        agent_group_lcuuid = None
        for item in agent_group_list:
            if item["NAME"] == agent_group_name:
                log.info(
                    "get_agent_group_lcuuid_by_name::item ==> {}".format(item)
                )
                agent_group_lcuuid = item["LCUUID"]
                log.info(
                    "get_agent_group_uuid_by_name::agent_group_uuid ==> {}"
                    .format(agent_group_lcuuid)
                )
                break
        if agent_group_lcuuid:
            return agent_group_lcuuid
        else:
            assert agent_group_lcuuid

    def update_agent_group_according_name(self, agent_group_name="default"):
        self.agent_group_lcuuid = self.get_agent_group_lcuuid_by_name(
            agent_group_name=agent_group_name
        )
        log.info(
            "update_agent_group_according_name::agent_group_lcuuid ==> {}"
            .format(self.agent_group_lcuuid)
        )


class Summary(object):

    def __init__(self):
        pass

    def get_agent_start_time(self, agent_name):
        pass
