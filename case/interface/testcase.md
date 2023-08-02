## API测试用例列表

### Queirer sql查询

#### select sql查询
- select all tags
  - 测试步骤
    - 1.show tags查询所有tag
    - 2.flow_metrics和flow_log的表select所有tag
  - 期望结果
    - 1.查询成功

- group all tags
  - 测试步骤
    - 1.show tags查询所有tag
    - 2.flow_metrics和flow_log的表group所有tag
  - 期望结果
    - 1.查询成功

- enum all tags
  - 测试步骤
    - 1.show tags查询所有tag
    - 2.flow_metrics和flow_log的表使用enum函数查询所有支持的tag
  - 期望结果
    - 1.查询成功

- exist all tags
  - 测试步骤
    - 1.show tags查询所有tag
    - 2.flow_metrics和flow_log的表使用exist函数过滤所有支持的tag
  - 期望结果
    - 1.查询成功

- select all metrics
  - 测试步骤
    - 1.show metrics查询所有metrics
    - 2.flow_metrics和flow_log的表select所有metrics
  - 期望结果
    - 1.查询成功

#### show sql查询
- show databases
  - 测试步骤
    - 1.执行sql:`show databases`
  - 期望结果
    - 1.查询成功

- show tables
  - 测试步骤
    - 1.执行sql:`show tables` db:`flow_metrics`
  - 期望结果
    - 1.查询成功

- show metrics
  - 测试步骤
    - 1.执行sql:`show metrics from vtap_flow_port` db:`flow_metrics`
  - 期望结果
    - 1.查询成功

- show tags
  - 测试步骤
    - 1.执行sql:`show tags` db:`flow_metrics`
  - 期望结果
    - 1.查询成功

- show tag values