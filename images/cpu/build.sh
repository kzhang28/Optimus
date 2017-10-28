# build and push
ansible all -m shell -a "docker rmi -f xxx/k8s-mxnet-cpu-experiment:latest"
docker build -t xxx/k8s-mxnet-cpu-experiment:latest -f k8s-mxnet-cpu-experiment.Dockerfile .
docker push xxx/k8s-mxnet-cpu-experiment:latest