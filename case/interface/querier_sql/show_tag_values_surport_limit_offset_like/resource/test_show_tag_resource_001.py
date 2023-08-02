# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase
#  Agent type: contain-V


class TestShowTagResource001(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('resource')
    @allure.title('resource limit_offset正常查询')
    @allure.description
    @pytest.mark.medium
    def test_show_tag_resource_001(self):
        case_id = "show_tag_resource_001"
        case_name = "resource类型limit_offset正常查询"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #0、Assuming that 17 pieces of data exist in the target data table
        #1、use <limit 10 offset 0> query , i.e. [0,10)
        #2、use <limit 17 offset 0> query , i.e. [0-17)
        #3、use <limit 10 offset 2> query , i.e. [2-12)
        #4、use <limit 10 offset 7> query , i.e. [7-17)
        #5、use <limit 0 offset 0> query , i.e. (0-0)
        #6、use <limit 0 offset 17> query , i.e. [17-17)

        # Expected results:
        #1、Query to the 0-9th data, total 10 items, and the value column of the returned result is in ascending order.
        #2、Query to the 0-17th data, total 17 items, and the value column of the returned result is in ascending order.
        #3、Query to the 2-12th data, total 10 items, and the value column of the returned result is in ascending order.
        #4、Query to the 7-17th data, total 10 items, and the value column of the returned result is in ascending order.
        #5、Query to the 0-0th data, total 0 items
        #6、Query to the 17-17th data, total 0 items

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        api.query_by_detail(
            database="flow_metrics",
            table="vtap_app_edge_port",
            tag="pod_group",
        )
        # The value of values is overwritten
        values = api.response_json["result"]["values"]  

        # 1、use <limit 10 offset 0> query , i.e. [0,10)
        with allure_step('1、use <limit 10 offset 0> query , i.e. [0,10)'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", limit="10", offset="0"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            api.response_values_length_equal(10)
            api.response_values_equal_specified_values(values[0:10])

        # 2、use <limit 17 offset 0> query , i.e. [0-17)
        with allure_step('2、use <limit 17 offset 0> query , i.e. [0-17)'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", limit="{}".format(len(values)), offset="0"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            api.response_values_length_equal(len(values))
            api.response_values_equal_specified_values(values[:])

        # 3、use <limit 10 offset 2> query , i.e. [2-12)
        with allure_step('3、use <limit 10 offset 2> query , i.e. [2-12)'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", limit="10", offset="2"
            )
            api.response_status_assert_success()
            api.response_values_length_equal(10)
            api.response_values_include_specified_values(values[2:12])

        # 4、use <limit 10 offset 7> query , i.e. [7-17)
        with allure_step('4、use <limit 10 offset 7> query , i.e. [7-17)'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", limit="{}".format(len(values)), offset="10"
            )
            api.response_status_assert_success()
            api.response_values_length_equal(len(values) - 10)
            api.response_values_include_specified_values(values[10:])

        # 5、use <limit 0 offset 0> query , i.e. (0-0)
        with allure_step('5、use <limit 0 offset 0> query , i.e. (0-0)'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", limit="0", offset="0"
            )
            api.response_status_assert_success()
            api.response_values_is_None()

        # 6、use <limit 0 offset 17> query , i.e. [17-17)
        with allure_step('6、use <limit 0 offset 17> query , i.e. [17-17)'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", limit="{}".format(len(values)),
                offset="{}".format(len(values))
            )
            api.response_status_assert_success()
            api.response_values_is_None()
