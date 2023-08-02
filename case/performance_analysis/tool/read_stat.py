import time
import sys
from influxdb import InfluxDBClient

influxdb_password = ""
client = InfluxDBClient(
    '127.0.0.1', 8086, 'root', influxdb_password, 'telegraf'
)
nginx_client = InfluxDBClient(
    'nginx_ip', 8086, 'root', influxdb_password, 'telegraf'
)
PROCESS_WRK = "wrk2"
PROCESS_NGINX = "nginx"
PROCESS_PRODUCTPAGE = "productpage"
PROCESS_DEEPFLOW_AGENT = "deepflow_agent"
filter_map = {
    PROCESS_PRODUCTPAGE: "pattern = 'productpage' AND process_name = 'python'",
}


def get_result(sql):
    result = client.query(sql)
    return list(result.get_points())


def get_nginx_result(sql):
    result = nginx_client.query(sql)
    return list(result.get_points())


def get_sql(process):
    now = int(time.time())
    start = (now - 60) * 1000000000
    end = now * 1000000000  # s->ns
    if process in filter_map:
        filter = filter_map[process]
    else:
        filter = f"pattern = '{process}'"
    sql = f"SELECT percentile(sum_cpu_usage, 90) AS max_cpu_usage, percentile(sum_memory_usage, 90) AS max_mem_usage FROM (SELECT sum(cpu_usage) as sum_cpu_usage, sum(memory_usage) as sum_memory_usage FROM procstat WHERE {filter} AND time >= {start} AND time <= {end} GROUP BY time(10s))"
    return sql


if __name__ == "__main__":
    process = sys.argv[1]
    if process == "nginx":
        if len(sys.argv) > 2:
            process = sys.argv[2]
        sql = get_sql(process)
        result = get_nginx_result(sql)
    else:
        sql = get_sql(process)
        result = get_result(sql)
    if result:
        print(result[0]["max_cpu_usage"])
        print(result[0]["max_mem_usage"])
    else:
        print(0)
        print(0)
