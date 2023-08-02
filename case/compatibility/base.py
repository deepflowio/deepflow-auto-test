import allure
import time
import logging
from common.env import apply_env, release_env
from case.base import BaseCase
from common import common_config
from common.utils import step as allure_step


class CompatibilityBaseCase(BaseCase):

    vm_id_info = None
    vm_private_ip = None
