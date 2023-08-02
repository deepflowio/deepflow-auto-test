# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from case.interface.querier_sql.base import QuerierSqlBaseCase

#  Agent type: contain-V


class TestShowTables001(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tables')
    @allure.feature('')
    @allure.title('tables 正常查询')
    @allure.description
    @pytest.mark.medium
    def test_show_tables_001(self):
        case_id = "show tables_001"
        case_name = "正常查询"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #1、use show tables query

        # Expected results:
        #1、Query to specific table name data

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        # 1、use <show tabless> query
        with allure_step('1、use <show tables> query'):
            api.query_sql_api(database="flow_metrics", sql_cmd="show tables")
            api.echo_debug_info()
            api.response_status_assert_success()
            api.response_values_equal_specified_values(values[:])


values = [['vtap_flow_port', ['1s', '1m']],
          ['vtap_flow_edge_port', ['1s',
                                   '1m']], ['vtap_app_port', ['1s', '1m']],
          ['vtap_app_edge_port', ['1s', '1m']]]
