# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagIntEnum004(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('int enum')
    @allure.title('int_enum like正常查询- *')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_int_enum_004(self):
        case_id = "show_tag_int_enum_004"
        case_name = "int_enum类型like查询根据星号位置"

        # Procedure:
        # 0、Assuming that 140 pieces of data exist in the target data table
        # 1、The query uses : like ab
        # 2、The query uses : like *ab
        # 3、The query uses : like a*b
        # 4、The query uses : like ab*
        # 5、The query uses : like **ab
        # 6、The query uses : like a**b
        # 7、The query uses : like ab**
        # 8、The query uses : like *a*b
        # 9、The query uses : like a*b*
        # 10、The query uses : like *a*b*
        # 11、The query uses : like a*b*c
        # 12、The query uses : like *a*b*c
        # Expected results:
        # 1-12、return specific data when a query field matches database data

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )

        # 1、The query uses : like ab
        with allure_step('1、The query uses : like ab'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'DCN-MEAS'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 2、The query uses : like *ab
        with allure_step('2、The query uses : like *ab'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'*N-MEAS'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 3、The query uses : like a*b
        with allure_step('3、The query uses : like a*b'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'DCN*MEAS'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 4、The query uses : like ab*
        with allure_step('4、The query uses : like ab*'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'DCN-MEA*'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 5、The query uses : like **ab
        with allure_step('5、The query uses : like **ab'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'**N-MEAS'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 6、The query uses : like a**b
        with allure_step('6、The query uses : like a**b'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'DC**MEAS'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 7、The query uses : like ab**
        with allure_step('7、The query uses : like ab**'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'DCN-ME**'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 8、The query uses : like *a*b
        with allure_step('8、The query uses : like *a*b'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'*C*-MEAS'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 9、The query uses : like a*b*
        with allure_step('9、The query uses : like a*b*'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'DC*-MEA*'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 10、The query uses : like *a*b*
        with allure_step('10、The query uses : like *a*b*'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'*C*-MEA*'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 11、The query uses : like a*b*c
        with allure_step('11、The query uses : like a*b*c'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'DC*-ME*S'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 12、The query uses : like *a*b*c
        with allure_step('12、The query uses : like *a*b*c'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", like="'*C*-ME*S'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])
