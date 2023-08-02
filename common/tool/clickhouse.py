import logging

from clickhouse_sqlalchemy import make_session
from sqlalchemy import create_engine
import pandas as pd
import requests
from common.common_config import df_ce_mgt_ip
from common.tool.linux_cmd import LinuxCmd


class ClickHouse(object):

    def __init__(self):
        self.host = df_ce_mgt_ip
        self.linux_cmd = LinuxCmd()
        pass

    def get_port(self):
        self.linux_cmd.setter(vm_ip=df_ce_mgt_ip)
        port = self.linux_cmd.exec_cmd(
            "kubectl get svc -A | grep deepflow-clickhouse |  awk '{print $6}'"
        )
        service_port = port[0].split(",")
        for item in service_port:
            if "8123" in item:
                port = item.split("/")[0].split(":")[1]
                logging.info("get_port::port ==> {}".format(port))
                break
        return port

    def query_for_dataframe(self, sql=""):
        if sql == "":
            assert False
        logging.info("query_for_dataframe::sql ==> {}".format(sql))

        host = self.host
        port = self.get_port()
        conf = {
            "user": "default",
            "password": "",
            "server_host": host,
            "port": port,
            "db": "deepflow_system"
        }

        connection = 'clickhouse://{user}:{password}@{server_host}:{port}/{db}'.format(
            **conf
        )
        engine = create_engine(
            connection, pool_size=100, pool_recycle=3600, pool_timeout=20
        )

        session = make_session(engine)
        cursor = session.execute(sql)
        try:
            fields = cursor._metadata.keys
            # Convert data returned from the database into DataFrame objects
            df = pd.DataFrame([
                dict(zip(fields, item)) for item in cursor.fetchall()
            ])
        finally:
            cursor.close()
            session.close()
        return df

    def query_for_list(self, sql=""):
        if sql == "":
            assert False
        logging.info("query_for_list::sql ==> {}".format(sql))
        SSL_VERIFY = False
        host = self.host
        port = self.get_port()
        url = 'http://{}:{}'.format(host, port)
        query_dict = {'query': sql}
        res = requests.post(url, params=query_dict, verify=SSL_VERIFY)
        res = res.text.split("\n")
        res_list = []
        for item in res:
            res_list.append(item.split("\t"))
        return res_list
