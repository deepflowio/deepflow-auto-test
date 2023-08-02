import pytest
from common.utils import step as allure_step
import allure
import time

k8s_vm_name = 'automation-performance-k8s-http'
loop_num = 15


@pytest.fixture(scope="session", autouse=True)
def folder_fixture():
    print("sleep 60")
    time.sleep(60)
    yield
