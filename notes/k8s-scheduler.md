Generic Scheduler

FitPredicate (see master/pkg/scheduler/predicates.go) and PriorityFunction (see master/pkg/scheduler/priorities.go). 

one example:
candidates = []
for pod in pods:
	for node in nodes:
		if pod.label-selector == node.label or pod.resources.limits + node.allocated_resources < node.resources.capacity:	// fit predicate
		candidates.append(node)
	for candidate in candidates:
		select one according to priorities (e.g., least used resources)	// priority function

general steps:
(1) filter the nodes,
(2) prioritize the filtered list of nodes
(3) select the best fit node

Available Predicates
Static predicates: PodFitsPorts, PodFitsResources, NoDiskConflict, MatchNodeSelector, HostName
Configurable predicates: ServiceAffinity, LabelsPresence

Available Priority Functions
Static priority functions: LeastRequestedPriority, BalancedResourceAllocation, ServiceSpreadingPriority, EqualPriority
Configurable priority functions: ServiceAntiAffinity, LabelPrerference

Provide a JSON file that specifies the predicates and priority functions to override the default scheduler. The path to the file can be specified in the master configuration file.

How to label a node:
kubectl label nodes <node-name> <label-key>=<label-value>

How to add a nodeSelector selector:
add the following in pod spec:
nodeSelector:
    disktype: ssd

How to write a custom scheduler:
http://blog.kubernetes.io/2017/03/advanced-scheduling-in-kubernetes.html
