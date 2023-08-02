import logging
import os
from common import common_config
from common.ssh import ssh_pool


def check_cluster_in_deepflow(cluster_name, conn, includes=True):
    result = False
    with conn.cursor() as cur:
        sql = "select name from pod_cluster where name='{}';".format(
            cluster_name
        )
        logging.info(f"Exec Sql: {sql}")
        cur.execute(sql)
        if includes:
            for r in cur:
                logging.info("Debug add cluster: {r}")
                if cluster_name == r[0]:
                    result = True
                    break
        else:
            datas = cur.fetchall()
            logging.info(f"Debug delete cluster: {datas}")
            if datas == ():
                result = True
    return result


def k8s_delete_node(
    master_mgt_ip, node_mgt_ip, username=common_config.ssh_username_default,
    password=common_config.ssh_password_default,
    ssh_port=common_config.ssh_port_default
):
    ssh = ssh_pool.get(master_mgt_ip, ssh_port, username, password)
    stdin, stdout, stderr = ssh.exec_command(
        '''sealos delete --nodes {} --force && \
                                                kubectl get nodes'''
        .format(node_mgt_ip)
    )
    err = stderr.readlines()
    if err:
        logging.error(err)


def k8s_add_node(
    master_mgt_ip, node_mgt_ip, ssh_port=common_config.ssh_port_default,
    username=common_config.ssh_username_default,
    password=common_config.ssh_password_default
):
    ssh = ssh_pool.get(master_mgt_ip, ssh_port, username, password)
    stdin, stdout, stderr = ssh.exec_command(
        f'''sealos add --nodes {node_mgt_ip} && kubectl get nodes'''
    )
    err = stderr.readlines()
    if err:
        logging.error(err)
