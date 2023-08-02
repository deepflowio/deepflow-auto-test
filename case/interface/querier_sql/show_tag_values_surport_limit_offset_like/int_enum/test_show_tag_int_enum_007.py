# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagIntEnum007(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('int enum')
    @allure.title('int_enum like正常查询- 特殊字符')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_int_enum_007(self):
        case_id = "show_tag_int_enum_007"
        case_name = "int_enum类型like查询根据特殊字符字段"

        # Procedure:
        # 0、Assuming that there are 143 pieces of data in the data table
        # 1、The query uses : like !
        # 2、The query uses : like %
        # 3、The query uses : like ?
        # 4、The query uses : like ."
        # Expected results:
        # 1、2 Return all data, but the value field is disordered.
        # 2、1 and 3-4 return result is None,
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        # 1、The query uses : like !
        with allure_step('1、The query uses : like !'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'!'"
            )
            api.response_status_assert_success()
            api.response_values_is_None()

        # 2、The query uses : like % (返回结果value字段不再正向排序)
        ''' with allure_step('2、The query uses : like %'):
            api.query_by_detail(database="flow_metrics",
                                table="vtap_app_edge_port",
                                tag="protocol",
                                like="'%'")
            api.response_status_assert_success()
            api.response_values_include_specified_values(values[:]) '''

        # 3、The query uses : like ?
        with allure_step('3、The query uses : like ?'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'?'"
            )
            api.response_status_assert_success()
            api.response_values_is_None()

        # 4、The query uses : like .
        with allure_step('4、The query uses : like .'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'.'"
            )
            api.response_status_assert_success()
            api.response_values_is_None()
