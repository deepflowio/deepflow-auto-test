# coding: utf-8
"""
author: danqing
date: 2022-09-16
desc: 兼容性测试中常用的方法
"""

import requests
import paramiko
import re
import time
from common import logger
from common import common_config
from common import url
from common.ssh import ssh_pool

log = logger.getLogger()


def get_vtaps_list_info(df_mgt_ip):
    '''Get information of the vtaps by API, parameter:
    df_mgt_ip; optional, The ip of DeepFlow
    '''
    vtaps_list_url = url.protocol + df_mgt_ip + ':' + str(
        common_config.df_ce_api_port
    ) + url.vtaps_list_api_prefix
    res = requests.get(url=vtaps_list_url)
    log.info(f"get vtaps list info:{res.json()}")
    if res.status_code == 200:
        json_str = res.json()
        return json_str['DATA']
    else:
        return []


def loop_check_vtaps_list_info(
    df_mgt_ip, count, vtaps_data, vtaps_content, vtaps_value
):
    '''Check if vtaps_data[vtaps_value] contains vtaps_content on Deepflow by API
         count: the the number of checks
         df_mgt_ip: the ip of Deepflow
         '''
    res = False
    for i in range(count):
        log.info('Waiting for resource sync, about 10s')
        time.sleep(10)
        vtaps_info = vtaps_data(df_mgt_ip)
        if not vtaps_info:
            log.error("get vtaps info error")
            continue
        for k in vtaps_info:
            if vtaps_content in k['{}'.format(vtaps_value)]:
                res = True
                break
        if res == True:
            log.info(
                'new vtap in deepflow, vtap name is {}'.format(vtaps_content)
            )
            break
    assert res


def vtaps_install_deepflow_agent_lastest_rpm(
    vtaps_mgt_ip, df_mgt_ip, username=common_config.ssh_username_default,
    password=common_config.ssh_password_default,
    ssh_port=common_config.ssh_port_default, system_platform='linux',
    cluster_id=''
):
    '''Login to the vtaps by SSH,Deploy and start the latest version of deepflow-agent. parameter:
    vtaps_mgt_ip; The ip of vtaps
    username; login username
    password; login password
    ssh_port; port
    '''
    ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
    stdin, stdout, stderr = ssh.exec_command(
        '''cat /dev/null > /etc/resolv.conf && echo "nameserver %s" > /etc/resolv.conf && cat /etc/issue '''
        % (common_config.ali_dns_ip)
    )
    system_version = stdout.readlines()[0]
    if system_platform == 'linux' and '\S' in system_version:
        stdin, stdout, stderr = ssh.exec_command(
            '''curl -O %s &&\
                                                 curl -O http://nexus.yunshan.net/repository/tools/automation/offline/unzip/unzip-6.0-24.el7_9.x86_64.rpm &&\
                                                 rpm -ivh unzip-6.0-24.el7_9.x86_64.rpm &&\
                                                 unzip deepflow-agent-rpm.zip &&\
                                                 rpm -ivh x86_64/deepflow-agent-1*.rpm &&\
                                                 sed -i 's/  - 127.0.0.1/  - %s/g' /etc/deepflow-agent.yaml &&\
                                                 systemctl restart deepflow-agent && systemctl status deepflow-agent'''
            % (common_config.deepflow_agent_rpm_lastest_url, df_mgt_ip)
        )
        if bool(
            re.search('active \(running\)', "".join(stdout.readlines()))
        ) == True:
            log.info(
                'centos7 deployed deepflow-agent successfully and running normally, vtap ip addres is {}'
                .format(vtaps_mgt_ip)
            )
            #ssh.close()
        else:
            log.error(
                'centos7 failed to deploy deepflow-agent, vtap ip addr is {}'
                .format(vtaps_mgt_ip)
            )
            #ssh.close()
            assert False
    elif system_platform == 'linux' and 'Ubuntu' in system_version and int(
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
            % (common_config.deepflow_agent_deb_lastest_url, df_mgt_ip)
        )
        if bool(
            re.search(
                'deepflow-agent start/running', "".join(stdout.readlines())
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
    elif system_platform == 'linux' and 'Ubuntu' in system_version and int(
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
            % (common_config.deepflow_agent_deb_lastest_url, df_mgt_ip)
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
    elif system_platform == 'linux' and 'Debian' in system_version:
        print(system_version)
        stdin, stdout, stderr = ssh.exec_command(
            '''curl -O %s &&\
                                                    curl -O http://nexus.yunshan.net/repository/tools/automation/offline/unzip/unzip_6.0-9ubuntu1.5_amd64.deb &&\
                                                    dpkg -i unzip_6.0-9ubuntu1.5_amd64.deb &&\
                                                    unzip deepflow-agent-deb.zip &&\
                                                    dpkg -i x86_64/deepflow-agent-*.systemd.deb &&\
                                                    sed -i 's/  - 127.0.0.1/  - %s/g' /etc/deepflow-agent.yaml  &&\
                                                    systemctl restart deepflow-agent && systemctl status deepflow-agent'''
            % (common_config.deepflow_agent_deb_lastest_url, df_mgt_ip)
        )
        if bool(
            re.search('active \(running\)', "".join(stdout.readlines()))
        ) == True:
            log.info(
                '{} deployed deepflow-agent successfully and running normally, vtap ip addr is {}'
                .format(
                    system_version.split(' ')[0] +
                    system_version.split(' ')[2], vtaps_mgt_ip
                )
            )
            print(
                '{} deployed deepflow-agent successfully and running normally, vtap ip addr is {}'
                .format(
                    system_version.split(' ')[0] +
                    system_version.split(' ')[2], vtaps_mgt_ip
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
            print(
                '{} failed to deploy deepflow-agent, vtap ip addr is {}'
                .format(
                    system_version.split(' ')[0] +
                    system_version.split(' ')[1], vtaps_mgt_ip
                )
            )
            #ssh.close()
            assert False
    elif system_platform == 'arm':
        stdin, stdout, stderr = ssh.exec_command(
            '''curl -O https://deepflow-ce.oss-cn-beijing.aliyuncs.com/rpm/agent/latest/linux/$(arch | sed 's|x86_64|amd64|' | sed 's|aarch64|arm64|')/deepflow-agent-rpm.zip &&\
                                                    unzip deepflow-agent*.zip &&\
                                                    rpm -ivh aarch64/deepflow-agent-1*.rpm &&\
                                                    sed -i 's/  - 127.0.0.1/  - %s/g' /etc/deepflow-agent.yaml &&\
                                                    systemctl restart deepflow-agent && systemctl status deepflow-agent
                                                    ''' % (df_mgt_ip)
        )
        if bool(
            re.search('active \(running\)', "".join(stdout.readlines()))
        ) == True:
            log.info(
                'arm deployed deepflow-agent successfully and running normally, vtap ip addr is {}'
                .format(vtaps_mgt_ip)
            )
            #ssh.close()
        else:
            log.error(
                'arm failed to deploy deepflow-agent, vtap ip addr is {}'
                .format(vtaps_mgt_ip)
            )
            #ssh.close()
            assert False


def check_vtaps_deepflow_agent_logs(
    vtaps_mgt_ip, username=common_config.ssh_username_default,
    password=common_config.ssh_password_default,
    ssh_port=common_config.ssh_port_default, system_platform='linux'
):
    '''Login to the vtaps by SSH,View See if the deepflow-agent log contains ERRO or WARN information.parameter:
    vtaps_mgt_ip; The ip of vtaps
    username; login username
    password; login password
    ssh_port; port
    '''
    logs = list()
    ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
    warn_stdin, warn_stdout, warn_stderr = ssh.exec_command(
        'cat /var/log/deepflow-agent/deepflow-agent.log|grep WARN'
    )
    err_stdin, err_stdout, err_stderr = ssh.exec_command(
        'cat /var/log/deepflow-agent/deepflow-agent.log|grep ERR'
    )
    warn_log = warn_stdout.readlines()
    error_log = err_stdout.readlines()
    if not warn_log and not error_log:
        log.info('vtap deepflow-agent logs no warn and error')
        return
    else:
        if not error_log:
            for warn in warn_log:
                if 'The core file is configured with pipeline operation, failed to check.' in warn:
                    return
        log.error(
            'vtap deepflow-agent logs has warn or error, log info is {} {}'
            .format(warn_log, error_log)
        )
        assert False


def vtaps_send_icmp_flow(
    vtaps_mgt_ip, dst_ip, username=common_config.ssh_username_default,
    password=common_config.ssh_password_default,
    ssh_port=common_config.ssh_port_default, pack_count=5
):
    '''Login to the vtaps by SSH,vtaps sends ICMP flow.parameter:
    vtaps_mgt_ip; The ip of vtaps
    username; login username
    password; login password
    ssh_port; port
    dst_ip: Object ip to which ICMP flow is sent
    '''
    log.info('Wait for flow statistics to complete,about 60s')
    time.sleep(60)
    ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
    stdin, stdout, stderr = ssh.exec_command(
        'ping -c {} {}'.format(pack_count, dst_ip)
    )
    if '0% packet loss' in stdout.readlines()[-2]:
        log.info(
            'vtap send icmp successfully, vtap ip is {}'.format(vtaps_mgt_ip)
        )
    else:
        log.error('vtap send icmp failed, vtap ip is {}'.format(vtaps_mgt_ip))


def check_vtaps_deepflow_agent_flow(
    df_mgt_ip, vtaps_mgt_ip, username=common_config.ssh_username_default,
    password=common_config.ssh_password_default,
    ssh_port=common_config.ssh_port_default, system_platform='linux'
):
    '''Login to the vtaps by SSH,View deepflow-agent flow information.parameter:
    vtaps_mgt_ip; The ip of vtaps
    username; login username
    password; login password
    ssh_port; port
    '''
    if system_platform == 'linux':
        ssh = ssh_pool.get(df_mgt_ip, ssh_port, username, password)
        stdin, stdout, stderr = ssh.exec_command(
            'kubectl get pods -n deepflow -o wide|grep server'
        )
        deepflow_server_ip = re.search(
            r'(([01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])\.){3}([01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])',
            str(stdout.readlines()[0])
        ).group()
        stdin, stdout, stderr = ssh.exec_command(
            'deepflow-ctl -i {} ingester metrics adapter all|grep {}'.format(
                deepflow_server_ip, vtaps_mgt_ip
            )
        )
        logs = stdout.readlines()
        if logs != []:
            log.info(
                'vtap receives flow normally, vtap ip is {}'
                .format(vtaps_mgt_ip)
            )
        else:
            log.error(
                'vtap receives flow abnormality, vtap ip is {}'
                .format(vtaps_mgt_ip)
            )


def workload_v_force_kill_agent_action(
    vtaps_mgt_ip, username=common_config.ssh_username_default,
    password=common_config.ssh_password_default,
    ssh_port=common_config.ssh_port_default
):
    ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
    for i in range(3):
        try:
            cmd = 'ps -ef|grep deepflow-agent|grep -v pts/0'
            log.info(f"exec cmd {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            curr_agent_id = re.search(r'\d+', stdout.readlines()[0]).group()
            log.info('deepflow-agent current id:{}'.format(curr_agent_id))
            stdin, stdout, stderr = ssh.exec_command(
                'kill -9 {}'.format(curr_agent_id)
            )
            logs = stdout.readlines()
            log.info(
                f'wait deepflow-agent{vtaps_mgt_ip} auto-restart, about 10s'
            )
            time.sleep(11)
            stdin, stdout, stderr = ssh.exec_command(
                'ps -ef|grep deepflow-agent|grep -v pts/0'
            )
            new_agent_id = re.search(r'\d+', stdout.readlines()[0]).group()
            log.info('deepflow-agent new id:{}'.format(new_agent_id))
            if new_agent_id is not None and curr_agent_id != new_agent_id:
                log.info(
                    f'deepflow-agent{vtaps_mgt_ip} force restart successfully'
                )
                break
            #ssh.close()
        except Exception as err:
            log.error(
                'deepflow-agent force restart failed, log info is {}'
                .format(err)
            )


# if __name__ == '__main__':
#     workload_v_force_kill_agent_action(vtaps_mgt_ip='10.1.19.11')
