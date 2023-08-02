## 性能测试用例列表

### Agent采集性能

#### Workload-V-Linux
- Workload-V-Linux采集器类型，TCP大包场景
  - 测试步骤：
    - 1、Workload-V-Linux采集器硬件规格: 2C4G / 采集器默认资源限制(1C768M)
    - 2、Workload-V-Linux采集器，通过公有云提供的sdk方式创建centos7系统且内核为4.19版本
    - 3、Workload-V-Linux采集器，部署最新版本的deepflow-agent
    - 4、Workload-V-Linux采集器，发送BPS流量>=10Gbps(后续考虑通过docker-compose方式来实现)。命令行参考; iperf3 -c server_ip -b 10G -t 600s -M 1400
  - 期望结果：
    - 1、步骤4期望结果，通过DeepFlow的querier api接口, 读取deepflow-system表中的数据(包括CPU/内存/采集流量速率/丢包数等)。采集流量速率>=10Gbps、丢包数为0

- Workload-V-Linux采集器类型，UDP小包场景
  - 测试步骤：
    - 1、Workload-V采集器发送PPS流量>=600Kpps。命令行; hping3 -d 18 server_ip -2 -p 10001 -s 10002 -k --flood 
    - 2、TODO
  - 期望结果：
    - 1、采集包速率>=600Kpps、丢包数为0

- Workload-V-Linux采集器类型，HTTP包场景
  - 测试步骤：
    - 1、Workload-V采集器发送HTTP流量。命令行; ab -n 3000000 -c 1000 http://server_ip/index.html
    - 2、TODO
  - 期望结果：
    - 1、采集流量速率约为90MBps、采集包速率为80Kpps、丢包数为0(参考之前的数据)

#### 容器
- 容器采集器类型，TCP大包场景
  - 测试步骤：
    - 1、容器采集器硬件规格: 4C8G。发送BPS流量>=6Gbps
    - 2、TODO
  - 期望结果：
    - 1、采集流量速率>=6Gbps、丢包数为0(参考之前结果)

- 容器采集器类型，UDP小包场景
  - 测试步骤：
    - 1、发送PPS流量>=600Kpps
  - 期望结果：
    - 1、采集包速率>=600Kpps、丢包数为0(参考之前结果)

- 容器采集器类型，HTTP包场景
  - 测试步骤：
    - 1、TODO
  - 期望结果：
    - 1、采集流量速率约为145MBps、采集包速率为125Kpps、丢包数为0(参考之前结果)



