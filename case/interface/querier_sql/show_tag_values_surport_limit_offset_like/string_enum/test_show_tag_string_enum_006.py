# coding: utf-8
import pytest
from common.utils import step as allure_step
import allure
from common.querier_api_utils import QueryApi
from common_variable import values
from case.interface.querier_sql.base import QuerierSqlBaseCase


class TestShowTagStringEnum006(QuerierSqlBaseCase):

    @allure.suite('API test')
    @allure.epic('show tag values')
    @allure.feature('string enum')
    @allure.title('string_enum like正常查询- *')
    @allure.description('')
    @pytest.mark.medium
    def test_show_tag_string_enum_006(self):
        case_id = "show_tag_string_enum_006"
        case_name = "string_enum类型like查询根据星号位置"
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
        # 10、The query uses : like *a*b*"
        # Expected results:
        # 1-10、return specific data when a query field matches database data
        api = QueryApi(
            self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
        )

        # show tag tap_side values from l4_flow_log like hello;

        # with allure_step('BUG： 使用like时候不带where'):
        #     api.query_sql_api(database="flow_log", sql_cmd="show tag tap_side values from l4_flow_log like hello;")
        #     api.echo_debug_info()
        #     api.response_status_assert_success()
        #     # http://bugzilla.yunshan.net/show_bug.cgi?id=19424
        #     # TODO 这里是BUG，需要修改,这里期望like需要依赖于where 去使用
        # http://bugzilla.yunshan.net/buglist.cgi?action=wrap&bug_status=RESOLVED&chfield=%5BBug%20creation%5D&chfieldfrom=2020-05-01&chfieldto=Now&list_id=111338&product=DeepFlow&reporter=jincong%40yunshan.net&resolution=FIXED&resolution=INVALID&resolution=WONTFIX&resolution=DUPLICATE&resolution=WORKSFORME&resolution=FIXEDINRC&resolution=UNREPRODUCED&saved_report_id=83&version=5.7.3&version=5.7.4&version=6.0.0&version=6.0.1&version=6.1.0&version=6.1.1&version=6.1.2&version=6.1.3&version=6.1.4&version=6.1.5&version=6.1.6

        # with allure_step('BUG： 使用offset时候不带limit'):
        #     api.query_sql_api(database="flow_log", sql_cmd="show tag tap_side values from l4_flow_log offset 5")
        #     api.echo_debug_info()
        #     api.response_status_assert_success()
        #     # TODO 已经确定是BUG,offset需要依赖于limit生效

        # 1、The query uses : like ab
        with allure_step('1、The query uses : like ab'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'Client NIC'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])

        # 2、The query uses : like *ab
        with allure_step('2、The query uses : like *ab'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'Client NIC'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])

        # 3、The query uses : like a*b
        with allure_step('3、The query uses : like a*b'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'Clien* NIC'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])

        # 4、The query uses : like ab*
        with allure_step('4、The query uses : like ab*'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'Client NI*'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])

        # 5、The query uses : like **ab
        with allure_step('5、The query uses : like **ab'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'**ient NIC'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])

        # 6、The query uses : like a**b
        with allure_step('6、The query uses : like a**b'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'Clien**NIC'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])

        # 7、The query uses : like ab**
        with allure_step('7、The query uses : like ab**'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'Client N**'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])

        # 8、The query uses : like *a*b
        with allure_step('8、The query uses : like *a*b'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'*l*ent NIC'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])

        # 9、The query uses : like a*b*
        with allure_step('9、The query uses : like a*b*'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'Client*NI*'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])

        # 10、The query uses : like *a*b*
        with allure_step('10、The query uses : like *a*b*'):
            api.query_by_detail(
                database="flow_log", table="l4_flow_log", tag="tap_side",
                like="'*lient*NI*'"
            )
            api.response_status_assert_success()
            api.response_values_sort_by_ascending()
            api.response_values_equal_specified_values([[
                'c', 'Client NIC', ''
            ]])
