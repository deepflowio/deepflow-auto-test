# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
import logging
from common.querier_api_utils import QueryApi
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestSelectAllTags(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('select tags')
    @allure.feature('flow_log')
    @allure.title('select all tags from l4_flow_log')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_l4_flow_log(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_all_tags(api, "flow_log", "l4_flow_log")
            api.clear()
        with allure_step('2.select all tags from l4_flow_log'):
            sql = f"select {', '.join(tags)} from l4_flow_log limit 1"
            api.query_sql_loop_values(
                database="flow_log", sql_cmd=sql, retries=30
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in tags:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select tags')
    @allure.feature('flow_log')
    @allure.title('select all tags from l7_flow_log')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_l7_flow_log(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_all_tags(api, "flow_log", "l7_flow_log")
            api.clear()
        with allure_step('2.select all tags from l7_flow_log'):
            sql = f"select {', '.join(tags)} from l7_flow_log limit 1"
            api.query_sql_loop_values(
                database="flow_log", sql_cmd=sql, retries=30
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in tags:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select tags')
    @allure.feature('flow_log')
    @allure.title('select all tags from l4_packet')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_l4_packet(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_all_tags(api, "flow_log", "l4_packet")
            api.clear()
        with allure_step('2.select all tags from l4_packet'):
            sql = f"select {', '.join(tags)} from l4_packet limit 1"
            api.query_sql_api(database="flow_log", sql_cmd=sql)
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in tags:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select tags')
    @allure.feature('flow_log')
    @allure.title('select all tags from l7_packet')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_l7_packet(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_all_tags(api, "flow_log", "l7_packet")
            api.clear()
        with allure_step('2.select all tags from l7_packet'):
            sql = f"select {', '.join(tags)} from l7_packet limit 1"
            api.query_sql_api(database="flow_log", sql_cmd=sql)
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in tags:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select tags')
    @allure.feature('flow_metrics')
    @allure.title('select all tags from vtap_flow_edge_port')
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
            api.clear()
        with allure_step('2.select all tags from vtap_flow_edge_port'):
            sql = f"select {', '.join(tags)} from vtap_flow_edge_port limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m",
                retries=30
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in tags:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select tags')
    @allure.feature('flow_metrics')
    @allure.title('select all tags from vtap_app_edge_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_vtap_app_edge_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_all_tags(api, "flow_metrics", "vtap_app_edge_port")
            api.clear()
        with allure_step('2.select all tags from vtap_app_edge_port'):
            sql = f"select {', '.join(tags)} from vtap_app_edge_port limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m",
                retries=30
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in tags:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select tags')
    @allure.feature('flow_metrics')
    @allure.title('select all tags from vtap_flow_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_vtap_flow_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_all_tags(api, "flow_metrics", "vtap_flow_port")
            api.clear()
        with allure_step('2.select all tags from vtap_flow_port'):
            sql = f"select {', '.join(tags)} from vtap_flow_port limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m",
                retries=30
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in tags:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select tags')
    @allure.feature('flow_metrics')
    @allure.title('select all tags from vtap_app_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_vtap_app_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_all_tags(api, "flow_metrics", "vtap_app_port")
            api.clear()
        with allure_step('2.select all tags from vtap_app_port'):
            sql = f"select {', '.join(tags)} from vtap_app_port limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m",
                retries=30
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in tags:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False
