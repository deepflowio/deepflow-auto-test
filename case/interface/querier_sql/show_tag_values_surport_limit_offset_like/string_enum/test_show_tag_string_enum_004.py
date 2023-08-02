# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagStringEnum004(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('string enum')
    @allure.title('string_enum limit_offset异常查询')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_string_enum_004(self):
        case_id = "show_tag_string_enum_004"
        case_name = "string_enum类型description的select_offset异常查询"

        # 0、Assuming that 17 pieces of data exist in the target data table
        # 1、use <limit 20 offset -10> query , i.e. [-10-10)
        # 2、use <limit 100 offset 10> query , i.e. [10-120)
        # 3、use <limit 20 offset 100> query , i.e. [100-120)

        # 1、Cannot retrieve data and the offset field is illegal.
        # 2、Query to the 10-max data，total max-10 items，and the value column of the returned result is in ascending order.
        # 3、Data cannot be queried and no exception is reported
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        # TODO 这里的数据需要固定下来, 有个奇怪的问题，这里综合连跑的时候会引用到int_enum的变量（直接引用的时候）
        api.query_by_detail(
            database="flow_log", table="l4_flow_log", tag="tap_side"
        )
        values = api.response_json["result"]["values"]

        with allure_step('1、use <limit 20 offset -10> query , i.e. [-10-10)'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                limit="20", offset="-10"
            )
            api.response_status_assert_fail()
            api.response_description_equal_to(
                'code: 440, message: The value -10 of OFFSET expression is not representable as UInt64'
            )
            api.response_result_is_None()

        with allure_step('2、use <limit 100 offset 10> query , i.e. [10-120)'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                limit="100", offset="10"
            )
            api.response_status_assert_success()
            api.response_values_length_equal(7)
            api.response_values_include_specified_values(values[10:])

        with allure_step('3、use <limit 20 offset 100> query , i.e. [100-120)'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                limit="20", offset="100"
            )
            api.response_status_assert_success()
            api.response_values_is_None()
