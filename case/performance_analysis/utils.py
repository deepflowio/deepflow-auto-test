import logging
import datetime
import time
from common import common_config
from common.ssh import ssh_pool
from scp import SCPClient

loop_count = 90
nginx_rate = '85000 75000 65000 60000 55000 50000 45000 40000 35000 30000'
istio_rate = '420 400 380 360 350 340 330 320 310 300'
go_chi_rate = '7500 6500 5500 5000 4500 4000 3500 3000 2500 2000'
go_server_rate = '360 330 300 270 240 220 200 180 160 140'


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
        assert False
    return res[-1].strip('\n')[:8]


def upload_tools(
    vm_ip, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(vm_ip, ssh_port, username, password)
    scpclient = SCPClient(ssh.get_transport(), socket_timeout=15.0)
    local_path = "/root/df-test/case/performance_analysis/tool/"
    remote_path = "/root/"
    try:
        scpclient.put(local_path + "run.sh", remote_path)
        scpclient.put(local_path + "read_stat.py", remote_path + "df-test/")
        scpclient.put(local_path + "run-nginx.sh", remote_path + "df-test/")
        scpclient.put(local_path + "run-go-chi.sh", remote_path + "df-test/")
        scpclient.put(
            local_path + "run-go-server.sh", remote_path + "df-test/"
        )
        scpclient.put(
            local_path + "run-productpage.sh", remote_path + "df-test/"
        )
        scpclient.put(local_path + "telegraf.conf", "/etc/telegraf/")
        ssh.exec_command("systemctl restart telegraf")
    except Exception as e:
        logging.error(e)
        assert False
    else:
        logging.info("upload tools success")


def init_go_chi(
    vm_ip, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(vm_ip, ssh_port, username, password)
    cmd = "cd go-microservices-main&&make up&&sleep 3&&make auth&&docker ps"
    logging.info(f"exec cmd: {cmd}")
    _, stdout, stderr = ssh.exec_command(cmd)
    logging.info(stdout.readlines())
    err = stderr.readlines()
    if err:
        logging.error(f"init go chi error: {err}")


def init_go_server(
    vm_ip, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(vm_ip, ssh_port, username, password)
    cmd = "cd go-server-sample-master&&docker-compose up -d&&sleep 3&&docker ps"
    logging.info(f"exec cmd: {cmd}")
    _, stdout, stderr = ssh.exec_command(cmd)
    logging.info(stdout.readlines())
    err = stderr.readlines()
    if err:
        logging.error(f"init go server error: {err}")


def init_istio(
    vm_ip, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(vm_ip, ssh_port, username, password)
    i = 0
    while True:
        logging.info(
            'Wait for istio service status to be normal,about 30s, timeout is 900'
        )
        stdin, stdout, stderr = ssh.exec_command('kubectl get pods')
        logs = stdout.readlines()
        logging.info(logs)
        res = True
        for k in logs[1:]:
            logging.info("get pod ========= > {}".format(k))
            if 'Running' not in k.split()[2] or '2/2' not in k.split()[1]:
                res = False
                break
        if res == True:
            logging.info('istio services is normal')
            break
        else:
            if i >= loop_count:
                assert False
            i += 1
            time.sleep(10)
    cmd = '''cd istio-1.17.1 && kubectl exec "$(kubectl get pod -l app=ratings -o jsonpath='{.items[0].metadata.name}')" -c ratings -- curl -sS productpage:9080/productpage | grep -o "<title>.*</title>" && \
        kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml && \
        istioctl analyze'''
    logging.info(f"exec cmd: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    logging.info(stdout.readlines())
    logging.error(stderr.readlines())


def install_istio(
    vm_ip, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(vm_ip, ssh_port, username, password)
    #cmd = "sh ./init_istio.sh"
    cmd1 = "cd istio-1.17.1 && export PATH=$PWD/bin:$PATH && istioctl install --set profile=demo -y"
    logging.info(f"exec cmd: {cmd1}")
    stdin, stdout, stderr = ssh.exec_command(cmd1)
    logging.info(stdout.readlines())
    err = stderr.readlines()
    logging.error(err)
    if any("5m0s" in e for e in err):
        cmd_tmp = "kubectl get pod  -n istio-system|awk 'NR>1{print $3}'"
        start_time = time.time()
        end_time = start_time + 30 * 60
        while True:
            stdin, stdout, stderr = ssh.exec_command(cmd_tmp)
            logs = stdout.readlines()
            logging.info(f"istio_pod_status is {logs}")
            if all("Running" in pod_status for pod_status in logs):
                break
            elif time.time() > end_time:
                assert False
            else:
                time.sleep(30)
    cmd2 = '''kubectl label namespace default istio-injection=enabled && \
        kubectl apply -f istio-1.17.1/samples/bookinfo/platform/kube/bookinfo.yaml'''
    logging.info(f"exec cmd: {cmd2}")
    stdin, stdout, stderr = ssh.exec_command(cmd2)
    logging.info(stdout.readlines())
    err = stderr.readlines()
    if err:
        logging.info(err)
        assert False


def run_nginx_analysis(
    nginx_ip, with_agent=False, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    nginx_ssh = ssh_pool.get(nginx_ip, ssh_port, username, password)
    nginx_invoke = nginx_ssh.invoke_shell()
    test_nginx_cmd = "wrk2 -c1 -t1 -R30000 -d30 -L http://127.0.0.1:80/index.html"
    nginx_cmd = "sleep 3&&sh ./run.sh log nginx without_agent"
    if with_agent:
        nginx_cmd = "sleep 30&&sh ./run.sh agent-log nginx with_agent"

    # test nginx
    logging.info(f"exec test_nginx cmd: {test_nginx_cmd}")
    _, stdout, _ = nginx_ssh.exec_command(test_nginx_cmd, timeout=60)
    logging.info(f"test_nginx: {stdout.readlines()}")
    time.sleep(10)

    # run nginx
    logging.info(f"run nginx cmd: {nginx_cmd}")
    _, stdout, _ = nginx_ssh.exec_command(nginx_cmd)
    logging.info(f"run nginx: {stdout.readlines()}")


def run_istio_analysis(
    istio_ip, with_agent=False, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    istio_ssh = ssh_pool.get(istio_ip, ssh_port, username, password)
    test_istio_cmd = "wrk2 -c50 -t4 -R340 -d120 -L http://$(kubectl get svc |grep productpage|awk '{print $3}'):9080/productpage"
    istio_cmd = "sleep 3&&sh ./run.sh log istio without_agent"
    if with_agent:
        istio_cmd = "sleep 30&&sh ./run.sh agent-log istio with_agent"

    # test istio
    logging.info(f"exec test_istio cmd: {test_istio_cmd}")
    _, stdout, _ = istio_ssh.exec_command(test_istio_cmd, timeout=150)
    logging.info(f"test_istio: {stdout.readlines()}")
    time.sleep(10)

    # run istio
    logging.info(f"run istio cmd: {istio_cmd}")
    _, stdout, _ = istio_ssh.exec_command(istio_cmd)
    logging.info(f"run istio: {stdout.readlines()}")


def run_go_chi_analysis(
    go_chi_ip, with_agent=False, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(go_chi_ip, ssh_port, username, password)
    cmd = "sleep 3&&sh ./run.sh log go-chi without_agent"
    if with_agent:
        cmd = "sleep 30&&sh ./run.sh agent-log go-chi with_agent"

    logging.info(f"run go_chi cmd: {cmd}")
    _, stdout, _ = ssh.exec_command(cmd)
    logging.info(f"run go_chi: {stdout.readlines()}")


def run_go_server_analysis(
    go_server_ip, with_agent=False, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(go_server_ip, ssh_port, username, password)
    cmd = "sleep 60&&sh ./run.sh log go-server without_agent"
    if with_agent:
        cmd = "sleep 60&&sh ./run.sh agent-log go-server with_agent"

    logging.info(f"run go_server cmd: {cmd}")
    _, stdout, _ = ssh.exec_command(cmd)
    logging.info(f"run go_server: {stdout.readlines()}")


def get_analysis_result(
    nginx_ip=None, istio_ip=None, go_chi_ip=None, go_server_ip=None,
    time_end=None, with_agent=False, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    logs = []
    if not time_end:
        time_end = int(time.mktime(datetime.datetime.now().timetuple()))
        time_end -= time_end % 60
    if nginx_ip:
        nginx_ssh = ssh_pool.get(nginx_ip, ssh_port, username, password)
        if not with_agent:
            stdin, stdout, stderr = nginx_ssh.exec_command("cat log")
            logs = stdout.readlines()
            logging.info(f"nginx_without_agent:{logs}")
            if not logs:
                assert False
        else:
            stdin, stdout, stderr = nginx_ssh.exec_command("cat agent-log")
            logs = stdout.readlines()
            logging.info(f"nginx_with_agent:{logs}")
            if not logs:
                assert False

    if istio_ip:
        istio_ssh = ssh_pool.get(istio_ip, ssh_port, username, password)
        if not with_agent:
            stdin, stdout, stderr = istio_ssh.exec_command("cat log")
            logs = stdout.readlines()
            logging.info(f"istio_without_agent:{logs}")
            if not logs:
                assert False
        else:
            stdin, stdout, stderr = istio_ssh.exec_command("cat agent-log")
            logs = stdout.readlines()
            logging.info(f"istio_with_agent:{logs}")
            if not logs:
                assert False
    if go_chi_ip:
        chi_ssh = ssh_pool.get(go_chi_ip, ssh_port, username, password)
        if not with_agent:
            stdin, stdout, stderr = chi_ssh.exec_command("cat log")
            logs = stdout.readlines()
            logging.info(f"go_chi_without_agent:{logs}")
            if not logs:
                assert False
        else:
            stdin, stdout, stderr = chi_ssh.exec_command("cat agent-log")
            logs = stdout.readlines()
            logging.info(f"go_chi_with_agent:{logs}")
            if not logs:
                assert False

    if go_server_ip:
        server_ssh = ssh_pool.get(go_server_ip, ssh_port, username, password)
        if not with_agent:
            stdin, stdout, stderr = server_ssh.exec_command("cat log")
            logs = stdout.readlines()
            logging.info(f"go_server_without_agent:{logs}")
            if not logs:
                assert False
        else:
            stdin, stdout, stderr = server_ssh.exec_command("cat agent-log")
            logs = stdout.readlines()
            logging.info(f"go_server_with_agent:{logs}")
            if not logs:
                assert False
    return format_analysis_result(logs, time_end, with_agent)


def update_wrk_rate(
    vm_ip, nginx_rate=nginx_rate, istio_rate=istio_rate,
    go_chi_rate=go_chi_rate, go_server_rate=go_server_rate,
    ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(vm_ip, ssh_port, username, password)

    cmd1 = f'''sed -ri "s/(nginx_rate_array=).*/\\1\\({nginx_rate}\\)/g" run.sh'''
    stdin, stdout, stderr = ssh.exec_command(cmd1)
    err1 = stderr.readlines()
    if err1:
        logging.error(f"exec cmd1: {cmd1} err: {err1}")
        assert False

    cmd2 = f'''sed -ri "s/(istio_rate_array=).*/\\1\\({istio_rate}\\)/g" run.sh'''
    stdin, stdout, stderr = ssh.exec_command(cmd2)
    err2 = stderr.readlines()
    if err2:
        logging.error(f"exec cmd2: {cmd2} err: {err2}")
        assert False
    cmd3 = f'''sed -ri "s/(chi_rate_array=).*/\\1\\({go_chi_rate}\\)/g" run.sh'''
    stdin, stdout, stderr = ssh.exec_command(cmd3)
    err3 = stderr.readlines()
    if err3:
        logging.error(f"exec cmd3: {cmd3} err: {err3}")
        assert False
    cmd4 = f'''sed -ri "s/(server_rate_array=).*/\\1\\({go_server_rate}\\)/g" run.sh'''
    stdin, stdout, stderr = ssh.exec_command(cmd4)
    err4 = stderr.readlines()
    if err4:
        logging.error(f"exec cmd4: {cmd4} err: {err4}")
        assert False
    return


def format_analysis_result(logs, time_end, with_agent):
    '''
    nginx                # process
    30000                # rate
    603.00us             # lantency p50 
    1.05ms               # lantency p90
    29999.52
    53.6862749910574     # process_max_cpu(%)
    0.02504129335284233  # process_max_mem(%)
    26.802343808681144   # wrk2_max_cpu(%)
    0.037101056426763535 # wrk2_max_mem(%)
    26.802343808681144   # agent_max_cpu(%)
    0.037101056426763535 # agent_max_mem(%)
    '''

    def format_lantency(lantency):
        if lantency.endswith("us"):
            return float(lantency[:-2])
        elif lantency.endswith("ms"):
            return float(lantency[:-2]) * 1000
        elif lantency.endswith("s"):
            return float(lantency[:-2]) * 1000000
        else:
            return lantency

    def format_nginx_log(log, i):
        point = {
            "process_name": log[i],
            "rate": log[i + 1],
            "annotation_rate": f"QPS={log[i+1]}",
            "lantency_p50": format_lantency(log[i + 2]),
            "lantency_p90": format_lantency(log[i + 3]),
            "req_per_sec": float(log[i + 4]),
            "process_max_cpu": float(log[i + 5]),
            "process_max_mem": float(log[i + 6]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10, # unit K, log mem%
            "wrk2_max_cpu": float(log[i + 7]),
            "wrk2_max_mem": float(log[i + 8]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
            "agent_max_cpu": float(log[i + 9]),
            "agent_max_mem": float(log[i + 10]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
        }
        return point

    def format_go_chi_log(log, i):
        point = {
            "process_name": log[i],
            "rate": log[i + 1],
            "annotation_rate": f"QPS={log[i+1]}",
            "lantency_p50": format_lantency(log[i + 2]),
            "lantency_p90": format_lantency(log[i + 3]),
            "req_per_sec": float(log[i + 4]),
            "process_max_cpu": float(log[i + 5]),
            "process_max_mem": float(log[i + 6]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
            "wrk2_max_cpu": float(log[i + 7]),
            "wrk2_max_mem": float(log[i + 8]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
            "postgres_max_cpu": float(log[i + 9]),
            "postgres_max_mem": float(log[i + 10]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
            "agent_max_cpu": float(log[i + 11]),
            "agent_max_mem": float(log[i + 12]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
        }
        return point

    def format_go_server_log(log, i):
        point = {
            "process_name": log[i],
            "rate": log[i + 1],
            "annotation_rate": f"QPS={log[i+1]}",
            "lantency_p50": format_lantency(log[i + 2]),
            "lantency_p90": format_lantency(log[i + 3]),
            "req_per_sec": float(log[i + 4]),
            "process_max_cpu": float(log[i + 5]),
            "process_max_mem": float(log[i + 6]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
            "wrk2_max_cpu": float(log[i + 7]),
            "wrk2_max_mem": float(log[i + 8]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
            "mysql_max_cpu": float(log[i + 9]),
            "mysql_max_mem": float(log[i + 10]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
            "agent_max_cpu": float(log[i + 11]),
            "agent_max_mem": float(log[i + 12]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
        }
        return point

    def format_istio_log(log, i):
        point = {
            "process_name": log[i],
            "rate": log[i + 1],
            "annotation_rate": f"QPS={log[i+1]}",
            "lantency_p50": format_lantency(log[i + 2]),
            "lantency_p90": format_lantency(log[i + 3]),
            "req_per_sec": float(log[i + 4]),
            "process_max_cpu": float(log[i + 5]),
            "process_max_mem": float(log[i + 6]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
            "wrk2_max_cpu": float(log[i + 7]),
            "wrk2_max_mem": float(log[i + 8]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
            "details_max_cpu": float(log[i + 9]),
            "details_max_mem": float(log[i + 10]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
            "reviews_max_cpu": float(log[i + 11]),
            "reviews_max_mem": float(log[i + 12]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
            "ratings_max_cpu": float(log[i + 13]),
            "ratings_max_mem": float(log[i + 14]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
            "envoy_max_cpu": float(log[i + 15]),
            "envoy_max_mem": float(log[i + 16]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
            "agent_max_cpu": float(log[i + 17]),
            "agent_max_mem": float(log[i + 18]) *
            common_config.AGENT_PERFORMANCE_MEMORY * 10,
        }
        return point

    points = []

    indexs = []

    for i, item in enumerate(logs):
        if not item or item == "\n":
            continue
        if item.startswith("nginx") or item.startswith(
            "productpage"
        ) or item.startswith("authApp") or item.startswith("go-server-sampl"):
            indexs.append(i)
    logs = [i.replace("\n", "") for i in logs]
    rs_checked_index = 0
    for index, i in enumerate(indexs):
        if logs[i] == "nginx":
            point = format_nginx_log(logs, i)
        elif logs[i] == "productpage":
            point = format_istio_log(logs, i)
        elif logs[i] == "authApp":
            point = format_go_chi_log(logs, i)
        elif logs[i] == "go-server-sampl":
            point = format_go_server_log(logs, i)
        if point["req_per_sec"] < float(point["rate"]) * 0.9:
            rs_checked_index = index
        point["time"] = time_end - (index * 60)
        point["end_time"] = (point["time"] + 60) * 1000
        point["time_end"] = point["end_time"]
        if not with_agent:
            point["with_agent"] = 0
        else:
            point["with_agent"] = 1
        points.append(point)
    points = points[rs_checked_index:]
    return points


def update_productpage_ip(
    vm_ip, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(vm_ip, ssh_port, username, password)
    cmd = '''sed -ri "s/10.96.3.18/$(kubectl get svc |grep productpage|awk '{print $3}')/g" df-test/run-productpage.sh'''
    stdin, stdout, stderr = ssh.exec_command(cmd)
    err = stderr.readlines()
    if err:
        logging.error(f"exec cmd1: {cmd} err: {err}")
    return


def update_nginx_ip(
    vm_ip, nginx_ip, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(vm_ip, ssh_port, username, password)
    cmd = f'''sed -ri "s/nginx_ip/{nginx_ip}/g" df-test/run-nginx.sh'''
    stdin, stdout, stderr = ssh.exec_command(cmd)
    err = stderr.readlines()
    if err:
        logging.error(f"exec cmd1: {cmd} err: {err}")
    cmd = f'''sed -ri "s/nginx_ip/{nginx_ip}/g" df-test/read_stat.py'''
    stdin, stdout, stderr = ssh.exec_command(cmd)
    err = stderr.readlines()
    if err:
        logging.error(f"exec cmd1: {cmd} err: {err}")
    return
