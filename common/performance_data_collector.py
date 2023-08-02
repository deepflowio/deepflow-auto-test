from influxdb import InfluxDBClient
from common import common_config
import os


class PerfDataCollect(object):

    def __init__(self, template=""):
        self.tags_dict = {}
        self.field_dict = {}
        influxdb_password = os.environ.get('INFLUXDB_PASSWORD')
        self.client = InfluxDBClient(
            'influxdb-v1.yunshan.net', 8086, 'root', influxdb_password,
            'yunshan_autotest'
        )
        self.get_tags_of_template(template)
        self.demo_client = InfluxDBClient(
            common_config.ce_demo_influxdb_url,
            common_config.ce_demo_influxdb_port,
            common_config.ce_demo_influxdb_user,
            common_config.ce_demo_influxdb_passwd, 'yunshan_autotest'
        )

    def get_tags_of_template(self, template):
        template_line = template.split("\n")
        for line in template_line:
            line = line.strip().replace("：", ":")  #考虑到有可能该模板存在中英文冒号混用的情况
            if ':' in line and line.startswith("-"):
                line = line.strip("-").strip()  #去掉前面的减号和空格
                key = line.split(":", 1)[0]
                value = line.split(":", 1)[1].strip()
                if value != "" and "{}" not in value:  #value为空时候，为提示信息，value中带{}为field，IP除外
                    self.tags_dict.update({key: value})

    def update_proper_tags_to_tags(self, **kwargs):
        """
        更新专有信息到tags中，包含ip，case_id，case_name
        """
        for key, value in kwargs.items():  #更新IP到tags中
            if key == "vtaps_mgt_ip":
                self.tags_dict.update({"vtaps_mgt_ip": value.strip()})
            elif key == "case_id":
                self.tags_dict.update({"case_id": value.strip()})
            elif key == "case_name":
                self.tags_dict.update({"case_name": value.strip()})
            else:
                pass
                #print("目前补充的专有信息只有IP，case_id， case_name。其他信息不补充")

    def update_data_and_storage(self, *args, **kwargs):
        self.update_proper_tags_to_tags(**kwargs)

        need_write_field_list = [
            "cpu_usage", "mem_usage", "dispatcher_bps", "dispatcher_pps",
            "drop_pack"
        ]
        for key, value in kwargs.items():  #分别对某一类的信息，比如CPU类，内存类，丢包类，进行数据写入
            if key in need_write_field_list:
                data_point = self.prepare_json_body_with_tags_field({
                    key: int(value)
                })
                self.write_to_influxdb(data_point)  #写入数据库

    def prepare_json_body_with_tags_field(self, field_dict):
        #根据field判断应该写入哪一张表,目前为精确判断，以后可能扩展为字段包含等复杂的判断方法
        data_point_dict = {}
        for key, value in field_dict.items():
            if "cpu_usage" in key:
                data_point_dict.update({"measurement": "cpu"})
            elif "mem_usage" in key:
                data_point_dict.update({"measurement": "mem"})
            elif "dispatcher_bps" in key:
                data_point_dict.update({"measurement": "dispatcher_bytes"})
            elif "dispatcher_pps" in key:
                data_point_dict.update({"measurement": "dispatcher_packets"})
            elif "drop_pack" in key:
                data_point_dict.update({
                    "measurement": "dispatcher_kernel_drops"
                })

        point_tags_dict = {"tags": self.tags_dict}
        point_fields_dict = {"fields": field_dict}
        data_point_dict.update(point_tags_dict)
        data_point_dict.update(point_fields_dict)
        data_point_res = []
        data_point_res.append(data_point_dict)
        return data_point_res

    def write_to_influxdb(self, json_body):
        self.client.write_points(json_body)  # 写入数据，同时创建表
        self.demo_client.write_points(json_body)
