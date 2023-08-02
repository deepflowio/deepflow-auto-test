# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
import logging
from common.querier_api_utils import QueryApi
from case.interface.querier_sql.base import QuerierSqlBaseCase, edge_table_names

enum_tag_types = ["int_enum", "string_enum"]


class TestEnumAllTags(QuerierSqlBaseCase):

    @staticmethod
    def get_enum_tags(api, db, table):
        tags = []
        api.query_sql_api(database=db, sql_cmd=f"show tags from {table}")
        api.echo_debug_info()
        api.response_status_assert_success()
        values = api.response_json["result"]["values"]
        for value in values:
            if value[4] not in enum_tag_types:
                continue
            # Tag that doesn't support SELECT but only WHERE
            if value[0] in ["lb_listener", "pod_ingress"]:
                continue
            if table in edge_table_names and value[0] != value[1]:
                tags.append(f"`{value[1]}`")

                tags.append(f"`{value[2]}`")
            else:
                tags.append(f"`{value[0]}`")
        return tags

    @allure.suite('API test')
    @allure.epic('enum tags')
    @allure.feature('flow_log')
    @allure.title('enum all tags from l4_flow_log')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_l4_flow_log(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_enum_tags(api, "flow_log", "l4_flow_log")
            api.clear()
            enum_tags = [f"Enum({tag})" for tag in tags]
            enum_as_tag = [
                f"Enum({tag}) AS enum_{tag.replace('`','')}" for tag in tags
            ]
            as_tag = [f"enum_{tag.replace('`','')}" for tag in tags]
        with allure_step('2.enum all tags from l4_flow_log'):
            sql = f"select {', '.join(enum_as_tag)}, Max(byte) as max_byte from l4_flow_log group by {', '.join(as_tag)} limit 1"
            api.query_sql_loop_values(database="flow_log", sql_cmd=sql)
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in as_tag:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('enum tags')
    @allure.feature('flow_log')
    @allure.title('enum all tags from l7_flow_log')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_l7_flow_log(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_enum_tags(api, "flow_log", "l7_flow_log")
            api.clear()
            enum_tags = [f"Enum({tag})" for tag in tags]
            enum_as_tag = [
                f"Enum({tag}) AS enum_{tag.replace('`','')}" for tag in tags
            ]
            as_tag = [f"enum_{tag.replace('`','')}" for tag in tags]
        with allure_step('2.enum all tags from l7_flow_log'):
            sql = f"select {', '.join(enum_as_tag)}, Max(request) as max_request from l7_flow_log group by {', '.join(as_tag)} limit 1"
            api.query_sql_loop_values(database="flow_log", sql_cmd=sql)
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in as_tag:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('enum tags')
    @allure.feature('flow_metrics')
    @allure.title('enum all tags from vtap_flow_edge_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_vtap_flow_edge_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_enum_tags(
                api, "flow_metrics", "vtap_flow_edge_port"
            )
            api.clear()
            enum_tags = [f"Enum({tag})" for tag in tags]
            enum_as_tag = [
                f"Enum({tag}) AS enum_{tag.replace('`','')}" for tag in tags
            ]
            as_tag = [f"enum_{tag.replace('`','')}" for tag in tags]
        with allure_step(
            '2.select Max(byte) enum all tags from vtap_flow_edge_port'
        ):
            sql = f"select {', '.join(enum_as_tag)}, Max(byte) as max_byte from vtap_flow_edge_port group by {', '.join(as_tag)} limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in as_tag:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False
        with allure_step(
            '3.select Sum(byte) enum all tags from vtap_flow_edge_port'
        ):
            sql = f"select {', '.join(enum_as_tag)}, Sum(byte) as sum_byte from vtap_flow_edge_port group by {', '.join(as_tag)} limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in as_tag:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('enum tags')
    @allure.feature('flow_metrics')
    @allure.title('enum all tags from vtap_app_edge_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_vtap_app_edge_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_enum_tags(
                api, "flow_metrics", "vtap_app_edge_port"
            )
            api.clear()
            enum_tags = [f"Enum({tag})" for tag in tags]
            enum_as_tag = [
                f"Enum({tag}) AS enum_{tag.replace('`','')}" for tag in tags
            ]
            as_tag = [f"enum_{tag.replace('`','')}" for tag in tags]
        with allure_step(
            '2.select Max(request) enum all tags from vtap_app_edge_port'
        ):
            sql = f"select {', '.join(enum_as_tag)}, Max(request) as max_request from vtap_app_edge_port group by {', '.join(as_tag)} limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in as_tag:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False
        with allure_step(
            '3.select Sum(request) enum all tags from vtap_app_edge_port'
        ):
            sql = f"select {', '.join(enum_as_tag)}, Sum(request) as sum_request from vtap_app_edge_port group by {', '.join(as_tag)} limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in as_tag:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('enum tags')
    @allure.feature('flow_metrics')
    @allure.title('enum all tags from vtap_flow_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_vtap_flow_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_enum_tags(api, "flow_metrics", "vtap_flow_port")
            api.clear()
            enum_tags = [f"Enum({tag})" for tag in tags]
            enum_as_tag = [
                f"Enum({tag}) AS enum_{tag.replace('`','')}" for tag in tags
            ]
            as_tag = [f"enum_{tag.replace('`','')}" for tag in tags]
        with allure_step(
            '2.select Max(byte) enum all tags from vtap_flow_port'
        ):
            sql = f"select {', '.join(enum_as_tag)}, Max(byte) as max_byte from vtap_flow_port group by {', '.join(as_tag)} limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in as_tag:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False
        with allure_step(
            '3.select Sum(byte) enum all tags from vtap_flow_port'
        ):
            sql = f"select {', '.join(enum_as_tag)}, Sum(byte) as sum_byte from vtap_flow_port group by {', '.join(as_tag)} limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in as_tag:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False

    @allure.suite('API test')
    @allure.epic('enum tags')
    @allure.feature('flow_metrics')
    @allure.title('enum all tags from vtap_app_port')
    @allure.description
    @pytest.mark.medium
    def test_select_all_tags_vtap_app_port(self):
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('1.show tags'):
            tags = self.get_enum_tags(api, "flow_metrics", "vtap_app_port")
            api.clear()
            enum_tags = [f"Enum({tag})" for tag in tags]
            enum_as_tag = [
                f"Enum({tag}) AS enum_{tag.replace('`','')}" for tag in tags
            ]
            as_tag = [f"enum_{tag.replace('`','')}" for tag in tags]
        with allure_step(
            '2.select Max(request) enum all tags from vtap_app_port'
        ):
            sql = f"select {', '.join(enum_as_tag)}, Max(request) as max_request from vtap_app_port group by {', '.join(as_tag)} limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in as_tag:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False
        with allure_step(
            '2.select Sum(request) enum all tags from vtap_app_port'
        ):
            sql = f"select {', '.join(enum_as_tag)}, Sum(request) as Sum_request from vtap_app_port group by {', '.join(as_tag)} limit 1"
            api.query_sql_loop_values(
                database="flow_metrics", sql_cmd=sql, data_precision="1m"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            columns = api.response_json["result"]["columns"]
            for tag in as_tag:
                tag = tag.strip("`")
                if tag not in columns:
                    logging.error(f"tag {tag} not in result")
                    assert False
