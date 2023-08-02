from common.utils import step as allure_step
import allure
import time
import logging
from case.base import BaseCase
from common.querier_api_utils import QueryApi

edge_table_names = [
    "vtap_flow_edge_port", "vtap_app_edge_port", "l4_flow_log", "l7_flow_log"
]


class QuerierSqlBaseCase(BaseCase):

    first_data_checked = False

    @classmethod
    def _setup_class(cls):
        api = QueryApi(
            cls.df_ce_info["mgt_ip"], cls.df_ce_info["server_query_port"]
        )
        with allure_step('setup: check db first data'):
            count = 0
            while not cls.first_data_checked and count < 60:
                api.query_sql_api(
                    database="flow_metrics", sql_cmd=
                    "select pod_node from vtap_flow_port order by time limit 1",
                    data_precision="1s"
                )
                api.echo_debug_info()
                api.response_status_assert_success()
                if api.response_json["result"]["values"]:
                    cls.first_data_checked = True
                else:
                    time.sleep(10)
                    count += 1
            if not cls.first_data_checked:
                logging.error("querier check first data error!")
                assert False

    def get_all_tags(self, api, db, table):
        tags = []
        api.query_sql_api(database=db, sql_cmd=f"show tags from {table}")
        api.echo_debug_info()
        api.response_status_assert_success()
        values = api.response_json["result"]["values"]
        for value in values:
            # Tag that doesn't support SELECT but only WHERE
            if value[0] in ["lb_listener", "pod_ingress"]:
                continue
            if table in edge_table_names and value[0] != value[1]:
                #Strings containing backquotes
                tags.append(f"`{value[1]}`")
                tags.append(f"`{value[2]}`")
            else:
                tags.append(f"`{value[0]}`")
        return tags

    def get_tables(self, api, db):
        tables = []
        api.query_sql_api(database=db, sql_cmd="show tables")
        api.echo_debug_info()
        api.response_status_assert_success()
        values = api.response_json["result"]["values"]
        for value in values:
            tables.append(value[0])
        return tables
