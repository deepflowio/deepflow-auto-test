## 性能分析用例列表

### Agent采集性能分析

#### 采集器对宿主机业务的影响
- 容器采集器，nginx场景
  - 测试步骤：
    - 1、采集器硬件规格: 8C16G / 采集器默认资源限制(1C768M)
    - 2、通过公有云提供的sdk方式创建centos7系统且内核为4.19版本
    - 3、使用wrk2工具进行针对nginx的压力测试，url为127.0.0.1:80/index.html，rps分别为 30000 28000 26000 24000 22000 20000 18000 16000 14000 12000, wrk2 -c1 -t1 -R$rate -d60 -L http://127.0.0.1:80/index.html
    - 4、从telegraf分别查询4次压力测试的数据，指标量包括 时延p50, 时延p90, nginx_cpu_p90, nginx_mem_p90, wrk_cpu_p90, wrk_mem_p90
    - 5、安装k8s以及deepflow-agent
    - 6、重复步骤3的压力测试
    - 7、重复步骤4的数据查询，并额外查询指标量 agent_cpu_p90, agent_mem_p90
  - 期望结果：
    - 1、获得步骤4以及步骤7的查询结果，可以直观的看出deepflow-agent对于简单业务环境nginx的影响

- 容器采集器，istio场景
  - 测试步骤：
    - 1、采集器硬件规格: 8C16G / 采集器默认资源限制(1C768M)
    - 2、通过公有云提供的sdk方式创建centos7系统且内核为4.19版本
    - 3、安装k8s以及istio组件，其中，productage副本数为4，details副本数为2
    - 4、使用wrk2工具进行针对nginx的压力测试，url为productpage_ip:9080//productpage，rps分别为 380 370 360 350 340 330 320 310 300 290，例：wrk2 -c50 -t4 -R$rate -d60 -L http://$productpage_ip:9080/productpage
    - 5、从telegraf分别查询4次压力测试的数据，指标量包括 时延p50, 时延p90, nginx_cpu_p90, nginx_mem_p90, wrk_cpu_p90, wrk_mem_p90
    - 6、安装deepflow-agent
    - 7、重复步骤4的压力测试
    - 8、重复步骤5的数据查询，并额外查询指标量 agent_cpu_p90, agent_mem_p90
  - 期望结果：
    - 1、获得步骤5以及步骤8的查询结果，可以直观的看出deepflow-agent对于复杂业务环境istio的影响



