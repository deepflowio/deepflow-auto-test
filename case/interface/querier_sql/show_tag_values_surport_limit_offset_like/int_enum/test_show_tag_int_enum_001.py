# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagIntEnum001(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('int enum')
    @allure.title('int_enum limit_offset正常查询')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_int_enum_001(self):
        case_id = "show_tag_int_enum_001"
        case_name = "int_enum类型select_offset正常查询"

        # Procedure:
        # 0、Assuming that there are 143 pieces of data in the data table
        # 1、use <limit 10 offset 0> query, i.e. [0,10)
        # 2、use <limit 142 offset 0> query, i.e. [0-142)
        # 3、use <limit 10 offset 10> query, i.e. [10-20)
        # 4、use <limit 132 offset 10> query, i.e. [10-131)
        # 5、use <limit 0 offset 0> query
        # 6、use <limit 0 offset 142> query
        # Expected results:(currently not testing whether the value column of the returned result is sorted in ascending order)
        # 1、Query to the 0-9th data, total 10 items, and the value column of the returned result is in ascending order.
        # 2、Query to the 0-141th data, total 142 items, and the value column of the returned result is in ascending order.
        # 3、Query to the 10-19th data, total 10 items, and the value column of the returned result is in ascending order.
        # 4、Query to the 10-141th data, total 132 items, and the value column of the returned result is in ascending order.
        # 5、Query to the 0-0th data, total 0 items
        # 6、Query to the 0-0th data, total 0 items

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )

        # 1、use <limit 10 offset 0> query, i.e. [0-10)
        with allure_step('1、use <limit 10 offset 0> query'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="10", offset="0"
            )
            api.response_status_assert_success()
            api.response_values_length_equal(10)
            #api.response_values_equal_specified_values(values[0:10])

        # 2、use <limit 142 offset 0> query, i.e. [0-142)
        with allure_step('2、use <limit 142 offset 0> query'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="142", offset="0"
            )
            api.response_status_assert_success()
            api.response_values_length_equal(142)
            #api.response_values_equal_specified_values(values[0:142])

        # 3、use <limit 10 offset 10> query, i.e. [10-20)
        with allure_step('3、use <limit 10 offset 10> query'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="10", offset="10"
            )
            api.response_status_assert_success()
            api.response_values_length_equal(10)
            #api.response_values_equal_specified_values(values[10:20])

        # 4、use <limit 132 offset 10> query, i.e. [10-141)
        with allure_step('4、use <limit 132 offset 10> query'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="132", offset="10"
            )
            api.response_status_assert_success()
            api.response_values_length_equal(132)
            #api.response_values_equal_specified_values(values[10:142])

        # 5、use <limit 0 offset 0> query, i.e. [0-0)
        with allure_step('5、use <limit 0 offset 0> query, return None'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="0", offset="0"
            )
            api.response_status_assert_success()
            api.response_values_is_None()

        # 6、use <limit 0 offset 142> query, i.e. [100-100)
        with allure_step('6、use <limit 0 offset 142> query, return None'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="0", offset="142"
            )
            api.response_status_assert_success()
            api.response_values_is_None()
