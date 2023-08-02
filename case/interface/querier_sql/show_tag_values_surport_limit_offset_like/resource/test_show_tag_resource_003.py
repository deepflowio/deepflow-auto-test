# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase
#  Agent type: contain-V


class TestShowTagResource003(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('resource')
    @allure.title('resource sql注入')
    @allure.description
    @pytest.mark.medium
    def test_show_tag_resource_003(self):
        case_id = "show_tag_resource_003"
        case_name = "resource类型sql注入"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #1、Insert the string "; show databases" for the limit and offset parameters.

        # Expected results:
        #1、Expect execution to fail with reasonable warning and without exposing system information

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        with allure_step('limit parameter insertion"; show databases"'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", limit="20; show databases", offset="10"
            )
            api.echo_debug_info()
            api.response_status_assert_fail()
            api.response_description_equal_to(
                "syntax error at position 125 near 'show'"
            )

        with allure_step('offset parameter insertion"; show databases"'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", limit="20", offset="10; show databases"
            )
            api.echo_debug_info()
            api.response_status_assert_fail()
            api.response_description_equal_to(
                "syntax error at position 135 near 'show'"
            )
