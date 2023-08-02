# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagIntEnum003(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('int enum')
    @allure.title('int_enum sql注入')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_int_enum_003(self):
        case_id = "show_tag_int_enum_003"
        case_name = "int_enum类型sql注入"

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        # Procedure:
        # 1、Add illegal fields to each parameter <;show databases>

        # Expected results:
        # 1、Execution to fail with reasonable warning and without exposing system information
        with allure_step('XX limit 20 offset 20; show databases'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="20", offset="20; show databases"
            )
            api.response_status_assert_fail()
            api.response_description_contains("syntax error at position")
            api.response_result_is_None()

        with allure_step('XX limit 20; show databases offset 20'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="20; show databases;", offset="20"
            )
            api.response_status_assert_fail()
            api.response_description_contains("syntax error at position")
            api.response_result_is_None()

        with allure_step('XX ; show databases limit 20 offset 20'):
            api.query_by_detail(
                database="flow_metrics",
                table="vtap_app_edge_port; show databases;", tag="protocol",
                limit="20;", offset="20"
            )
            api.response_status_assert_fail()
            api.response_description_equal_to(
                'no tag protocol in flow_metrics.vtap_app_edge_port;'
            )
            api.response_result_is_None()

        with allure_step('XXlike ab; show databases limit 20 offset 20 '):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="20;", offset="20",
                like="'ab; show databases;'"
            )
            api.echo_debug_info()
            api.response_status_assert_fail()
            api.response_description_contains('syntax error at position')
            api.response_result_is_None()
