# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagIntEnum006(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('int enum')
    @allure.title('int_enum like正常查询- 大小写字母')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_int_enum_006(self):
        case_id = "show_tag_int_enum_006"
        case_name = "int_enum类型like查询根据字母大小写"

        # Procedure:
        # 0、Assuming that there are 143 pieces of data in the data table
        # 1、The query uses : like AB
        # 2、The query uses : like ab
        # 3、The query uses : like Ab
        # 4、The query uses : like aB

        # Expected results:
        # 1-4、return specific data when a query field matches database data

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )

        # 1、The query uses : like ab
        with allure_step('1、The query uses : like AB'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'DCN-MEAS'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 2、The query uses : like AB
        with allure_step('2、The query uses : like ab'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'dcn-meas'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 3、The query uses : like Ab
        with allure_step('3、The query uses : like Ab'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'DCN-meas'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 4、The query uses : like aB"
        with allure_step('4、The query uses : like aB'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'dcn-MEAS'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])
