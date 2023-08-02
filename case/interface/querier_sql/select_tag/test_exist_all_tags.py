# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
import logging
from common.querier_api_utils import QueryApi
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestExistAllTags(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('exist tags')
    @allure.feature('flow_log')
    @allure.title('exist all tags from l4_flow_log')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_l4_flow_log(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_all_tags(api, "flow_log", "l4_flow_log")
            exist_tags = [f"exist({tag})" for tag in tags]
            api.clear()
        with allure_step('2.exist all tags from l4_flow_log'):
            sql = f"select Max(byte) as max_byte from l4_flow_log where {' AND '.join(exist_tags)} limit 1"
            api.query_sql_loop_values(database="flow_log", sql_cmd=sql)
            api.echo_debug_info()
            api.response_status_assert_success()

    @allure.suite('API test')
    @allure.epic('exist tags')
    @allure.feature('flow_log')
    @allure.title('exist all tags from l7_flow_log')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_l7_flow_log(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_all_tags(api, "flow_log", "l7_flow_log")
            exist_tags = [f"exist({tag})" for tag in tags]
            api.clear()
        with allure_step('2.exist all tags from l7_flow_log'):
            sql = f"select Max(request) as max_request from l7_flow_log where {' AND '.join(exist_tags)} limit 1"
            api.query_sql_loop_values(database="flow_log", sql_cmd=sql)
            api.echo_debug_info()
            api.response_status_assert_success()

    @allure.suite('API test')
    @allure.epic('exist tags')
    @allure.feature('flow_metrics')
    @allure.title('exist all tags from vtap_flow_edge_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_vtap_flow_edge_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_all_tags(
                api, "flow_metrics", "vtap_flow_edge_port"
            )
            exist_tags = [f"exist({tag})" for tag in tags]
            api.clear()
        with allure_step(
            '2.select Max(byte) exist all tags from vtap_flow_edge_port'
        ):
            sql = f"select Max(byte) as max_byte from vtap_flow_edge_port where {' AND '.join(exist_tags)} limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m"
            )
            api.echo_debug_info()
            api.response_status_assert_success()

    @allure.suite('API test')
    @allure.epic('exist tags')
    @allure.feature('flow_metrics')
    @allure.title('exist all tags from vtap_app_edge_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_vtap_app_edge_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_all_tags(api, "flow_metrics", "vtap_app_edge_port")
            exist_tags = [f"exist({tag})" for tag in tags]
            api.clear()
        with allure_step(
            '2.select Max(request) exist all tags from vtap_app_edge_port'
        ):
            sql = f"select Max(request) as max_request from vtap_app_edge_port where {' AND '.join(exist_tags)} limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m"
            )
            api.echo_debug_info()
            api.response_status_assert_success()

    @allure.suite('API test')
    @allure.epic('exist tags')
    @allure.feature('flow_metrics')
    @allure.title('exist all tags from vtap_flow_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_vtap_flow_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_all_tags(api, "flow_metrics", "vtap_flow_port")
            exist_tags = [f"exist({tag})" for tag in tags]
            api.clear()
        with allure_step(
            '2.select Max(byte) exist all tags from vtap_flow_port'
        ):
            sql = f"select Max(byte) as max_byte from vtap_flow_port where {' AND '.join(exist_tags)} limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m"
            )
            api.echo_debug_info()
            api.response_status_assert_success()

    @allure.suite('API test')
    @allure.epic('exist tags')
    @allure.feature('flow_metrics')
    @allure.title('exist all tags from vtap_app_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_vtap_app_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_all_tags(api, "flow_metrics", "vtap_app_port")
            exist_tags = [f"exist({tag})" for tag in tags]
            api.clear()
        with allure_step(
            '2.select Max(request) exist all tags from vtap_app_port'
        ):
            sql = f"select Max(request) as max_request from vtap_app_port where {' AND '.join(exist_tags)} limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
