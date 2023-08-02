# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from case.interface.querier_sql.base import QuerierSqlBaseCase

#  Agent type: contain-V


class TestShowDatabases001(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show database')
    @allure.feature('')
    @allure.title('databases 正常查询')
    @allure.description
    @pytest.mark.medium
    def test_show_databases_001(self):
        case_id = "show_databases_001"
        case_name = "正常查询"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #1、use show databases query

        # Expected results:
        #1、Query to a specific database name

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('step1: use show databases query'):
            api.query_sql_api(
                database="flow_metrics", sql_cmd="show databases"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            api.response_values_include_specified_values(values[:])


values = [['ext_metrics'], ['deepflow_system'], ['event'], ['flow_log'],
          ['flow_metrics']]
