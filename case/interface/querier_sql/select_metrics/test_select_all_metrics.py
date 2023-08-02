# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
import logging
from common.querier_api_utils import QueryApi
from case.interface.querier_sql.base import QuerierSqlBaseCase

metrics_type_tag = 6
metrics_type_array = 7
metrics_type_countall = 8


class TestSelectAllMetrics(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('select metrics')
    @allure.feature('flow_log')
    @allure.title('select all metrics from l4_flow_log')
    @allure.description
    @pytest.mark.medium
    def test_select_all_metrics_l4_flow_log(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show metrics'):
            metrics = self.get_all_metrics(api, "flow_log", "l4_flow_log")
            api.clear()
        with allure_step('2.select all metrics from l4_flow_log'):
            sql = f"select {', '.join(metrics)} from l4_flow_log limit 1"
            api.query_sql_loop_values(
                database="flow_log", sql_cmd=sql, retries=30
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for m in metrics:
                if m not in columns:
                    logging.error(f"metrics {m} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select metrics')
    @allure.feature('flow_log')
    @allure.title('select all metrics from l7_flow_log')
    @allure.description
    @pytest.mark.medium
    def test_select_all_metrics_l7_flow_log(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show metrics'):
            metrics = self.get_all_metrics(api, "flow_log", "l7_flow_log")
            api.clear()
        with allure_step('2.select all metrics from l7_flow_log'):
            sql = f"select {', '.join(metrics)} from l7_flow_log limit 1"
            api.query_sql_loop_values(
                database="flow_log", sql_cmd=sql, retries=30
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for m in metrics:
                if m not in columns:
                    logging.error(f"m {m} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select metrics')
    @allure.feature('flow_log')
    @allure.title('select all metrics from l4_packet')
    @allure.description
    @pytest.mark.medium
    def test_select_all_metrics_l4_packet(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show metrics'):
            metrics = self.get_all_metrics(api, "flow_log", "l4_packet")
            api.clear()
        with allure_step('2.select all metrics from l4_packet'):
            sql = f"select {', '.join(metrics)} from l4_packet limit 1"
            api.query_sql_api(database="flow_log", sql_cmd=sql)
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for m in metrics:
                if m not in columns:
                    logging.error(f"metrics {m} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select metrics')
    @allure.feature('flow_log')
    @allure.title('select all metrics from l7_packet')
    @allure.description
    @pytest.mark.medium
    def test_select_all_metrics_l7_packet(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show metrics'):
            metrics = self.get_all_metrics(api, "flow_log", "l7_packet")
            api.clear()
        with allure_step('2.select all metrics from l7_packet'):
            sql = f"select {', '.join(metrics)} from l7_packet limit 1"
            api.query_sql_api(database="flow_log", sql_cmd=sql)
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for m in metrics:
                if m not in columns:
                    logging.error(f"m {m} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select metrics')
    @allure.feature('flow_metrics')
    @allure.title('select all metrics from vtap_flow_edge_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_metrics_vtap_flow_edge_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show metrics'):
            metrics = self.get_all_metrics(
                api, "flow_metrics", "vtap_flow_edge_port"
            )
            api.clear()
        with allure_step('2.select all metrics from vtap_flow_edge_port'):
            sql = f"select {', '.join(metrics)} from vtap_flow_edge_port limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m",
                retries=30
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for m in metrics:
                if m not in columns:
                    logging.error(f"m {m} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select metrics')
    @allure.feature('flow_metrics')
    @allure.title('select all metrics from vtap_app_edge_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_metrics_vtap_app_edge_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show metrics'):
            metrics = self.get_all_metrics(
                api, "flow_metrics", "vtap_app_edge_port"
            )
            api.clear()
        with allure_step('2.select all metrics from vtap_app_edge_port'):
            sql = f"select {', '.join(metrics)} from vtap_app_edge_port limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m",
                retries=30
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for m in metrics:
                if m not in columns:
                    logging.error(f"m {m} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select metrics')
    @allure.feature('flow_metrics')
    @allure.title('select all metrics from vtap_flow_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_metrics_vtap_flow_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show metrics'):
            metrics = self.get_all_metrics(
                api, "flow_metrics", "vtap_flow_port"
            )
            api.clear()
        with allure_step('2.select all metrics from vtap_flow_port'):
            sql = f"select {', '.join(metrics)} from vtap_flow_port limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m",
                retries=30
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for m in metrics:
                if m not in columns:
                    logging.error(f"m {m} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('select metrics')
    @allure.feature('flow_metrics')
    @allure.title('select all metrics from vtap_app_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_metrics_vtap_app_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show metrics'):
            metrics = self.get_all_metrics(
                api, "flow_metrics", "vtap_app_port"
            )
            api.clear()
        with allure_step('2.select all metrics from vtap_app_port'):
            sql = f"select {', '.join(metrics)} from vtap_app_port limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m",
                retries=30
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for m in metrics:
                if m not in columns:
                    logging.error(f"m {m} not in result")
                    assert False

    def get_all_metrics(self, api, db, table):
        metrics = []
        api.query_sql_api(database=db, sql_cmd=f"show metrics from {table}")
        api.echo_debug_info()
        api.response_status_assert_success()
        values = api.response_json["result"]["values"]
        for value in values:
            if value[1] == True or value[4] == metrics_type_tag or value[
                4] == metrics_type_array or value[4] == metrics_type_countall:
                continue
            else:
                metrics.append(value[0])
        return metrics
