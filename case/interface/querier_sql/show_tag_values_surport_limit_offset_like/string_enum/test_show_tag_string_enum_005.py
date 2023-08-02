# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagStringEnum005(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('string enum')
    @allure.title('string_enum sql注入')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_string_enum_005(self):
        case_id = "show_tag_string_enum_005"
        case_name = "string_enum类型sql注入"

        # Procedure:
        # 0、Assuming that there are 100 pieces of data in the target data table
        # 1、Use the query for the target data table: XX limit 20 offset 20; show databases"
        # 2、Use the query for the target data table: show XX;show XX;

        # Expected results:
        # 1、Expect execution to fail with reasonable warning and without exposing system information
        # 2、Expect execution to fail with reasonable warning and without exposing system information

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )

        with allure_step(
            '1、Use the query for the target data table: XX limit 5 offset 5; show databases"'
        ):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                limit="5", offset="5; show databases"
            )
            api.response_status_assert_fail()
            api.response_description_contains("syntax error at position")
            api.response_result_is_None()

        with allure_step(
            '2、Use the query for the target data table: show XX;show XX;'
        ):
            api.query_sql_api(
                database="flow_log", sql_cmd=
                "show tag tap_side from l4_flow_log limit 5 offset 5; show tag tap_side from l4_flow_log limit 5 offset 5;"
            )
            api.response_status_assert_fail()
            api.response_description_equal_to(
                "parse show sql error, sql: 'show tag tap_side from l4_flow_log limit 5 offset 5; show tag tap_side from l4_flow_log limit 5 offset 5;' not support"
            )
            api.response_result_is_None()
