# coding: utf-8

import paramiko
import requests
import logging
from urllib.parse import urlencode
from common import common_config
from common.utils import CommonUtils
from common.ssh import ssh_pool
from scp import SCPClient


def upload_tools(
    vm_ip, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(vm_ip, ssh_port, username, password)
    scpclient = SCPClient(ssh.get_transport(), socket_timeout=15.0)
    scpclient.put("/root/df-test/case/performance/tools/udp_flood", f"/root/")


def init_high_concuerrency_server(
    vm_ip, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(vm_ip, ssh_port, username, password)
    scpclient = SCPClient(ssh.get_transport(), socket_timeout=15.0)
    scpclient.put("/root/df-test/case/performance/tools/tcpclient", f"/root/")
    scpclient.put("/root/df-test/case/performance/tools/tcpserver", f"/root/")
    cmds = [
        "echo 10000 > /proc/sys/net/core/somaxconn",
        "echo 1 > /proc/sys/net/ipv4/tcp_tw_reuse",
        "echo 0 > /proc/sys/net/ipv4/tcp_syncookies",
        "ip addr add dev lo 192.168.10.100/24",
        "ip addr add dev lo 192.168.10.101/24",
        "ip addr add dev lo 192.168.10.102/24",
        "ip addr add dev lo 192.168.10.103/24",
        "ip addr add dev lo 192.168.10.104/24",
        "ip addr add dev lo 192.168.10.105/24",
    ]
    for cmd in cmds:
        logging.info(f"exec cmd {cmd}")
        _, _, stderr = ssh.exec_command(cmd)
        err = stderr.readlines()
        if err:
            logging.error(err)
            assert False
    ssh.exec_command("ulimit -n 400000 && ./tcpserver > tcpserver.log &")


def get_agent_commit_id(
    vm_ip, is_pod=True, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    if is_pod:
        cmd = "kubectl exec -it $(kubectl get pod -n deepflow|grep agent|awk '{print $1}') -n deepflow -- deepflow-agent -v|grep CommitId| awk '{print $2}'"
    else:
        cmd = "deepflow-agent -v|grep CommitId| awk '{print $2}'"
    logging.info(f"exec get_agent_commit_id: {cmd}")
    ssh = ssh_pool.get(vm_ip, ssh_port, username, password)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    res = stdout.readlines()
    logging.info(res)
    if not res:
        err = stderr.readlines()
        logging.error(f"get commit id error: {err}")
        return ""
    return res[-1].strip('\n')[:8]


def create_udp_performance_pods(
    vtaps_mgt_ip, username=common_config.ssh_username_default,
    password=common_config.ssh_password_default,
    ssh_port=common_config.ssh_port_default
):
    '''Login to the vtaps by SSH,create pod for UDP performance
    '''
    ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
    cmds = [
        f"cat /dev/null > /etc/resolv.conf && echo 'nameserver {common_config.ali_dns_ip}' >> /etc/resolv.conf",
        "curl -O http://nexus.yunshan.net/repository/tools/automation/performance/performance_client.yaml",
        "curl -O http://nexus.yunshan.net/repository/tools/automation/performance/performance_server.yaml",
        "sed -i 's/image: performance:lastest/image: dfcloud-image-registry.cn-beijing.cr.aliyuncs.com\/public\/agent_performance_test:latest/g' performance_client.yaml",
        "sed -i 's/image: performance:lastest/image: dfcloud-image-registry.cn-beijing.cr.aliyuncs.com\/public\/agent_performance_test:latest/g' performance_server.yaml",
        "kubectl apply -f performance_client.yaml && kubectl apply -f performance_server.yaml",
        "sleep 60"
    ]
    cmd = " && ".join(cmds)
    logging.info(cmd)
    strin, stdout, stderr = ssh.exec_command(cmd)
    err = stderr.readlines()
    if err:
        logging.error(err)
    logs = stdout.readlines()
    logging.info(logs)
    pod_client_name = ''
    pod_client_ip = ''
    pod_server_name = ''
    pod_server_ip = ''
    stdin, stdout, stderr = ssh.exec_command(
        'kubectl get pods -o wide|grep client'
    )
    client_logs = stdout.readlines()
    for i in client_logs:
        pod_client_name = i.split(' ')[0]
        pod_client_ip = i.split(' ')[24]
    stdin, stdout, stderr = ssh.exec_command(
        'kubectl get pods -o wide|grep server'
    )
    server_logs = stdout.readlines()
    for i in server_logs:
        pod_server_name = i.split(' ')[0]
        pod_server_ip = i.split(' ')[24]
    return pod_client_name, pod_client_ip, pod_server_name, pod_server_ip


def create_performance_pods(
    vtaps_mgt_ip, username=common_config.ssh_username_default,
    password=common_config.ssh_password_default,
    ssh_port=common_config.ssh_port_default
):
    '''Login to the vtaps by SSH,create pod for TCP performance
    '''
    ssh = ssh_pool.get(vtaps_mgt_ip, ssh_port, username, password)
    cmd = '''cat /dev/null > /etc/resolv.conf &&\
                                              echo 'nameserver %s' >> /etc/resolv.conf && \
                                              curl -O http://nexus.yunshan.net/repository/tools/automation/performance/performance_v1.tar && \
                                              curl -O http://nexus.yunshan.net/repository/tools/automation/performance/performance_client.yaml && \
                                              curl -O http://nexus.yunshan.net/repository/tools/automation/performance/performance_server.yaml && \
                                              nerdctl -n k8s.io load -i performance_v1.tar && \
                                              nerdctl -n k8s.io tag $(nerdctl -n k8s.io image list|grep overlayfs|awk -F ' ' '{print $3}') performance:lastest && \
                                              kubectl apply -f performance_client.yaml && kubectl apply -f performance_server.yaml &&\
                                              sleep 60''' % (
        common_config.ali_dns_ip
    )
    strin, stdout, stderr = ssh.exec_command(cmd)
    err = stderr.readlines()
    if err:
        logging.error(err)
    logs = stdout.readlines()
    logging.info(logs)
    pod_client_name = ''
    pod_client_ip = ''
    pod_server_name = ''
    pod_server_ip = ''
    stdin, stdout, stderr = ssh.exec_command(
        'kubectl get pods -o wide|grep client'
    )
    client_logs = stdout.readlines()
    for i in client_logs:
        pod_client_name = i.split(' ')[0]
        pod_client_ip = i.split(' ')[24]
    stdin, stdout, stderr = ssh.exec_command(
        'kubectl get pods -o wide|grep server'
    )
    server_logs = stdout.readlines()
    for i in server_logs:
        pod_server_name = i.split(' ')[0]
        pod_server_ip = i.split(' ')[24]
    return pod_client_name, pod_client_ip, pod_server_name, pod_server_ip


def get_vtaps_max_cpu_usage(
    query_port, vtaps_name, start_time, end_time, df_mgt_ip
):
    '''Maximum CPU usage of the agent on DF by API. Parameter description:
    query_port; required field, Query the port of the interface
    vtaps_name; required field, Name of vtaps
    start_time; required field, Start time for filtering data
    end_time; required field, End time for filtering data
    df_mgt_ip; required field, The ip of DF
    '''
    max_cpu_list = list()
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    sql = '''select Max(`metrics.cpu_percent`) AS RSS, `tag.host` from \
            deepflow_agent_monitor where `tag.host` IN ('%s') AND time>=%s \
            AND time<=%s group by `tag.host` limit 100''' % (
        vtaps_name, start_time, end_time
    )
    data = {'db': 'deepflow_system', 'sql': sql}
    data = urlencode(data, encoding='gb2312')
    res = requests.post(
        url='http://%s:%s/v1/query/' % (df_mgt_ip, query_port),
        headers=headers, data=data
    )
    logging.info(f"get_vtaps_max_cpu_usage:: sql:{sql} res: {res.content}")
    if res.json()['result'] is None:
        assert False
    if res.json()['result']['values'] is None:
        assert False
    for i in res.json()['result']['values']:
        max_cpu_list.append(i[-1])
    # print(max(max_cpu_list))
    return max(max_cpu_list)


def get_vtaps_max_mem_usage(
    query_port, vtaps_name, start_time, end_time, df_mgt_ip
):
    '''Maximum memory usage of the agent on DF by API. Parameter description:
    query_port; required field, Query the port of the interface
    vtaps_name; required field, Name of vtaps
    start_time; required field, Start time for filtering data
    end_time; required field, End time for filtering data
    df_mgt_ip; required field, The ip of DF
    '''
    max_mem_list = list()
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    sql = '''select Max(`metrics.memory`) AS RSS, `tag.host` from \
            deepflow_agent_monitor where `tag.host` IN ('%s') AND time>=%s \
            AND time<=%s group by `tag.host` limit 100''' % (
        vtaps_name, start_time, end_time
    )
    data = {'db': 'deepflow_system', 'sql': sql}
    data = urlencode(data, encoding='gb2312')
    res = requests.post(
        url='http://%s:%s/v1/query/' % (df_mgt_ip, query_port),
        headers=headers, data=data
    )
    logging.info(f"get_vtaps_max_cpu_usage:: sql:{sql} res: {res.content}")
    for i in res.json()['result']['values']:
        max_mem_list.append(i[-1])
    # print(max(max_mem_list))
    return max(max_mem_list)


def get_vtaps_max_dispatcher_bps(
    query_port, vtaps_name, start_time, end_time, df_mgt_ip
):
    '''Maximum BPS of the agent on DF by API. Parameter description:
    query_port; required field, Query the port of the interface
    vtaps_name; required field, Name of vtaps
    start_time; required field, Start time for filtering data
    end_time; required field, End time for filtering data
    df_mgt_ip; required field, The ip of DF
    '''
    max_dispatcher_bps = list()
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    sql = '''select (Sum(`metrics.rx_bytes`)*8/60) AS rx_bytes,time(time, 60) AS time_interval,`tag.host` from \
            deepflow_agent_dispatcher where `tag.host` IN ('%s') AND time>=%s \
            AND time<=%s group by time_interval,`tag.host` limit 100''' % (
        vtaps_name, start_time, end_time
    )
    data = {'db': 'deepflow_system', 'sql': sql}
    data = urlencode(data, encoding='gb2312')
    res = requests.post(
        url='http://%s:%s/v1/query/' % (df_mgt_ip, query_port),
        headers=headers, data=data
    )
    logging.info(
        f"get_vtaps_max_dispatcher_bps:: sql:{sql} res: {res.content}"
    )
    for i in res.json()['result']['values']:
        max_dispatcher_bps.append(i[-1])
    # print(max(max_dispatcher_bps))
    return max(max_dispatcher_bps)


def get_vtaps_max_dispatcher_pps(
    query_port, vtaps_name, start_time, end_time, df_mgt_ip
):
    '''Maximum PPS of the agent on DF by API. Parameter description:
    query_port; required field, Query the port of the interface
    vtaps_name; required field, Name of vtaps
    start_time; required field, Start time for filtering data
    end_time; required field, End time for filtering data
    df_mgt_ip; required field, The ip of DF
    '''
    max_dispatcher_pps = list()
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    sql = '''select (Sum(`metrics.rx`)/60) AS rx,time(time, 60) AS time_interval,`tag.host` from \
                deepflow_agent_dispatcher where `tag.host` IN ('%s') AND time>=%s \
                AND time<=%s group by time_interval,`tag.host` limit 100''' % (
        vtaps_name, start_time, end_time
    )
    data = {'db': 'deepflow_system', 'sql': sql}
    data = urlencode(data, encoding='gb2312')
    res = requests.post(
        url='http://%s:%s/v1/query/' % (df_mgt_ip, query_port),
        headers=headers, data=data
    )
    logging.info(
        f"get_vtaps_max_dispatcher_pps:: sql:{sql} res: {res.content}"
    )
    for i in res.json()['result']['values']:
        max_dispatcher_pps.append(i[-1])
    # print(max(max_dispatcher_pps))
    return max(max_dispatcher_pps)


def get_vtaps_max_drop_pack(
    query_port, vtaps_name, start_time, end_time, df_mgt_ip
):
    '''Maximum drop-pack of the agent on DF by API. Parameter description:
    query_port; required field, Query the port of the interface
    vtaps_name; required field, Name of vtaps
    start_time; required field, Start time for filtering data
    end_time; required field, End time for filtering data
    df_mgt_ip; required field, The ip of DF
    '''
    drop_pack = list()
    query_url = 'http://%s:%s/v1/query/' % (df_mgt_ip, query_port)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    sql = '''select Max(`metrics.kernel_drops`) AS drops,`tag.host` from \
                deepflow_agent_dispatcher where `tag.host` IN ('%s') AND time>=%s \
                AND time<=%s group by `tag.host` limit 100''' % (
        vtaps_name, start_time, end_time
    )
    data = {'db': 'deepflow_system', 'sql': sql}
    data = urlencode(data, encoding='gb2312')
    res = requests.post(url=query_url, headers=headers, data=data)
    logging.info(f"get_vtaps_max_drop_pack:: sql:{sql} res: {res.content}")
    for i in res.json()['result']['values']:
        drop_pack.append(i[-1])
    # print(max(drop_pack))
    return max(drop_pack)


def get_vtaps_max_concuerrent(
    query_port, vtaps_name, start_time, end_time, df_mgt_ip
):
    '''Maximum number of agent concurrent connections on DF by API. Parameter description:
    query_port; required field, Query the port of the interface
    vtaps_name; required field, Name of vtaps
    start_time; required field, Start time for filtering data
    end_time; required field, End time for filtering data
    df_mgt_ip; required field, The ip of DF
    '''
    concurrent = list()
    query_url = 'http://%s:%s/v1/query/' % (df_mgt_ip, query_port)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    sql = '''select Max(`metrics.concurrent`) AS concurrent,`tag.host` from \
                deepflow_agent_flow_map where `tag.host` IN ('%s') AND time>=%s \
                AND time<=%s group by `tag.host` limit 100''' % (
        vtaps_name, start_time, end_time
    )
    data = {'db': 'deepflow_system', 'sql': sql}
    data = urlencode(data, encoding='gb2312')
    res = requests.post(url=query_url, headers=headers, data=data)
    logging.info(f"get_vtaps_max_drop_pack:: sql:{sql} res: {res.content}")
    for i in res.json()['result']['values']:
        concurrent.append(i[-1])
    return max(concurrent)


def get_dispatcher_info_action(
    vtaps_mgt_ip, df_mgt_ip, start_time, end_time, common_utils
):
    '''Performance results from the agent on DF by API.

    '''
    vtap_name = common_utils.get_vtaps_full_name_by_ip(
        vtaps_mgt_ip=vtaps_mgt_ip
    )
    cpu_usage = get_vtaps_max_cpu_usage(
        vtaps_name=vtap_name, query_port=common_utils.df_server_query_port,
        start_time=start_time, end_time=end_time, df_mgt_ip=df_mgt_ip
    )
    mem_usage = get_vtaps_max_mem_usage(
        vtaps_name=vtap_name, query_port=common_utils.df_server_query_port,
        start_time=start_time, end_time=end_time, df_mgt_ip=df_mgt_ip
    )
    dispatcher_bps = get_vtaps_max_dispatcher_bps(
        vtaps_name=vtap_name, query_port=common_utils.df_server_query_port,
        start_time=start_time, end_time=end_time, df_mgt_ip=df_mgt_ip
    )
    dispatcher_pps = get_vtaps_max_dispatcher_pps(
        vtaps_name=vtap_name, query_port=common_utils.df_server_query_port,
        start_time=start_time, end_time=end_time, df_mgt_ip=df_mgt_ip
    )
    drop_pack = get_vtaps_max_drop_pack(
        vtaps_name=vtap_name, query_port=common_utils.df_server_query_port,
        start_time=start_time, end_time=end_time, df_mgt_ip=df_mgt_ip
    )
    concurrent = get_vtaps_max_concuerrent(
        vtaps_name=vtap_name, query_port=common_utils.df_server_query_port,
        start_time=start_time, end_time=end_time, df_mgt_ip=df_mgt_ip
    )
    return cpu_usage, mem_usage, dispatcher_bps, dispatcher_pps, drop_pack, concurrent


def unit_format(data):
    '''Data format conversion, The specific fields are as follows.
    cpu_usage: Values are retained in two decimal places and converted to percentage form
    mem_usage: The unit of the value is converted from bytes to megabytes
    dispatcher_pps: The unit of the value is converted from packets per second to thousands of packets per second. 
    drop_pack: The format of the value is converted to string form.
    concurrent: The format of the value is converted to string form.
    '''
    data["cpu_usage"] = "%.2f" % round(data["cpu_usage"], 2)
    data["cpu_usage"] = f"{data['cpu_usage']}%"
    data["mem_usage"] = "%.2fM" % round(data["mem_usage"] / 1000000, 2)
    data["dispatcher_bps"] = "%.2fGbps" % round(
        data["dispatcher_bps"] / 1000000000, 2
    ) if data["dispatcher_bps"] >= 1000000000 else "%.2fMbps" % round(
        data["dispatcher_bps"] / 1000000, 2
    )
    data["dispatcher_pps"
         ] = "%.2fKpps" % round(data["dispatcher_pps"] / 1000, 2)
    data["drop_pack"] = "%d" % data["drop_pack"]
    data["concurrent"] = "%d" % data["concurrent"]
    return data
