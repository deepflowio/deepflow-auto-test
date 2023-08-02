# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagStringEnum011(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('string enum')
    @allure.title('string_enum limit_offset、like正常查询- *')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_string_enum_011(self):
        case_id = "show_tag_string_enum_011"
        case_name = "string_enum类型like交叉limit和offset"

        # Procedure:
        #0、Assuming that there are 100 pieces of data in the target data table
        #1、The query uses : limit 10 offset 10 like ab
        #2、The query uses : limit 5 offset 5 like *ab*

        # Expected results:
        #1-2、return specific data when a query field matches database data

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        # 1、The query uses : limit 10 offset 0 like ab
        with allure_step('1、The query uses : limit 10 offset 0 like ab'):

            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                limit="10", offset="0", like="'Client NIC'"
            )
            api.response_status_assert_success()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])

        # 2、The query uses : limit 10 offset 0 like ab
        with allure_step('2、The query uses : limit 10 offset 0 like ab'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                limit="10", offset="0", like="'Client NIC'"
            )
            api.response_status_assert_success()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])
