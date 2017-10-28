kubectl delete --force --grace-period=3 jobs,deployments,replicationcontrollers,replicasets,statefulsets,daemonsets,services,pods,configmaps --all
kubectl delete --force --grace-period=3 jobs,deployments,replicationcontrollers,replicasets,statefulsets,daemonsets,services,pods,configmaps --all --namespace=kube-system
KUBERNETES_PROVIDER=ubuntu ./kube-down.sh
