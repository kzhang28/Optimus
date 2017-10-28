# build and push
ansible all -m shell -a "docker rmi -f xxx/k8s-bandwidth:latest"
docker build -t xxx/k8s-bandwidth:latest -f bandwidth.Dockerfile .
docker push xxx/k8s-bandwidth:latest
