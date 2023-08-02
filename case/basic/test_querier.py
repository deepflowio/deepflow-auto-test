import time
import pytest
import allure
from common.querier_api_utils import QueryApi
from case.base import BaseCase
from common.utils import step as allure_step
from common import logger

log = logger.getLogger()


class TestQuerier(BaseCase):

    @allure.suite('basic test')
    @allure.epic('basic test - data query function of querier component')
    @allure.feature('')
    @allure.title('DeepFlow基础测试-querier数据查询')
    @allure.description
    @pytest.mark.high
    @pytest.mark.basic
    def test_querier_sql_data(self):
        with allure_step('step 1: check db data'):
            api = QueryApi(
                self.df_ce_info["mgt_ip"], self.df_ce_info["server_query_port"]
            )
            count = 0
            first_data_checked = False
            while not first_data_checked and count < 60:
                api.query_sql_api(
                    database="flow_metrics", sql_cmd=
                    "select pod_node from vtap_flow_port order by time limit 1",
                    data_precision="1s"
                )
                api.echo_debug_info()
                api.response_status_assert_success()
                if api.response_json["result"]["values"]:
                    first_data_checked = True
                else:
                    time.sleep(10)
                    count += 1
            if not first_data_checked:
                log.error("querier check first data error!")
                assert False
