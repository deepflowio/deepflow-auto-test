# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagStringEnum008(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('string enum')
    @allure.title('string_enum like正常查询- 大小写字母')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_string_enum_008(self):
        case_id = "show_tag_string_enum_008"
        case_name = "string_enum类型like查询根据字母大小写"

        # 0、Assuming that there are 100 pieces of data in the target data table
        # 1、The query uses : like ab
        # 2、The query uses : like _ab
        # 3、The query uses : like a_b
        # 4、The query uses : like ab_

        # Expected results:
        # 1-4、return specific data when a query field matches database data
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )

        # 0、Assuming that there are 100 pieces of data in the target data table
        # 1、The query uses : like ab
        # TODO 目前这个数据表不含有英文无法测试大小写
        # with allure_step('1、The query uses : like ab'):
        #     api.query_by_detail(database="flow_log",
        #                         table="l4_flow_log",
        #                         tag="tap_side",
        #                         like="'客户端网卡'")
        #     api.response_status_assert_success()
        #     api.response_values_sort_by_ascending()
        #     api.is_specified_column_contain_specified_value("display_name", "客户端网卡")
