# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagIntEnum008(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('int enum')
    @allure.title('int_enum like正常查询- 特殊长度')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_int_enum_008(self):
        case_id = "show_tag_int_enum_008"
        case_name = "int_enum类型like查询根据不同长度"

        # Procedure:
        # 0、Assuming that there are 143 pieces of data in the data table
        # 1、The query uses : like (no characters, 0 length)
        # 2、The query uses : like yunshanyunshanXXXX(256 total lengths)
        # Expected results:
        # 1、Returns None
        # 2、Query to a specific data
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )

        # 1、The query uses : like (no characters, 0 length)
        with allure_step('1、The query uses : like (no characters, 0 length)'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="''"
            )
            api.response_status_assert_success()
            api.response_values_is_None()

        # 2、The query uses : like yunshanyunshanXXXX(256 total lengths)
        with allure_step(
            '2、The query uses : like yunshanyunshanXXXX(256 total lengths)'
        ):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'ARGUS (deprecated)'"
            )
            api.response_status_assert_success()
            api.response_values_equal_specified_values([[
                13, 'ARGUS (deprecated)', ''
            ]])
