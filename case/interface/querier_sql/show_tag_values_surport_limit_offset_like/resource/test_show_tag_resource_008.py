# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase
#  Agent type: contain-V


class TestShowTagResource008(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('resource')
    @allure.title('resource like正常查询- 特殊长度')
    @allure.description
    @pytest.mark.medium
    def test_show_tag_resource_008(self):
        case_id = "show_tag_resource_008"
        case_name = "resource类型like查询根据不同长度"

        # Precondition operation:
        #1、Agent deployment complete
        #2、Environmental docking completed
        #3、Packets and data exist on the default environment that satisfy the test conditions

        # Procedure:
        #0、Assuming that there are 100 pieces of data in the target data table
        #1、The query uses : like (no characters, 0 length)
        #2、The query uses : like yunshanyunshanXXXX(256 total lengths)

        # Expected results:
        #1-2、Returns None

        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )

        # 1、The query uses : like (no characters, 0 length)
        with allure_step('1、The query uses : like (no characters, 0 length)'):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like="''"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            api.response_values_is_None()

        # 2、The query uses : like yunshanyunshanXXXX(256 total lengths)
        with allure_step(
            '2、The query uses : like yunshanyunshanXXXX(256 total lengths)'
        ):
            api.query_by_detail(
                database="flow_metrics", table="vtap_app_edge_port",
                tag="pod_group", like=
                "'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbb"
                "ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
                "ddddddddddddddddddddddddddddddddddddddddeeeeeeeeeeeeeeeeeeee"
                "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                "ddddddddddddddddddddddddddddddddddddddddeeeeeeeeeeeeeeeeeeee"
                "ddddddddddddddddddddddddddddddddddddddddeeeeeeeeeeeeeeeeeeee"
                "ddddddddddddddddddddddddddddddddddddddddeeeeeeeeeeeeeeeeeeee"
                "ddddddddddddddddddddddddddddddddddddddddeeeeeeeeeeeeeeeeeeee"
                "ddddddddddddddddddddddddddddddddddddddddeeeeeeeeeeeeeeeeeeee"
                "ddddddddddddddddddddddddddddddddddddddddeeeeeeeeeeeeeeeeeeee"
                "ddddddddddddddddddddddddddddddddddddddddeeeeeeeeeeeeeeeeeeee"
                "ddddddddddddddddddddddddddddddddddddddddeeeeeeeeeeeeeeeeeeee"
                "ddddddddddddddddddddddddddddddddddddddddeeeeeeeeeeeeeeeeeeee'"
            )
            api.echo_debug_info()
            api.response_status_assert_success()
            api.response_values_is_None()
