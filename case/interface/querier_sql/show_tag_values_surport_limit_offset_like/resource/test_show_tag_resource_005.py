# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase
#  Agent type: contain-V


class TestShowTagResource005(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('resource')
    @allure.title('resource like正常查询- _')
    @allure.description
    @pytest.mark.medium
    def test_show_tag_resource_005(self):
        case_id = "show_tag_resource_005"
        case_name = "resource类型like查询根据下划线位置"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #1、Queries without like
        #2、The query uses : like ab
        #3、The query uses : like _ab
        #4、The query uses : like a_b
        #5、The query uses : like ab_

        # Expected results:
        #1-5、return specific data when a query field matches database data

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        # 1、Queries without like
        with allure_step('1、Queries without like'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 2、The query uses : like ab
        with allure_step('2、The query uses : like ab'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'deepflow-server'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 3、The query uses : like _ab
        with allure_step('3、The query uses : like _ab'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'_eepflow-server'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 4、The query uses : like a_b
        with allure_step('4、The query uses : like a_b'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'deepflow_server'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 5、The query uses : like ab_
        with allure_step('5、The query uses : like ab_'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'deepflow-serve_'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )
