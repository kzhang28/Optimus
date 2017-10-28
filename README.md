# Optimus

Optimus is a customized cluster scheduler for deep learning training jobs that targets high job performance and resource efficiency in production clusters. It builds resource-performance models for each job on the go, and dynamically schedules resources to jobs based on job progress and the cluster load to maximize training performance and resource efficiency.

## Prerequisites
### OS Environment
(1) Ubuntu 14.04.5 Server 64bit LTS;
(2) Install the basic tools by running the script <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/notes/preinstall.sh">preinstall.sh</a>.

### Cluster Environment
Build up the following platforms in the cluster:
(1) HDFS 2.8, see <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/notes/hadoop.md">hadoop.md</a> for more details;
(3) Docker 17.06.0-ce, see the official installation tutorial;
(4) Kubernetes 1.7, see notes/k8s.md for detailed installation steps (the official one is outdated).
### Container Environment




Python 2.7.6.




## Basic Usage
The system configuration file <a href="https://github.com/yhpeng-git/deTector/blob/master/controller/config.xml">config.xml</a> in the Controller specifies all details such as Controller/Diagnoser IP, listening port and ping interval. To run deTector on a cluster, you need to update this file according to your cluster configuration.

You need to start Controller first using the following command:

```
$ python controller.py
```

The Controller will read the configuration, compute the probe matrix and start a HTTP server.

To start the Diagnoser, run:
```
$ python diagnoser.py controller_ip controller_port
```
The Diagnoser needs to connect to the controller to get the probe matrix.

Next, start Responders on all servers using the command:
```
$ python responder.py controller_ip controller_port
```

Finally, run Pingers on servers who ping others:
```
$ python pinger.py host_ip controller_ip controller_port
```

## Advanced usage
For ease of deployment, you can direct run <a href="https://github.com/yhpeng-git/deTector/blob/master/controller/script.py">script.py</a> to deploy deTector in a cluster after you finish basic configuration and configure auto-login ssh. This script reads the configuration from config.xml and by default, it runs Controller and Diagnoser on localhost. 

To do loss localization, you also need to start failanalyzer on the same machine with Diagnoser using the command:
```
$ python failanalyzer.py
```

Note that deTector requires source routing in the cluster to controll packet path. Packet encapsulation and decapsulation (e.g., IP-in-IP) is a general solution and should be supported on commodity switches. 


## More
Please read <a href="https://github.com/yhpeng-git/deTector/blob/master/documentation/Architecture.md">Architecture.md</a> and <a href="https://github.com/yhpeng-git/deTector/blob/master/documentation/Workflow.md">Workflow.md</a> for more system design details.

Read the <a href="https://github.com/yhpeng-git/deTector/blob/master/documentation/technical_report.pdf"> technical report </a> for the core algorithm of deTector.
