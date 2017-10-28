# build and push
ansible all -m shell -a "docker rmi -f xxx/k8s-mxnet-gpu-experiment:latest"
docker build -t xxx/k8s-mxnet-gpu-experiment:latest -f k8s-mxnet-gpu-experiment.Dockerfile .
docker push xxx/k8s-mxnet-gpu-experiment:latest