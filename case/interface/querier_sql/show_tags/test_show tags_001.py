# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from case.interface.querier_sql.base import QuerierSqlBaseCase

#  Agent type: contain-V


class TestShowTags001(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('')
    @allure.feature('')
    @allure.title('show tags from flow_metrics')
    @allure.description
    @pytest.mark.medium
    def test_show_tags_001_flow_metrics(self):
        case_id = "show tags_001"
        case_name = "正常查询"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #1、use show tags query

        # Expected results:
        #1、Data can be queried
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1、use <show tags> query'):
            api.query_sql_api(database="flow_metrics", sql_cmd="show tags")
            api.echo_debug_info()
            api.response_status_assert_success()
            api.response_values_is_not_None()

    @allure.suite('API test')
    @allure.epic('')
    @allure.feature('')
    @allure.title('show tags from flow_log')
    @allure.description
    @pytest.mark.medium
    def test_show_tags_001_flow_log(self):
        case_id = "show tags_001"
        case_name = "正常查询"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #1、use show tags query

        # Expected results:
        #1、Data can be queried
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1、use <show tags> query'):
            api.query_sql_api(database="flow_log", sql_cmd="show tags")
            api.echo_debug_info()
            api.response_status_assert_success()
            api.response_values_is_not_None()

    @allure.suite('API test')
    @allure.epic('')
    @allure.feature('')
    @allure.title('show tags from event')
    @allure.description
    @pytest.mark.medium
    def test_show_tags_001_event(self):
        case_id = "show tags_001"
        case_name = "正常查询"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #1、use show tags query

        # Expected results:
        #1、Data can be queried
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1、use <show tags> query'):
            api.query_sql_api(database="event", sql_cmd="show tags")
            api.echo_debug_info()
            api.response_status_assert_success()
            api.response_values_is_not_None()

    @allure.suite('API test')
    @allure.epic('')
    @allure.feature('')
    @allure.title('show tags from deepflow_system')
    @allure.description
    @pytest.mark.medium
    def test_show_tags_001_deepflow_system(self):
        case_id = "show tags_001"
        case_name = "正常查询"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #1、use show tags query

        # Expected results:
        #1、Data can be queried
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1、use <show tags> query'):
            api.query_sql_api(database="deepflow_system", sql_cmd="show tags")
            api.echo_debug_info()
            api.response_status_assert_success()
            api.response_values_is_not_None()
