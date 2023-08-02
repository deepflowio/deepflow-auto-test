## 基础功能测试用例列表

### 对接功能

#### 云平台对接
- 对接阿里云
  - 测试步骤
    - 1.对接阿里云
    - 2.获取domain list
  - 期望结果
    - 1.domain对接成功

#### 采集器对接
- 对接本地deepflow-agent
  - 测试步骤
    - 1.部署deepflow-agent
    - 2.获取vtap list
  - 期望结果
    - 1.vtap对接成功

### querier数据查询
- 数据查询
  - 测试步骤
    - 1.直接查询querier,sql：`select pod_node from vtap_flow_port order by time limit 1`
  - 期望结果
    - 1.数据查询成功，有数据返回

