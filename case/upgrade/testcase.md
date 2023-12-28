## deepflow升级测试例

### deepflow-ce升级

#### server&agent升级
- 最新发布版升级至指定版本(默认latest)
  - 测试步骤：
    - 1、通过公有云提供的sdk方式创建centos7系统且内核为4.19版本
    - 2、部署k8s以及最新发布版deepflow，例v6.2.6
    - 3、检查基础功能是否正常，包括数据查询、采集器对接、云平台对接
    - 4、升级server和agent版本至指定版本，默认latest
    - 5、检查升级后基础功能是否正常，包括数据查询、采集器对接、云平台对接
  - 期望结果：
    - 1、升级成功，所有pod正常运行
    - 2、基础功能正常




