# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagStringEnum009(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('string enum')
    @allure.title('string_enum like正常查询- 特殊字符')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_string_enum_009(self):
        case_id = "show_tag_string_enum_009"
        case_name = "string_enum类型like查询根据特殊字符字段"

        # Procedure:
        #0、Assuming that there are 100 pieces of data in the target data table
        #1、The query uses : like !
        #2、The query uses : like %
        #3、The query uses : like ?
        #4、The query uses : like .

        # Expected results:
        # Returns None

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        # 1、The query uses : like !
        with allure_step('1、The query uses : like !'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'客户端网!'"
            )
            api.response_status_assert_success()
            api.response_values_is_None()

        # 2、The query uses : like %
        with allure_step('1、The query uses : like !'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'客户端网%'"
            )
            api.response_status_assert_success()
            api.response_values_is_None()

        # 3、The query uses : like ?
        with allure_step('3、The query uses : like ?'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'客户端网?'"
            )
            api.response_status_assert_success()
            api.response_values_is_None()

        # 4、The query uses : like .
        with allure_step('4、The query uses : like .'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'客户端网.'"
            )
            api.response_status_assert_success()
            api.response_values_is_None()
