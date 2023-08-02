import logging
import os

import pymysql
from common import common_config
from common.tool.linux_cmd import LinuxCmd


class Mysql(object):

    def __init__(self):
        self.db = None
        self.linux_cmd = LinuxCmd()
        pass

    def get_server_ip_port(self):
        mysql_ip = common_config.df_ce_mgt_ip
        self.linux_cmd.setter(vm_ip=mysql_ip)
        port, err = self.linux_cmd.exec_cmd(
            "kubectl get svc -A | grep deepflow-mysql |  awk '{print $6}'"
        )
        if err:
            assert False
        mysql_port = port[0].split("/")[0].split(":")[1]
        mysql_port = int(mysql_port)
        return mysql_ip, mysql_port

    def get_mysql_password(self):
        mysql_password = os.environ.get('MYSQL_PASSWORD')
        return mysql_password

    def mysqladmin_flush_hosts(self):
        pass

    def connect_to_mysql(self):
        mysql_ip, mysql_port = self.get_server_ip_port()
        mysql_password = self.get_mysql_password()
        print(mysql_ip, mysql_port)
        print(mysql_password)
        db = pymysql.connect(
            host=mysql_ip, port=mysql_port, user='root', passwd=mysql_password,
            db='deepflow', charset='utf8'
        )
        self.db = db

    def exec_sql(self, sql=""):
        if sql == "":
            assert False

        if self.db is None:
            self.connect_to_mysql()
        db = self.db

        cursor = db.cursor()
        try:
            cursor.execute(sql)  # Execute sql statement
            result = cursor.fetchall(
            )  # Returns all information from a database query
            db.commit()  # save changes made to the firm to the database.
        except Exception as err:
            db.rollback()  #Rollback on Error
            logging.error("exec_sql_cmd:exec cmd failed, err:{}".format(err))
        cursor.close()
        return result

    def change_database(self, target_databases="deepflow"):
        sql = "use {};".format(target_databases)
        logging.info("change_databases::sql ==> {}".format(sql))
        self.exec_sql(sql=sql)

    def exec_sql_in_database(self, database="deepflow", sql=""):
        self.change_database(target_databases=database)
        res = self.exec_sql(sql=sql)
        return res

    def get_all_vtap_ip_list(self, name_like="", ctrl_ip_like=""):
        sql = "select ctrl_ip from vtap"
        if name_like != "":
            sql = sql + " where name like '{}'".format(name_like)
        if ctrl_ip_like != "":
            if name_like != "":
                sql = sql + " and ctrl_ip like '{}'".format(ctrl_ip_like)
            else:
                sql = sql + " where ctrl_ip like '{}'".format(ctrl_ip_like)
        sql = sql + ";"
        logging.info("get_all_vtap_ip_list::sql ==> {}".format(sql))
        res = self.exec_sql_in_database(sql=sql)
        return res

    def batch_delete_vtap(self, name_like="", ctrl_ip_like=""):
        sql = 'delete from vtap'
        if name_like != "":
            sql = sql + " where name like '{}'".format(name_like)
        if ctrl_ip_like != "":
            if name_like != "":
                sql = sql + " and ctrl_ip like '{}'".format(ctrl_ip_like)
            else:
                sql = sql + " where ctrl_ip like '{}'".format(ctrl_ip_like)
        sql = sql + ";"

        logging.info("batch_delete_vtap::sql ==> {}".format(sql))
        self.exec_sql_in_database(sql=sql)
