import os
import sys
import time
import datetime
import logging
import math
import threading
from job import Job
import utils


	
#job_name_list = ['alexnet', 'resnet-50', 'vgg-11', 'inception-bn', 'resnet-152', 'resnet-101']
job_name_list = ['resnet-50', 'resnext-110', 'inception-bn', 'vgg', 'alexnet', 'lenet']
neural_network_list = ['resnet', 'resnext', 'inception-bn', 'vgg', 'alexnet', 'lenet']
num_layers_list = ['50', '110', '', '', '', '']

node_list = ['10.28.1.1', '10.28.1.2', '10.28.1.3', '10.28.1.4', '10.28.1.6', '10.28.1.7', '10.28.1.8']
ps_cpu = "4"
ps_mem = "8Gi"
worker_cpu = "4"
worker_mem = "8Gi"



	


def measure_speed():
	
	job_id = 0
	cwd = os.getcwd() + '/'
	stats = []	# element format (#ps, #worker, speed, cpu)
	txt = 'stats.txt'
	if os.path.isfile(txt):	# back up
		time_str = str(int(time.time()))
		fn =  './results/' + time_str + '.' + txt
		os.system('cp ' + txt + ' ' + fn)
	f = open(txt, 'w')	# clear txt
	f.close()
	
	num_node = len(node_list) * 7	# at most 42 pods in total
	kv_stores = ['dist_sync', 'dist_async']
	batch_sizes = ['1','2','4','8','16','32','64','128']
	
	tic = time.time()
	
	for job_index in range(len(job_name_list)):
		for kv_store in kv_stores:
			if kv_store == 'dist_sync':
				batch_size = '40'
			else:
				batch_size = '4'
			
			num_ps = 10
			num_worker = 20
			
			job_id += 1
		
			logger.info("------------------start job " + str(job_id) + "-------------------")
			toc = time.time()
			logger.info("time elapsed: " + str((toc-tic)/60) + " minutes" )
		
			measure_job = Job('measurement-imagenet', job_id, cwd)
			measure_job.set_ps_resources(num_ps,ps_cpu,ps_mem)
			#measure_job.set_ps_placement(node_list[:num_ps])

			measure_job.set_worker_resources(num_worker,worker_cpu,worker_mem)
			#measure_job.set_worker_placement(node_list[num_ps:num_ps+num_worker])
		
			placement_list = node_list * 7
			measure_job.set_ps_placement(placement_list[:num_ps])
			measure_job.set_worker_placement(placement_list[num_ps:num_ps+num_worker])
		
			image = 'yhpeng/k8s-mxnet-measurement'
			script = '/init.py'
			prog = '/mxnet/example/image-classification/train_imagenet.py'
			work_dir = '/mxnet/example/image-classification/data/'
			mount_dir_prefix = '/data/k8s-workdir/measurement/'
			measure_job.set_container(image, script, prog, work_dir, mount_dir_prefix)

			measure_job.set_data(data_train='imagenet_data_train_1.rec', data_val='',\
			hdfs_data_train='/k8s-mxnet/imagenet/imagenet_data_train_1.rec', hdfs_data_val='')
			measure_job.set_network(neural_network_list[job_index], num_layers_list[job_index])
			measure_job.set_training('100',batch_size,kv_store,gpus='')
			measure_job.set_disp('1')
			measure_job.set_mxnet(kv_store_big_array_bound=1000*1000)

			measure_job.start()
		
			counter = 0
			while(True):
				try:
					time.sleep(60)
				except:
					logger.info("detect Ctrl+C, exit...")
					measure_job.delete(True)
					sys.exit(0)
				
				counter += 1
				try:
					speed_list = measure_job.get_training_speed()
					(ps_metrics, worker_metrics) = measure_job.get_metrics()
				except:
					logger.info("get training speed error!")
					measure_job.delete(True)
					sys.exit(0)
				# compute cpu usage difference
				ps_cpu_usage_list = []
				for metrics in ps_metrics:
					ps_cpu_usage_list.append(metrics['cpu/usage_rate']/1000.0)
				ps_cpu_diff = max(ps_cpu_usage_list) - min(ps_cpu_usage_list)
				worker_cpu_usage_list = []
				for metrics in worker_metrics:
					worker_cpu_usage_list.append(metrics['cpu/usage_rate']/1000.0)
				worker_cpu_diff = max(worker_cpu_usage_list) - min(worker_cpu_usage_list)
			
				model_name = measure_job.get_model_name()
				logger.info("model name: " + model_name + ", kv_store: " + kv_store + ", batch_size: " + batch_size + \
				", num_ps: " + str(num_ps) + ", num_worker: " + str(num_worker) + \
				", speed_list: " + str(speed_list) + ", sum_speed (samples/second): " + str(sum(speed_list)) + \
				", sum_speed(batches/second): " + str(sum(speed_list)/int(batch_size)) + \
				", ps cpu usage diff: " + str(ps_cpu_diff) + \
				", worker cpu usage diff: " + str(worker_cpu_diff)
				)
				if counter >= 3:
					stat = (model_name, kv_store, batch_size, num_ps, num_worker, speed_list, sum(speed_list)/int(batch_size), ps_cpu_usage_list, worker_cpu_usage_list)
					stats.append(stat)
					with open(txt, 'a') as f:	# append
						#for stat in stats:
						f.write(str(stat) + '\n')
				
					measure_job.delete(True)
					logger.info("sleep 3 seconds before next job")
					time.sleep(3)
					break


def prepare_env():
	logger.info("clear all existing jobs")
	os.system("kubectl delete jobs,daemonsets --all")

	
	
def main():
	global logger
	
	logger = utils.getLogger('measure-speed')
	prepare_env()
	measure_speed()
	

if __name__ == '__main__':
	if len(sys.argv) != 1:
		print "Description: speed measurement script in k8s cluster, to explore how training speed changes with the number of parameter servers and workers"
		print "Usage: python measure-speed.py"
		sys.exit(1)
	main()