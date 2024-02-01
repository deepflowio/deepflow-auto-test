# Build

go build

# Run

```
Usage of ./app-traffic:
  -h string
        Target Service "host:port"
  -p int
        DB Root Password
  -r int
        request per second
  -d int
        Execution time in seconds
  -t int
        Number of threads
  -e string
        Engine of DB [redis, mysql]
  -c int
        concurrent connections of each thread, only support mysql
  -complexity int
        complexity of query sql, only add count of select key
```

- Example:
```
[root@iZ2zebdukco9jfpuo0shnaZ ~]# ./app-traffic -e redis -h 127.0.0.1:6379 -p deepflow -r 50000 -t 5 -d 10
2024/01/29 13:57:24 [*] Start redis App Traffic 127.0.0.1:6379, date rate 10000 rps.
2024/01/29 13:57:24 [*] Start redis App Traffic 127.0.0.1:6379, date rate 10000 rps.
2024/01/29 13:57:24 [*] Start redis App Traffic 127.0.0.1:6379, date rate 10000 rps.
2024/01/29 13:57:24 [*] Start redis App Traffic 127.0.0.1:6379, date rate 10000 rps.
2024/01/29 13:57:24 [*] Start redis App Traffic 127.0.0.1:6379, date rate 10000 rps.
now request count is 50020 , err is 0, cost time 1.001950s
now request count is 100021 , err is 0, cost time 2.001982s
now request count is 150068 , err is 0, cost time 3.002013s
now request count is 200076 , err is 0, cost time 4.002049s
now request count is 250076 , err is 0, cost time 5.002072s
now request count is 300076 , err is 0, cost time 6.002102s
now request count is 350040 , err is 0, cost time 7.002169s
now request count is 400082 , err is 0, cost time 8.002204s
now request count is 450070 , err is 0, cost time 9.002954s
now request count is 500071 , err is 0, cost time 10.002993s
total: 500395, count: 500395, error: 0, request/sec: 50024.43 avg: 39.512µs  max: 3.845947ms  p50: 34.687µs  p90: 62.392µs
```