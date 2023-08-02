# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagIntEnum002(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('int enum')
    @allure.title('int_enum limit_offset异常查询')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_int_enum_002(self):
        case_id = "show_tag_int_enum_002"
        case_name = "int_enum类型select_offset异常查询"

        # Procedure:
        # 0、Assuming that there are 143 pieces of data in the data table
        # 1、use <limit 20 offset -10> query
        # 2、use <limit 200 offset 20> query, 即[20-142)
        # 3、use <limit 20 offset 210> query
        # Expected results:
        # 1、Cannot retrieve data and the offset field is illegal.
        # 2、Query to the 20-142th data, total 123 items
        # 3、Data cannot be queried and no exception is reported

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )

        with allure_step('1、use <limit 20 offset -10> query'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="20", offset="-10"
            )
            api.response_status_assert_fail()
            api.response_description_equal_to(
                'code: 440, message: The value -10 of OFFSET expression is not representable as UInt64'
            )
            api.response_result_is_None()

        with allure_step('2、use <limit 100 offset 20> query'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="200", offset="20"
            )
            api.response_status_assert_success()
            api.response_values_length_equal(123)
            api.response_values_equal_specified_values(values[20:143])

        with allure_step('3、use <limit 20 offset 110> query'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="20", offset="210"
            )
            api.response_status_assert_success()
            api.response_values_is_None()
