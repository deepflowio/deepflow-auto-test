## krpc demo

build and push image:
```bash
docker build -f dockerfile-server --tag registry.cn-beijing.aliyuncs.com/deepflow-demo/krpc-server:latest .

docker build -f dockerfile-gateway --tag registry.cn-beijing.aliyuncs.com/deepflow-demo/krpc-gateway:latest .

docker push registry.cn-beijing.aliyuncs.com/deepflow-demo/krpc-gateway

docker push registry.cn-beijing.aliyuncs.com/deepflow-demo/krpc-server:latest
```

create k8s resource
```
kubectl create -f kubernetes.yaml
```
