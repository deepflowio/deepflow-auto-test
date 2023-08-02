# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from case.interface.querier_sql.base import QuerierSqlBaseCase

#  Agent type: contain-V


class TestShowTables002(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tables')
    @allure.feature('')
    @allure.title('tables sql 注入')
    @allure.description
    @pytest.mark.medium
    def test_show_tables_002(self):
        case_id = "show tables_002"
        case_name = "sql注入"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #1、use show tables;show tables query

        # Expected results:
        #1、Failed query

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1、use show tables;show tables query'):
            api.query_sql_api(
                database="flow_metrics", sql_cmd="show tables;show tables"
            )
            api.echo_debug_info()
            api.response_status_assert_fail()
            api.response_description_equal_to(
                "parse show sql error, sql: 'show tables;show tables' not support"
            )
