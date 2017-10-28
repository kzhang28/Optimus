echo "shutdown the cluster..."
./shutdown.sh

echo "stop docker and clear existing iptables rules..."
ansible all -m shell -a "sudo service docker stop"

ansible all -m shell -a "sudo iptables -t filter -F"
ansible all -m shell -a "sudo iptables -t nat -F"
ansible all -m shell -a "sudo iptables -t mangle -F"
ansible all -m shell -a "sudo iptables -t raw -F"

ansible all -m shell -a "sudo service docker start"

echo "starting kubernetes..."
KUBERNETES_PROVIDER=ubuntu ./kube-up.sh

echo "labeling nodes..."
./label_nodes.sh

echo "starting dashboard and dns..."
cd ubuntu && ./deployAddons.sh

echo "starting heapster..."
kubectl create -f ../addons/cluster-monitoring/influxdb/heapster-service.yaml
kubectl create -f ../addons/cluster-monitoring/influxdb/heapster-controller.yaml

echo "starting pingmesh..."
cd ~/k8s-mxnet/pingmesh && kubectl create -f pinger.yaml