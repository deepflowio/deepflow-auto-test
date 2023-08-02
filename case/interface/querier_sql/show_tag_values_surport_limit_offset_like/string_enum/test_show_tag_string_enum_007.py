# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagStringEnum007(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('string enum')
    @allure.title('string_enum like正常查询- _')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_string_enum_007(self):
        case_id = "show_tag_string_enum_007"
        case_name = "string_enum类型like查询根据下划线位置"

        # Procedure:
        # 0、Assuming that there are 100 pieces of data in the target data table
        # 1、The query uses : like ab
        # 2、The query uses : like _ab
        # 3、The query uses : like a_b
        # 4、The query uses : like ab_"

        # Expected results:
        #1-4、return specific data when a query field matches database data

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )

        # 1、The query uses : like ab
        with allure_step('1、The query uses : like ab'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'Client NIC'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])

        # 2、The query uses : like _ab
        with allure_step('2、The query uses : like _ab'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'_lient NIC'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])

        # 3、The query uses : like a_b
        with allure_step('3、The query uses : like a_b'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'Client_NIC'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])

        # 4、The query uses : like ab_"
        with allure_step('4、The query uses : like ab_'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'Client NI_'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])
