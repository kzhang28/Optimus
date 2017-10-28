# Optimus

Optimus is a customized cluster scheduler for deep learning training jobs that targets high job performance and resource efficiency in production clusters. It builds resource-performance models for each job on the go, and dynamically schedules resources to jobs based on job progress and the cluster load to maximize training performance and resource efficiency. It uses MXNet as the distributed training framework and is integrated into Kubernetes cluster manager.

## Setup
### OS Environment
(1) Ubuntu 14.04.5 Server 64bit LTS;

(2) Install the basic tools by running the script <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/notes/preinstall.sh">preinstall.sh</a>.

### Cluster Environment
Build up the following platforms in the cluster:

(1) HDFS 2.8: see <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/notes/hadoop.md">hadoop.md</a> for more details;

(2) Docker 17.06.0-ce: see the official installation tutorial https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/;

(3) Kubernetes 1.7: see <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/notes/hadoop.md">k8s.md</a> for detailed installation steps (the official one is outdated). Generally, you need to install from the <a href="https://github.com/eurosys18-Optimus/Optimus/tree/master/k8s/src">modified source code</a>. Configure the <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/k8s/scripts/config-default.sh">config-default.sh</a> script for cluster node information (e.g., Master IP) and label each node as CPU or GPU node in <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/k8s/scripts/label_nodes.sh"> label_nodes.sh</a>. Run <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/k8s/scripts/start.sh"> start.sh</a> to start the resource manager and <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/k8s/scripts/start.sh"> shutdown.sh</a> to shutdown it.


### Container Environment
(1) MXNet CPU container: see <a href="https://github.com/eurosys18-Optimus/Optimus/tree/master/images/cpu">k8s-mxnet-cpu-experiment.Dockerfile</a> and <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/images/cpu/build.sh">build.sh</a> to see how to compile MXNet container. To get faster training speed on Intel CPU, set USE_MKL2017=1 and USE_MKL2017_EXPERIMENTAL=1 when building the container to enable Intel Math Kernel Library. To get even faster training speed, copy the  <a href="https://github.com/eurosys18-Optimus/Optimus/tree/master/mxnet/params_distribution/implementation">scripts</a> into the image to enable balanced parameter assignment.

(2) MXNet GPU container (if the server has NVIDIA GPUs): see <a href="https://github.com/eurosys18-Optimus/Optimus/tree/master/images/gpu">k8s-mxnet-gpu-experiment.Dockerfile</a> and <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/images/gpu/build.sh">build.sh</a>. Note that NVIDIA Docker plugin is required in such case, see https://github.com/NVIDIA/nvidia-docker/wiki/nvidia-docker-plugin for installation details.

### CUDA Environment
Run <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/nvidia/install-nvidia-driver-cuda-cudnn.sh">install-nvidia-driver-cuda-cudnn.sh</a> to install:

(1) NVIDIA Driver version >= 375.66;

(2) CUDA version >= 8.0.61;

(3) CuDNN Library version >= 6.0


## Jobs
### A Simple Example
To train a ResNet-50 model in a distributed way in k8s cluster,

(1) Set the number of parameter servers and workers, the HDFS URL of ImageNet dataset in <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/measurement/training-speed/measure-speed.py">measure-speed.py</a>;

(2) Run
```
$ python measure-speed.py
```

Basically, what it does is to sumbit a job to k8s and display training details(eg., training progress, speed, cpu usage) every 5 minutes. See <a href="https://github.com/eurosys18-Optimus/Optimus/tree/master/measurement/examples">here</a> for more examples.

### Submit Your Job
(1) Prepare the container: copy your program into the <a href="https://github.com/eurosys18-Optimus/Optimus/tree/master/images/gpu/scripts">script folder</a> under the image path and build the image by running
```
$ ./build.sh
```

(2) Similar to the simple example, configure job details such as image path, container resource requirement etc, and run <a href="https://github.com/eurosys18-Optimus/Optimus/blob/master/measurement/training-speed/measure-speed.py">measure-speed.py</a>



## More
Read the <a href="https://www.dropbox.com/s/2mlpu2tk74f8cta/technical_report.pdf?dl=0"> technical report </a> for the details of Optimus.
