# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from case.interface.querier_sql.base import QuerierSqlBaseCase

#  Agent type: contain-V


class TestShowMetrics002(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show metrics')
    @allure.feature('')
    @allure.title('metrics sql注入')
    @allure.description
    @pytest.mark.medium
    def test_show_metrics_002(self):
        case_id = "show metrics_002"
        case_name = "sql注入"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #1、use show metrics;show metrics query

        # Expected results:
        #1、Failed query

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1、use show metrics;show metrics query'):
            api.query_sql_api(sql_cmd="show metrics;show metrics")
            api.echo_debug_info()
            api.response_status_assert_fail()
            api.response_description_equal_to(
                "parse show sql error, sql: 'show metrics;show metrics' not support"
            )
