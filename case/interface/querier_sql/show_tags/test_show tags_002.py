# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from case.interface.querier_sql.base import QuerierSqlBaseCase

#  Agent type: contain-V


class TestShowTags002(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('')
    @allure.feature('')
    @allure.title('tags sql注入')
    @allure.description
    @pytest.mark.medium
    def test_show_tags_002(self):
        case_id = "show tags_002"
        case_name = "sql注入"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #1、use show tags;show tags query

        # Expected results:
        #1、Failed query
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1、use <show tags;show tags> query'):
            api.query_sql_api(
                database="flow_metrics", sql_cmd="show tags;show tags"
            )
            api.echo_debug_info()
            api.response_status_assert_fail()
            api.response_description_equal_to(
                "parse show sql error, sql: 'show tags;show tags' not support"
            )
