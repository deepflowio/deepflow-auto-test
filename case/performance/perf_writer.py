import os

from influxdb import InfluxDBClient

from common import common_config
from common import logger

TAG_LIST = ["case_id", "case_name", "vtap_mgt_ip", "commit_id"]
FIELD_LIST = [
    "cpu_usage", "mem_usage", "dispatcher_bps", "dispatcher_pps", "concurrent",
    "drop_pack"
]
MEASUREMENT = "agent_performance"
MD_FILENAME = "test_logs/agent_performace.md"
log = logger.getLogger()


class Writer(object):

    def __init__(self, meta=None):
        self.tags_dict = {}
        self.field_dict = {}
        influxdb_password = os.environ.get('INFLUXDB_PASSWORD')
        self.client = InfluxDBClient(
            'influxdb-v1.yunshan.net', 8086, 'root', influxdb_password,
            'yunshan_autotest'
        )
        self.demo_client = InfluxDBClient(
            common_config.ce_demo_influxdb_url,
            common_config.ce_demo_influxdb_port,
            common_config.ce_demo_influxdb_user,
            common_config.ce_demo_influxdb_passwd, 'yunshan_autotest'
        )
        self.meta = meta
        self.tag_meta = {}
        self.field_meta = {}
        if self.meta:
            for k, v in self.meta.items():
                if v["type"] == "tag":
                    self.tag_meta[k] = v["value"]
                elif v["type"] == "field":
                    self.field_meta[k] = v["value"]

    def write_to(self, data):
        points = []
        for point in data:
            tags = {key: point[key] for key in TAG_LIST}
            fields = {key: point.get(key, float(0)) for key in FIELD_LIST}
            tags.update(self.tag_meta)
            fields.update(self.field_meta)
            body = {
                "measurement": MEASUREMENT,
                "tags": tags,
                "fields": fields,
                "time": point["time"] * 1000000000  # s->ns
            }
            points.append(body)
        self.client.write_points(points)
        self.demo_client.write_points(points)

    def to_markdown(self, data):
        keys = TAG_LIST + FIELD_LIST
        title = " | ".join(keys)
        title = f"| {title} |\n{'| --- '*len(keys)}|\n"
        value_list = [data.get(k, "") for k in keys]
        values = " | ".join(value_list)
        values = f"| {values} |\n"
        return title, values

    def save_markdown(self, data):
        title, value = self.to_markdown(data)
        log.info(title)
        log.info(value)
        # TODO
        return
        if not os.path.exists(MD_FILENAME):
            with open(MD_FILENAME, "a+") as f:
                content = f.read()
                if content == "":
                    # write to title
                    f.write(title)
                    f.write(value)
                else:
                    # write to data
                    f.write(value)
        else:
            # write to data
            with open(MD_FILENAME, "a") as f:
                f.write(value)
