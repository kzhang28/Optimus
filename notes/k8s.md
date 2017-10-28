Steps to bring up Kubernetes on Ubuntu 14.04
(1) configure ubuntu/config-default.sh
(2) modify the version of flannel, etcd and kubernetes in file download-release.sh
(3) comment out "verify-prereqs" and "verify-kube-binaries" in both kube-up.sh and kube-down.sh
(4) modify ubuntu/util.sh, add "KUBE_ROOT=/home/net/kubernetes/" in the begining. add "source ~/kube/config-default.sh" in function provision-master(), function provision-node() and function provision-masterandnode() just before "source ~/kube/util.sh".
(5) modify ubuntu/deployAddons.sh, replace the original two lines in the begining with "KUBE_ROOT=/home/net/kubernetes/" and KUBECTL="kubectl" in the begining, and exchange the order of starting DNS and UI (i.e., starting Dashboard first)
(6) update heapster-controller.yaml and influxdb-grafana-controller.yaml with newer version of images. Besides, delete "--threshold=5" and "--estimator=exponential"in heapster.
(7) change the NIC interface if there is strange connection issue.