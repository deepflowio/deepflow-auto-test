import time
import os
from common.env import apply_env, release_env
from common.const import CASE_TYPE_CONCURRENCY
from common.utils import CommonUtils
from common.utils import step as allure_step
from common import logger

log = logger.getLogger()


class BaseCase(object):

    CASE_TYPE = CASE_TYPE_CONCURRENCY
    df_ce_info = {}
    common_utils = None

    @classmethod
    @apply_env
    def setup_class(cls):
        deepflow_server_image_tag = os.environ.get('DEEPFLOW_SERVER_IMAGE_TAG')
        deepflow_agent_image_tag = os.environ.get('DEEPFLOW_AGENT_IMAGE_TAG')
        # init utils
        cls.common_utils = CommonUtils(
            cls.df_ce_info["mgt_ip"], cls.df_ce_info["server_controller_port"],
            cls.df_ce_info["server_query_port"], deepflow_server_image_tag,
            deepflow_agent_image_tag
        )
        cls.start = time.time()
        with allure_step('The setup of the class'):
            pass
        cls._setup_class()

    @classmethod
    @release_env
    def teardown_class(cls):
        cls._teardown_class()
        log.info(
            f"case {cls.class_name()} spend time {time.time()-cls.start}s"
        )
        with allure_step('The teardown of the class'):
            pass

    @classmethod
    def class_name(cls):
        return cls.__name__

    @classmethod
    def _setup_class(self):
        pass

    @classmethod
    def _teardown_class(self):
        pass
