## 兼容性测试用例列表

### Agent兼容性

#### DeepFlow-agent
- Centos7系统兼容性
  - 测试步骤
    - 1、通过公有云提供的sdk方式创建centos7系统内核>=4.14(支持ebpf)的虚拟机
    - 2、获取并部署最新版本的deepflow-agent版本
    - 3、通过API方式获取DeepFlow采集器列表
    - 4、查看采集器的deepflow-agent.log文件
    - 5、反复杀掉deepflow-agent进程
    - 6、采集器发送流量(例如:ICMP流量)
  - 期望结果
    - 1、步骤2期望结果，deepflow-agent运行正常
    - 2、步骤3期望结果，在DF的采集器列表中可以发现在Centos7采集器(主机名或者运行的IP地址)
    - 3、步骤4期望结果，采集器的deepflow-agent.log日志中无ERROR且无WARN信息
    - 4、步骤5期望结果，deepflow-agent进程自动拉起且运行正常
    - 5、步骤6期望结果，过deepflow-ctl命令中可以查看到相关流量信息

- Ubuntu14系统兼容性
  - 测试步骤
    - 1、通过公有云提供的sdk方式创建ubuntu14系统内核>=4.14版本的虚拟机
    - 2、TODO
  - 期望结果
    - 1、TODO

- Ubuntu16系统兼容性
  - 测试步骤
    - 1、通过公有云提供的sdk方式创建ubuntu16系统内核>=4.14版本的虚拟机
    - 2、TODO
  - 期望结果
    - 1、TODO

- Ubuntu18系统兼容性

- Ubuntu20系统兼容性

- ARM场景兼容性

