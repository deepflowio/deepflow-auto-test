# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase
#  Agent type: contain-V


class TestShowTagResource007(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('resource')
    @allure.title('resource like正常查询- 特殊字符')
    @allure.description
    @pytest.mark.medium
    def test_show_tag_resource_007(self):
        case_id = "show_tag_resource_007"
        case_name = "resource类型like查询根据特殊字符字段"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #0、Assuming that there are 100 pieces of data in the target data table
        #1、The query uses : like !
        #2、The query uses : like %
        #3、The query uses : like ?
        #4、The query uses : like .

        # Expected results:
        # Except for the 2 query to all the data, the other return results are None.

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        api.query_by_detail(
            database="flow_metrics", table="vtap_app_edge_port",
            tag="pod_group"
        )
        values = api.response_json["result"]["values"]

        # 1、The query uses : like !
        with allure_step('1、The query uses : like !'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'!'"
            )
            api.response_status_assert_success()
            api.response_values_is_None()

        # 2、The query uses : like %
        with allure_step('2、The query uses : like %'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'%'"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            api.response_values_include_specified_values(values[:])

        # 3、The query uses : like ?
        with allure_step('3、The query uses : like ?'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'!'"
            )
            api.response_status_assert_success()
            api.response_values_is_None()

        # 4、The query uses : like .
        with allure_step('4、The query uses : like .'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'.'"
            )
            api.response_status_assert_success()
            api.response_values_is_None()
