# coding: utf-8

import logging

import pymysql
import paramiko
import re
import os
import time
from common import common_config
from common.ssh import ssh_pool


class AgentSync(object):

    def __init__(self, df_mgt_ip):
        self.username = common_config.ssh_username_default
        self.password = common_config.ssh_password_default
        self.ssh_port = common_config.ssh_port_default
        self.df_mgt_ip = df_mgt_ip
        self.database_user = common_config.deepflow_ce_mysql_user
        self.database_passwd = common_config.deepflow_ce_mysql_passwd
        self.database_name = common_config.deepflow_ce_mysql_db
        self.mysql_ext_port = self.get_mysql_ext_port()

    def get_mysql_ext_port(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            self.df_mgt_ip, self.ssh_port, self.username, self.password
        )
        stdin, stdout, stderr = ssh.exec_command(
            'kubectl get svc -n deepflow|grep mysql'
        )
        mysql_ext_info = stdout.readlines()[0]
        mysql_ext_port = re.findall(r"\d.*:(\d.*)\/TCP", mysql_ext_info)[0]
        return int(mysql_ext_port)

    def get_vtap_hostname(self, vtap_mgt_ip):
        if vtap_mgt_ip is None:
            assert False
        ssh = ssh_pool.get(
            vtap_mgt_ip, self.ssh_port, self.username, self.password
        )
        stdin, stdout, stderr = ssh.exec_command('hostname')
        hostname_info = stdout.readlines()[0].rstrip('\n')
        return hostname_info

    def modify_mysql_database_max_connect_error(self):
        ssh = ssh_pool.get(
            self.df_mgt_ip, self.ssh_port, self.username, self.password
        )
        stdin, stdout, stderr = ssh.exec_command(
            'kubectl get pods -n deepflow|grep mysql'
        )
        mysql_pod_name = stdout.readlines()[0].split(' ')[0]
        chan = ssh.invoke_shell()
        chan.send(
            '''kubectl exec -ti {} -n deepflow bash\n
                     mysql -u root -pdeepflow\n
                     flush hosts;\n
                     set global max_connect_errors = 1000;\n'''
            .format(mysql_pod_name)
        )
        time.sleep(1)

    def check_vms_in_deepflow_database_by_hostname(self, vtap_hostname):
        if self.mysql_ext_port and vtap_hostname is None:
            assert False
        conn = pymysql.connect(
            host=self.df_mgt_ip, user=self.database_user,
            passwd=self.database_passwd, db=self.database_name,
            port=self.mysql_ext_port
        )
        cur = conn.cursor()
        cur.execute(
            "select * from vm where name like '%{}%';".format(vtap_hostname)
        )
        for r in cur:
            if r[2] == vtap_hostname:
                logging.info(
                    'check_vms_in_deepflow_database_by_hostname::vtap in vm database, vtap hostname:{}'
                    .format(vtap_hostname)
                )
                break
        cur.close()
        conn.close()

    def check_vpc_in_deepflow_database_by_ip(self, vtap_mgt_ip):
        if vtap_mgt_ip is None:
            assert False
        conn = pymysql.connect(
            host=self.df_mgt_ip, user=self.database_user,
            passwd=self.database_passwd, db=self.database_name,
            port=self.mysql_ext_port
        )
        cur = conn.cursor()
        cur.execute(
            "select * from epc where name like '%{}%';".format(vtap_mgt_ip)
        )
        for r in cur:
            if vtap_mgt_ip in r[2]:
                logging.info(
                    'check_vpc_in_deepflow_database_by_ip::vtap ip in vpc database, vtap ip:{}'
                    .format(vtap_mgt_ip)
                )
                break
        cur.close()
        conn.close()

    def check_subnet_in_deepflow_database_by_ip(self, vtap_mgt_ip):
        if vtap_mgt_ip is None:
            assert False
        if vtap_mgt_ip is None:
            assert False
        conn = pymysql.connect(
            host=self.df_mgt_ip, user=self.database_user,
            passwd=self.database_passwd, db=self.database_name,
            port=self.mysql_ext_port
        )
        cur = conn.cursor()
        cur.execute(
            "select * from vl2 where name like '%{}%';".format(vtap_mgt_ip)
        )
        for r in cur:
            if vtap_mgt_ip in r[3]:
                logging.info(
                    'check_subnet_in_deepflow_database_by_ip::vtap ip in subnet database, vtap ip:{}'
                    .format(vtap_mgt_ip)
                )
                break
        cur.close()
        conn.close()

    def check_pod_cluster_in_deepflow_database_by_subdomain_name(
        self, subdomain_name
    ):
        if subdomain_name is None:
            assert False
        conn = pymysql.connect(
            host=self.df_mgt_ip, user=self.database_user,
            passwd=self.database_passwd, db=self.database_name,
            port=self.mysql_ext_port
        )
        cur = conn.cursor()
        cur.execute(
            "select * from pod_cluster where name like '%{}%';"
            .format(subdomain_name)
        )
        for r in cur:
            if subdomain_name in r[1]:
                logging.info(
                    'check_pod_cluster_in_deepflow_database_by_subdomain_name::subdomain name in pod cluster database, name includes:{}'
                    .format(subdomain_name)
                )
                break
        cur.close()
        conn.close()

    def check_az_in_deepflow_database_by_domain_lcuuid(self, domain_lcuuid):
        if domain_lcuuid is None:
            assert False
        conn = pymysql.connect(
            host=self.df_mgt_ip, user=self.database_user,
            passwd=self.database_passwd, db=self.database_name,
            port=self.mysql_ext_port
        )
        cur = conn.cursor()
        cur.execute(
            "select * from az where domain like '%{}%';".format(domain_lcuuid)
        )
        for r in cur:
            if domain_lcuuid in r[5]:
                logging.info(
                    'check_az_in_deepflow_database_by_domain_lcuuid::domain lcuuid in az database, name includes:{}'
                    .format(domain_lcuuid)
                )
                break
        cur.close()
        conn.close()
