# coding=utf-8
import time
import re
import requests
from urllib.parse import urlencode
from common import common_config
from common import url
from common.utils import ASSERT
from common import logger

log = logger.getLogger()


class QueryApi(object):

    def __init__(self, ip, port):
        self.server_ip = ip
        self.server_port = port
        self.response = None
        self.response_json = None
        self.sql = None

    def clear(self):
        self.response = None
        self.response_json = None
        self.sql = None

    def query_sql_api(self, database="", sql_cmd="", data_precision=""):
        '''parameters:
       sql_cmd: sql command
        '''
        self.clear()
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if database == "":
            data = {'sql': sql_cmd}
        else:
            data = {'db': database, 'sql': sql_cmd}
        if data_precision:
            data["data_precision"] = data_precision
        data = urlencode(data, encoding='utf-8')
        url = 'http://%s:%s/v1/query/' % (self.server_ip, self.server_port)
        loop_num = 20
        while loop_num:
            try:
                self.response = requests.post(url=url,
                                              headers=headers,
                                              data=data)
                break
            except Exception as e:
                log.error(f"query url:{url} data:{data} error: {e}")
                loop_num -= 1
                time.sleep(10)
        if self.response is not None:
            self.response_json = self.response.json()
        self.sql = sql_cmd

    def query_sql_loop_values(self,
                              database,
                              sql_cmd,
                              data_precision="",
                              retries=1):
        success = False
        while retries:
            #self.clear()
            self.query_sql_api(database, sql_cmd, data_precision)
            if self.response.status_code != 200:
                retries -= 1
                if retries:
                    time.sleep(10)
                continue
            if self.response_json["result"]["values"] is None:
                retries -= 1
                if retries:
                    time.sleep(10)
                continue
            success = True
            break
        if not success:
            log.error(f"sql:{self.sql} values:{self.response_json} wait 10s")
        return success

    def query_by_detail(self,
                        database="",
                        table="",
                        tag="",
                        limit=None,
                        offset=None,
                        like=None):
        sql_template = "show tag {} values from {} "
        sql = sql_template.format(tag, table)
        if like is not None:
            sql = sql + "where Enum({}) like {} ".format(tag, like)
        if limit is not None and offset is not None:
            sql = sql + "limit {} ".format(limit)
            sql = sql + "offset {} ".format(offset)

        self.sql = sql
        self.query_sql_api(database, sql)

    def response_code_assert_equal(self, expected_code):
        assert self.response.status_code == expected_code

    def response_code_assert_not_equal(self, expected_code):
        assert self.response.status_code != expected_code

    def response_description_equal_to(self, expected_description=""):
        response_description = self.response_json["DESCRIPTION"]
        assert expected_description in response_description
        #assert response_description == expected_description

    def response_description_contains(self, expected_description=""):
        response_description = self.response_json["DESCRIPTION"]
        assert expected_description in response_description

    def response_status_assert_success(self):
        if self.response_json["OPT_STATUS"].upper() != "SUCCESS":
            log.error(f"sql: {self.sql}, response: {self.response_json}")
        assert self.response_json["OPT_STATUS"].upper() == "SUCCESS"

    def response_status_assert_fail(self):
        assert self.response_json["OPT_STATUS"].upper() == "FAIL"

    def response_values_length_equal(self, expected_length):
        if self.response_json["result"]["values"] is None:
            log.error(f"sql: {self.sql}, response: {self.response_json}")
            assert False
        assert len(self.response_json["result"]["values"]) == expected_length

    def response_values_sort_by_ascending(self):
        '''
        Checks whether the values column in the returned data is positively sorted.
        '''
        values = self.response_json["result"]["values"]
        values_length_list = []
        for value in values:
            display_name_of_value = value[1]
            values_length_list.append(len(display_name_of_value))

        if len(values_length_list) <= 2:
            assert True
        else:
            for i in range(1, len(values_length_list)):
                if values_length_list[i] < values_length_list[i - 1]:
                    assert False
            assert True

    def is_specified_column_contain_specified_value(self, specified_column,
                                                    specified_value):
        #value supports  strings or lists.
        columns = self.response_json["result"]["columns"]
        index = columns.index(specified_column)

        values = self.response_json["result"]["values"]
        target_values = [value[index] for value in values]

        if specified_value is None or specified_value == "":
            assert False
        elif isinstance(specified_value, str):
            if specified_value not in target_values:
                assert False
        elif isinstance(specified_value, list):
            for t_value in specified_value:
                if t_value not in target_values:
                    assert False
        else:

            print("Warnings: Only support string and list")

    def is_specified_column_not_contain_specified_value(
            self, specified_column, specified_value):
        #value supports  strings or lists.
        columns = self.response_json["result"]["columns"]
        index = columns.index(specified_column)

        values = self.response_json["result"]["values"]
        target_values = [value[index] for value in values]

        if specified_value is None or specified_value == "":
            assert False
        elif isinstance(specified_value, str):
            if specified_value in target_values:
                assert False
        elif isinstance(specified_value, list):
            for t_value in specified_value:
                if t_value in target_values:
                    assert False
        else:
            log.info("Warnings: Only surport string and list")
        pass

    def response_values_include_specified_values(self, specified_values_list):
        response_values = self.response_json["result"]["values"]
        for t_value_list in specified_values_list:
            if t_value_list not in response_values:
                log.info(f"specified_values_list ==> {specified_values_list}")
                log.info(f"response_values ==> {response_values}")
                assert False

    def response_values_equal_specified_values(self, specified_values_list):
        response_values = self.response_json["result"]["values"]
        ASSERT.assert_real_equal_except(response_values, specified_values_list)

    def response_values_is_None(self):
        response_values = self.response_json["result"]["values"]
        assert response_values is None

    def response_values_is_not_None(self):
        response_values = self.response_json["result"]["values"]
        assert response_values is not None

    def response_result_is_None(self):
        response_values = self.response_json["result"]
        assert response_values is None

    def echo_debug_info(self):
        log.info(f"\nself.response_json\n{self.response_json}\n")
        log.info(f"\nself.sql\n{self.sql}\n")

    def get_table_all_info(self):

        pass
