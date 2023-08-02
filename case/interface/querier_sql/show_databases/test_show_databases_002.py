# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from case.interface.querier_sql.base import QuerierSqlBaseCase

#  Agent type: contain-V


class TestShowDatabases002(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show database')
    @allure.feature('')
    @allure.title('databases sql注入')
    @allure.description
    @pytest.mark.medium
    def test_show_databases_002(self):
        case_id = "show_databases_002"
        case_name = "sql注入"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #1、使用show databases;show databases;查询

        # Expected results:
        #1、Failed query

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        # 1、使用show databases;show databases;查询
        with allure_step('1、使用show databases;show databases;查询'):
            api.query_sql_api(
                database="flow_metrics",
                sql_cmd="show databases;show databases"
            )
            api.echo_debug_info()
            api.response_status_assert_fail()
            api.response_description_equal_to(
                "parse show sql error, sql: 'show databases;show databases' not support"
            )
