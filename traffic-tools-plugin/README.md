# 打流工具介绍
工具用于生成触发wasm和c插件的流量

[插件地址](https://github.com/deepflowio/deepflow-wasm-go-sdk)

## 1. DNS 打流工具

**协议：** UDP (L4) 和 DNS (L7)

通过 UDP 协议和 DNS 协议的流量触发 DNS 插件。该工具可以模拟 DNS 流量，用于测试和评估 DNS 插件的性能和响应。

**使用方法：**

```
  -c int
        Number of concurrent connections (default 1)
  -r int
        Number of requests per connection (default 10)
```

## 2. HTTP 打流工具

**协议：** HTTP (L7)

通过 8080 端口和 URL 为 "/user_info" 的流量触发 HTTP 插件。该工具可以模拟 HTTP 流量，特定的请求和响应头部字段用于触发 HTTP 插件的计算。

**请求 (Req)：**
- Header 添加 "Custom-Trace-Info" 用于 HTTP 插件计算

**响应 (Resp)：**
- Data 添加 "code" 和 "data" 字段用于 HTTP 插件计算

**使用方法：**

```
  -r int
        request per second (default 100)
```

## 3. HTTP Status Rewrite 打流工具

**协议：** HTTP (L7)

HTTP 响应，设置Data 的"OPT_STATUS"字段的值为 "SUCCESS"，同时填充其他数据，以触发 TCP 分片（TCP Fragment）。

**响应 (Resp)：**
- Data 添加 "OPT_STATUS": "SUCCESS"，其他填充数据用于触发 TCP 分片

**使用方法：**

```
  -r int
        request per second (default 100)
```

## 4. GO_HTTP2_Uprobe 打流工具

**协议：** gRPC

通过 gRPC 调用触发，指定 "Msg" 和 "Trace" 字段。该工具用于测试和评估http2_uprobe插件性能。

**使用方法：**

```
  -r int
        request per second (default 100)
```

## 5. KRPC 打流工具

**使用方法：**

```
  -h string
        krpc pod clusterIP
  -r int
        request per second (default 100)
```



