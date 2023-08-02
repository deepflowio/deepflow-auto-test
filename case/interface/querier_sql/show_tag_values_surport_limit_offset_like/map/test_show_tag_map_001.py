# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from case.interface.querier_sql.base import QuerierSqlBaseCase

#  Agent type: contain-V


class TestShowTagMap001(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('map')
    @allure.title('map 正常查询')
    @allure.description
    @pytest.mark.medium
    def test_show_tag_map_001(self):
        case_id = "show_tag_map_001"
        case_name = "map类型的正常查询"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        # 1、use <show tag tag.host values from deepflow_agent_collect_sender> query, database=deepflow_system

        # Expected results:
        #1、Response status is SUCCESS

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )
        # 1、use <show tag tag.host values from deepflow_agent_collect_sender> query, database=deepflow_system
        with allure_step(
            '1、use <show tag chost values from vtap_app_edge_port> query'
        ):
            api.query_by_detail(
                database="deepflow_system",
                table="vtap_app_edge_port",
                tag="tag.host",
            )
            api.echo_debug_info()
            api.response_status_assert_success()
