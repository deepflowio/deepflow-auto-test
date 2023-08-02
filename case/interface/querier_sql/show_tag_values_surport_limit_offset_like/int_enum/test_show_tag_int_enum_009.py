# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagIntEnum009(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('int enum')
    @allure.title('int_enum limit_offset、like正常查询- *')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_int_enum_009(self):
        case_id = "show_tag_int_enum_009"
        case_name = "int_enum类型like交叉limit和offset"

        # Procedure:
        # 0、Assuming that there are 143 pieces of data in the data table
        # 1、The query uses : select 10 offset 10 like ab
        # 2、The query uses : select 5 offset 5 like *ab*"
        # Expected results:
        # 1-2、return specific data when a query field matches database data
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )

        # 1、The query uses : limit 100 offset 0 like ab
        with allure_step('1、The query uses : like ab and limit 100 offset 10'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="100", offset="0", like="'DCN-MEAS'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 2、The query uses : limit 100 offset 0 like *ab*"
        with allure_step(
            '2、The query uses : like *ab* and limit 100 offset 10'
        ):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="100", offset="0", like="'*CN-MEA*'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])

        # 3、The query uses : limit 100 offset 0 like *ab*"
        with allure_step(
            '3、The query uses : like *ab* and limit 100 offset 10'
        ):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="protocol", limit="100", offset="0", like="'*CN-MEAS*'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[19, 'DCN-MEAS', '']])
