# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from case.interface.querier_sql.base import QuerierSqlBaseCase

#  Agent type: contain-V


class TestShowTagResource009(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('resource')
    @allure.title('resource limit_offset、like正常查询- *')
    @allure.description
    @pytest.mark.medium
    def test_show_tag_resource_009(self):
        case_id = "show_tag_resource_009"
        case_name = "resource类型like交叉limit和offset"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #0、Assuming that there are 100 pieces of data in the target data table
        #1、The query uses : limit 10 offset 10 like ab
        #2、The query uses : limit 5 offset 5 like *ab*

        # Expected results:
        #1-2、return specific data when a query field matches database data

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        api.query_by_detail(
            database="flow_metrics", table="vtap_app_edge_port",
            tag="pod_group"
        )
        values = api.response_json["result"]["values"]

        # 1、The query uses : limit 2 offset 0 like ab
        with allure_step('1、The query uses : like *ab* and limit 2 offset 0'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", limit=2, offset=0, like="'deepflow-server'"
            )
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )

        # 2、The query uses : limit 2 offset 0 like *ab*
        with allure_step('2、The query uses : like *ab* and limit 2 offset 0'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", limit=2, offset=0, like="'*eepflow-serve*'"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            api.is_specified_column_contain_specified_value(
                "display_name", "deepflow-server"
            )
