# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase
#  Agent type: contain-V


class TestShowTagResource002(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('resource')
    @allure.title('resource limit_offset异常查询')
    @allure.description
    @pytest.mark.medium
    def test_show_tag_resource_002(self):
        case_id = "show_tag_resource_002"
        case_name = "resource类型select_offset异常查询"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #0、Assuming that 17 pieces of data exist in the target data table
        #1、use <limit 20 offset -10> query , i.e. [-10-10)
        #2、use <limit 10000 offset 10> query , i.e. [10-10000)
        #3、use <limit 10000 offset 10000> query , i.e. [10000-20000)
        #

        # Expected results:
        #1、Cannot retrieve data and the offset field is illegal.
        #2、Query to the 10-max data，total (max-10) items，and the value column of the returned result is in ascending order.
        #3、Data cannot be queried and no exception is reported

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        api.query_by_detail(
            database="flow_metrics",
            table="vtap_app_edge_port",
            tag="pod_group",
        )
        values = api.response_json["result"]["values"]

        # 1、use <limit 20 offset -10> query , i.e. [-10-10)
        with allure_step('1、use <limit 20 offset -10> query , i.e. [-10-10)'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", limit="20", offset="-10"
            )
            api.response_status_assert_fail()
            api.response_description_equal_to(
                "code: 440, message: The value -10 of OFFSET expression is not representable as UInt64"
            )

        # 2、use <limit 10000 offset 10> query , i.e. [10-10000)
        with allure_step(
            '2、use <limit 10000 offset 10> query , i.e. [10-10000)'
        ):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", limit="10000", offset="10"
            )
            api.response_status_assert_success()
            api.response_values_length_equal(len(values) - 10)
            api.response_values_include_specified_values(values[10:])

        # 3、use <limit 10000 offset 10000> query, i.e. [10000-20000)
        with allure_step(
            '3、use <limit 20 offset 110> query , i.e. [10000-10000)'
        ):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", limit="10000", offset="10000"
            )
            api.response_status_assert_success()
            api.response_values_is_None()
