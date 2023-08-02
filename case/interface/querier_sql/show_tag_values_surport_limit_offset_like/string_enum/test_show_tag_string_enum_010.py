# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagStringEnum010(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('string enum')
    @allure.title('string_enum like正常查询- 特殊长度')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_string_enum_010(self):
        case_id = "show_tag_string_enum_010"
        case_name = "string_enum类型like查询根据不同长度"

        # Procedure:
        #0、Assuming that there are 100 pieces of data in the target data table
        #1、The query uses : like (no characters, 0 length)
        #2、The query uses : like yunshanyunshanXXXX(256 total lengths)

        # Expected results:
        #1、Returns None

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        # 1、The query uses : like (no characters, 0 length)
        with allure_step('1、The query uses : like (no characters, 0 length)'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like=""
            )
            api.response_status_assert_fail()
            api.response_description_contains('syntax error at position')
            api.response_result_is_None()

        # 2、The query uses : like yunshanyunshanXXXX(256 total lengths)
        # TODO 目前需要构造数据才能测试256长度的字段
