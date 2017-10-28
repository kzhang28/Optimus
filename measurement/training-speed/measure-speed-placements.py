import os
import sys
import time
import datetime
import logging
import math
import threading
from job import Job
import utils
import Queue

	
job_name_list = ['alexnet', 'resnet-50', 'vgg-11', 'inception-bn', 'resnet-152', 'resnet-101']
neural_network_list = ['alexnet', 'resnet', 'vgg', 'inception-bn', 'resnet', 'resnet']
num_layers_list = ['', '50', '', '', '152', '101']

node_list = ['10.28.1.1', '10.28.1.2', '10.28.1.3', '10.28.1.4', '10.28.1.6', '10.28.1.7', '10.28.1.8']
NODE_CPU_CAP = [5, 6, 6, 7, 8, 7, 6] # to avoid same placement for RR and LL

NODE_MEM = 60

ps_cpu = "1"
ps_mem = "2Gi"
worker_cpu = "1"
worker_mem = "4Gi"

ps_cpu_int = 1
ps_mem_int = 2
worker_cpu_int = 1
worker_mem_int = 4



def PAA(num_ps, num_worker):
	# keep track of available resources on each node.
	node_used_cpu_list = [0 for i in range(len(node_list))]
	node_used_mem_list = [0 for i in range(len(node_list))]

	cpu_avail_queue = Queue.PriorityQueue()
	# sort nodes based on available cpus, since cpu is usually the bottleneck
	for i in range(len(node_list)):
		cpu_avail_queue.put((node_used_cpu_list[i]-NODE_CPU_CAP[i], i))

	cand_place_nodes = []
	while not cpu_avail_queue.empty():
		avail_cpu, node_index = cpu_avail_queue.get()
		cand_place_nodes.append(node_index)

		fit_flag = True  # whether these nodes can hold the job
		ps_already_deduct = False
		ps_nodes = []
		for i in range(num_ps):
			node = cand_place_nodes[i % len(cand_place_nodes)]
			if node_used_cpu_list[node] + ps_cpu_int <= NODE_CPU_CAP[node_index] and node_used_mem_list[node] + ps_mem_int <= NODE_MEM:
				ps_nodes.append(node)
				node_used_cpu_list[node] += ps_cpu_int
				node_used_mem_list[node] += ps_mem_int
			else:
				fit_flag = False
				for node in ps_nodes:
					node_used_cpu_list[node] -= ps_cpu_int
					node_used_mem_list[node] -= ps_mem_int
				ps_already_deduct = True
				break

		worker_nodes = []
		for i in range(num_worker):
			# also place worker evenly
			node = cand_place_nodes[i % len(cand_place_nodes)]
			# check whether resource is enough to place this ps
			if node_used_cpu_list[node] + worker_cpu_int <= NODE_CPU_CAP[node_index] and node_used_mem_list[node] + worker_mem_int <= NODE_MEM:
				worker_nodes.append(node)
				node_used_cpu_list[node] += worker_cpu_int
				node_used_mem_list[node] += worker_mem_int
			else:
				fit_flag = False
				# add the deducted resource back
				if not ps_already_deduct:
					for node in ps_nodes:
						node_used_cpu_list[node] -= ps_cpu_int
						node_used_mem_list[node] -= ps_mem_int
				for node in worker_nodes:
					node_used_cpu_list[node] -= worker_cpu_int
					node_used_mem_list[node] -= worker_mem_int
				break

		if fit_flag:
			ps_placement = [node_list[node] for node in ps_nodes]
			worker_placement = [node_list[node] for node in worker_nodes]
			for node in cand_place_nodes:  # enqueue them back
				cpu_avail_queue.put((node_used_cpu_list[node]-NODE_CPU_CAP[node], node))
			break
		else:
			if not cpu_avail_queue.empty():
				# print "should be all zero", node_used_cpu_list
				#print ps_nodes, worker_nodes
				continue  # add one more node to see if the job can be fitted
			else:
				logger.info("no enough resources to place ps and worker")
				break

	#print cand_place_nodes
	#print node_used_cpu_list
	return (ps_placement, worker_placement)




def LL(num_ps, num_worker):
	ps_placement = []
	worker_placement = []
	node_cpu_used = [0 for i in range(len(node_list))]
	node_mem_used = [0 for i in range(len(node_list))]

	node_queue = Queue.PriorityQueue()
	for i in range(len(node_list)):
		node_queue.put((node_cpu_used[i]-NODE_CPU_CAP[i], i))

	for i in range(num_ps):
		succ = False
		while not node_queue.empty():
			(capa, node_index) = node_queue.get()
			if node_cpu_used[node_index] + ps_cpu_int <= NODE_CPU_CAP[node_index] and node_mem_used[node_index] + ps_mem_int <= NODE_MEM:
				ps_placement.append(node_list[node_index])
				node_cpu_used[node_index] += ps_cpu_int
				node_mem_used[node_index] += ps_mem_int
				succ = True
				node_queue.put((node_cpu_used[node_index]-NODE_CPU_CAP[node_index], node_index))
				break
			else:
				# the next one must have no enough resource
				break

		if succ == False:
			logger.info("LL error, no enough resources for ps")
			break

	for i in range(num_worker):
		succ = False
		while not node_queue.empty():
			(capa, node_index) = node_queue.get()
			if node_cpu_used[node_index] + worker_cpu_int <= NODE_CPU_CAP[node_index] and node_mem_used[node_index] + worker_mem_int <= NODE_MEM:
				worker_placement.append(node_list[node_index])
				node_cpu_used[node_index] += worker_cpu_int
				node_mem_used[node_index] += worker_mem_int
				succ = True
				node_queue.put((node_cpu_used[node_index]-NODE_CPU_CAP[node_index], node_index))
				break
			else:
				# the next one must have no enough resource
				break

		if succ == False:
			logger.info("LL error, no enough resources for worker")
			break
	return (ps_placement, worker_placement)






def RR(num_ps, num_worker):
	ps_placement = []
	worker_placement = []
	cur_index = 0
	node_cpu_used = [0 for i in range(len(node_list))]
	node_mem_used = [0 for i in range(len(node_list))]

	# allocate ps first
	for i in range(num_ps):
		succ = False
		for j in range(len(node_list)):
			node_index = (cur_index + j) % len(node_list)
			if node_cpu_used[node_index] + ps_cpu_int <= NODE_CPU_CAP[node_index] and node_mem_used[node_index] + ps_mem_int <= NODE_MEM:
				ps_placement.append(node_list[node_index])
				node_cpu_used[node_index] += ps_cpu_int
				node_mem_used[node_index] += ps_mem_int
				cur_index = node_index + 1
				succ = True
				break
		if succ == False:
			logger.info("RR error, no enough resources for ps")
			break

	# allocate workers
	for i in range(num_worker):
		succ = False
		for j in range(len(node_list)):
			node_index = (cur_index + j) % len(node_list)
			if node_cpu_used[node_index] + worker_cpu_int <= NODE_CPU_CAP[node_index] and node_mem_used[node_index] + worker_mem_int <= NODE_MEM:
				worker_placement.append(node_list[node_index])
				node_cpu_used[node_index] += worker_cpu_int
				node_mem_used[node_index] += worker_mem_int
				cur_index = node_index + 1
				succ = True
				break
		if succ == False:
			logger.info("RR error, no enough resources for worker")
			break

	return (ps_placement, worker_placement)





def measure_speed():
	job_id = 0
	cwd = os.getcwd() + '/'
	stats = []	# element format (#ps, #worker, speed, cpu)
	txt = 'stats-placement.txt'
	if os.path.isfile(txt):	# back up
		time_str = str(int(time.time()))
		fn =  './results/' + time_str + '.' + txt
		os.system('cp ' + txt + ' ' + fn)
	f = open(txt, 'w')	# clear txt
	f.close()

	kv_stores = ['dist_async', 'dist_sync']
	batch_sizes = ['1','2','4','8','16','32','64','128']
	algs = ['PAA','LL','RR']

	tic = time.time()

	for alg in algs:
		for kv_store in kv_stores:
			if 'async' in kv_store:
				batch_size = '4'
			else:
				batch_size = '40'
			for num_ps in xrange(2, 16, 1):	# to save time, change to xrange(1, num_node, 2)
				num_worker = num_ps
				job_id += 1

				logger.info("------------------start job " + str(job_id) + "-------------------")
				toc = time.time()
				logger.info("time elapsed: " + str((toc-tic)/60) + " minutes" )

				measure_job = Job('measurement-imagenet', job_id, cwd)
				measure_job.set_ps_resources(num_ps,ps_cpu,ps_mem)
				measure_job.set_worker_resources(num_worker,worker_cpu,worker_mem)

				try:
					if alg == "PAA":
						(ps_placement, worker_placement) = PAA(num_ps, num_worker)
					elif alg == 'LL':
						(ps_placement, worker_placement) = LL(num_ps, num_worker)
					elif alg == 'RR':
						(ps_placement, worker_placement) = RR(num_ps, num_worker)

					logger.info("ps placement: " + str(ps_placement) + ", worker_placement: " + str(worker_placement))
					measure_job.set_ps_placement(ps_placement)
					measure_job.set_worker_placement(worker_placement)
				except Exception as e:
					logging.error("set placement error, break" + str(e))
					break

				image = 'yhpeng/k8s-mxnet-measurement'
				script = '/init.py'
				prog = '/mxnet/example/image-classification/train_imagenet.py'
				work_dir = '/mxnet/example/image-classification/data/'
				mount_dir_prefix = '/data/k8s-workdir/measurement/'
				measure_job.set_container(image, script, prog, work_dir, mount_dir_prefix)

				measure_job.set_data(data_train='imagenet_data_train_1.rec', data_val='',\
				hdfs_data_train='/k8s-mxnet/imagenet/imagenet_data_train_1.rec', hdfs_data_val='')
				measure_job.set_network('lenet', '50')  # try inception-bn
				measure_job.set_training('1000',batch_size,kv_store,gpus='')
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
					logger.info("alg: " + alg + ", model name: " + model_name + ", kv_store: " + kv_store + ", batch_size: " + batch_size + \
					", num_ps: " + str(num_ps) + ", num_worker: " + str(num_worker) + \
					", speed_list: " + str(speed_list) + ", sum_speed (samples/second): " + str(sum(speed_list)) + \
					", sum_speed(batches/second): " + str(sum(speed_list)/int(batch_size)) + \
					", ps cpu usage diff: " + str(ps_cpu_diff) + \
					", worker cpu usage diff: " + str(worker_cpu_diff)
					)
					if counter >= 2:
						stat = (alg, model_name, kv_store, batch_size, num_ps, num_worker, float('%.3f'%(sum(speed_list)/int(batch_size))), speed_list, ps_cpu_usage_list, worker_cpu_usage_list)
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