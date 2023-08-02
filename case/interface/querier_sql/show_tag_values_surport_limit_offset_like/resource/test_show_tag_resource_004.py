# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase
#  Agent type: contain-V


class TestShowTagResource004(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('resource')
    @allure.title('resource like正常查询- * ')
    @allure.description
    @pytest.mark.medium
    def test_show_tag_resource_004(self):
        case_id = "show_tag_resource_004"
        case_name = "resource类型like查询根据星号位置"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        # 0、Assuming that there are 100 pieces of data in the target data table
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
        # Expected results:
        # 1-10、return specific data when a query field matches database data

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )

        # 1、The query uses : like ab
        with allure_step('1、The query uses : like ab'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'deepflow-server'"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 2、The query uses : like *ab
        with allure_step('2、The query uses : like *ab'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'*eepflow-server'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 3、The query uses : like a*b
        with allure_step('3、The query uses : like a*b'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'deepflow*server'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 4、The query uses : like ab*
        with allure_step('4、The query uses : like ab*'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'deepflow-serve*'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 5、The query uses : like **ab
        with allure_step('5、The query uses : like **ab'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'**epflow-server'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 6、The query uses : like a**b
        with allure_step('6、The query uses : like a**b'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'deepflow**erver'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 7、The query uses : like ab**
        with allure_step('7、The query uses : like ab**'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'deepflow-serv**'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 8、The query uses : like *a*b
        with allure_step('8、The query uses : like *a*b'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'*eepflow*server'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 9、The query uses : like a*b*
        with allure_step('9、The query uses : like a*b*'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'deepflow*serve*'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 10、The query uses : like *a*b*
        with allure_step('10、The query uses : like *a*b*'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'*eepflow*serve*'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )
