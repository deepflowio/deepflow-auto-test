from influxdb import InfluxDBClient
from common import common_config
import os

TAG_LIST = [
    "with_agent", "process_name", "rate", "end_time", "annotation_rate"
]
FIELD_LIST = [
    "lantency_p50", "lantency_p90", "process_max_cpu", "process_max_mem",
    "req_per_sec", "wrk2_max_cpu", "wrk2_max_mem", "agent_max_cpu",
    "agent_max_mem", "details_max_cpu", "details_max_mem", "reviews_max_cpu",
    "reviews_max_mem", "ratings_max_cpu", "ratings_max_mem", "envoy_max_cpu",
    "envoy_max_mem", "agent_max_cpu", "agent_max_mem", "time_end",
    "postgres_max_cpu", "postgres_max_mem", "mysqld_max_cpu", "mysqld_max_mem"
]
MEASUREMENT = "agent_performance_analysis"


class Writer(object):

    def __init__(self, meta):
        self.tags_dict = {}
        self.field_dict = {}
        influxdb_password = os.environ.get('INFLUXDB_PASSWORD')
        # self.client = InfluxDBClient(
        #     'influxdb-v1.yunshan.net', 8086, 'root', influxdb_password,
        #     'yunshan_autotest'
        # )
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
            measurement = f"{MEASUREMENT}_{point['process_name']}"
            body = {
                "measurement": measurement,
                "tags": tags,
                "fields": fields,
                "time": point["time"] * 1000000000  # s->ns
            }
            points.append(body)
        #self.client.write_points(points)
        self.demo_client.write_points(points)
