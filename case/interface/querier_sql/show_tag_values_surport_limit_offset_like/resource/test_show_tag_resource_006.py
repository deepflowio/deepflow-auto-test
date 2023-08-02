# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase
#  Agent type: contain-V


class TestShowTagResource006(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('resource')
    @allure.title('resource like正常查询- 大小写字母')
    @allure.description
    @pytest.mark.medium
    def test_show_tag_resource_006(self):
        case_id = "show_tag_resource_006"
        case_name = "resource类型like查询根据字母大小写"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #0、Assuming that there are 100 pieces of data in the target data table
        #1、The query uses : like ab
        #2、The query uses : like AB
        #3、The query uses : like Ab
        #4、The query uses : like aB

        # Expected results:
        #1-4、return specific data when a query field matches database data

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        # 1、The query uses : like ab
        with allure_step('1、The query uses : like ab'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'deepflow-server'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 2、The query uses : like AB
        with allure_step('2、The query uses : like AB'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'DEEPFLOW-SERVER'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 3、The query uses : like Ab
        with allure_step('3、The query uses : like Ab'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'DEEPFLOW-server'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 4、The query uses : like aB
        with allure_step('4、The query uses : like aB'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="'deepflow-SERVER'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )
