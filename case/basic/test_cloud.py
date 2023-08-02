import time
import pytest
import allure
from case.base import BaseCase
from common.utils import step as allure_step
from common import logger

log = logger.getLogger()


class TestCloud(BaseCase):

    @allure.suite('basic test')
    @allure.epic('basic test - cloud platform docking')
    @allure.feature('')
    @allure.title('DeepFlow基础测试-对接自身云平台')
    @allure.description
    @pytest.mark.high
    @pytest.mark.basic
    def test_domain_sync(self):
        '''Check DF successfully docking with its own cloud platform by API 
        '''
        res = False
        deepflow_hostname_values = self.common_utils.get_deepflow_hostname()
        try:
            for k in range(20):
                domain_lists = self.common_utils.get_domains_list()
                for i in domain_lists:
                    if 'k8s' in i['NAME'] and i[
                        'CONTROLLER_IP'] == self.df_ce_info["mgt_ip"] and i[
                            'CONTROLLER_NAME'
                        ] == deepflow_hostname_values.lower(
                        ) and i['STATE'] == 1 and i['ENABLED'] == 1 and len(
                            i['SYNCED_AT']
                        ) > 0:
                        log.info(
                            'DeepFlow domain sync success，name:{}'.format(
                                i['NAME']
                            )
                        )
                        res = True
                        break
                    else:
                        time.sleep(30)
                        log.info('wait domain sync，wait 30s')
                if res == True:
                    break
        except Exception as err:
            log.error('DeepFlow domain sync error: {}'.format(err))
            assert False

    @allure.suite('basic test')
    @allure.epic('basic test - cloud platform docking')
    @allure.feature('')
    @allure.title('DeepFlow基础测试-对接自身采集器')
    @allure.description
    @pytest.mark.high
    @pytest.mark.basic
    def test_agent_sync(self):
        '''Check the DF's vtaps list contains information about DF's own vtaps by the API.
        Test that the agent is synchronized to DF.
        '''
        res = False
        deepflow_hostname_values = self.common_utils.get_deepflow_hostname()
        try:
            for k in range(20):
                vtap_lists = self.common_utils.get_vtaps_list()
                for i in vtap_lists:
                    if deepflow_hostname_values.lower() in i['NAME'] and i['SYNCED_CONTROLLER_AT'] is not None and i['SYNCED_ANALYZER_AT'] is not None\
                            and i['STATE'] == 1 and i['ENABLE'] == 1 and i['LAUNCH_SERVER'] == self.df_ce_info["mgt_ip"]:
                        log.info(
                            'DeepFlow agent sync success, name:{}'.format(
                                i['NAME']
                            )
                        )
                        res = True
                        break
                    else:
                        time.sleep(30)
                        log.info('wait agent sync, wait 30s')
                if res == True:
                    break
        except Exception as err:
            log.error('DeepFlow agent sync error: {}'.format(err))
            assert False
