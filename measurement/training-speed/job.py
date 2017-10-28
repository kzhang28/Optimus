import time
import datetime
import os
import threading
import subprocess
import requests

class Job(object):
	'''job description.
	Parameters
	----------
	id: int
	num_ps: int
	num_worker: int
	other parameters: string or list of strings
	work to be done on Tuesday 8/8/2017: 
		(1) modify template file, worker and server mount different dirs
		(2) modify template file, set work_dir and export it as an env
		(3) add support for gpu and get_progress() if necessary
	
	
	'''
	def __init__(self, type, id, dir_prefix):
		'''initialize a job
		job type: eg., measurement-imagenet, i.e., category-dataset
		'''
		self.name = str(id) + '-' + type
		
		now = time.time()
		self.timestamp = str(datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d-%H:%M:%S'))
		self.dir = dir_prefix + self.name + '-' + self.timestamp + '/'
		os.system('mkdir -p ' + self.dir)
		
		self.num_ps = 0
		self.ps_cpu = '1'
		self.ps_mem = '2Gi'
		
		self.num_worker = 0
		self.worker_cpu = '1'
		self.worker_mem = '2Gi'
		
		self.ps_placement = ''
		self.worker_placement = ''
		
		self.disp_batches = '5'
		self.speed_list = []
		self.ps_metrics = []
		self.worker_metrics = []
		self.ps_pods = []
		self.worker_pods = []
		
		self.kv_store_big_array_bound = str(1000*1000)
		self.ps_verbose = ''
	
	def set_ps_resources(self, num_ps, ps_cpu, ps_mem):
		'''resource requirements of parameter servers'''
		self.num_ps = num_ps
		self.ps_cpu = ps_cpu
		self.ps_mem = ps_mem
	
	def set_worker_resources(self, num_worker, worker_cpu, worker_mem, worker_gpu=''):
		'''resource requirements of workers'''
		self.num_worker = num_worker
		self.worker_cpu = worker_cpu
		self.worker_mem = worker_mem
		self.worker_gpu = worker_gpu	# add support for gpu later
	
	def set_ps_placement(self, ps_placement):
		'''the placement of parameter servers'''
		if isinstance(ps_placement, list):
			if len(ps_placement) == self.num_ps:
				self.ps_placement = ps_placement
			else:
				raise RuntimeError('ps_placement is not consistent with num_ps')
		else:
			raise TypeError('ps_placement is not a list')
	
	def set_worker_placement(self, worker_placement):
		'''the placement of workers'''
		if isinstance(worker_placement, list):
			if len(worker_placement) == self.num_worker:
				self.worker_placement = worker_placement
			else:
				raise RuntimeError('worker_placement is not consistent with num_worker')
		else:
			raise TypeError('worker_placement is not a list')
	
	def _set_mount_dirs(self, type, mount_dir_prefix):
		'''directories on hosts mounted to containers'''
		mount_dirs = []
		if type == 'ps':
			for i in xrange(self.num_ps):
				postfix = self.name + '-ps-' + str(i) + '/'
				mount_dir = mount_dir_prefix + postfix
				mount_dirs.append(mount_dir)
				cmd = 'ssh ' + self.ps_placement[i] + ' "mkdir -p ' + mount_dir + '"'
				os.system(cmd)
		
		elif type == 'worker':
			for i in xrange(self.num_worker):
				postfix = self.name + '-worker-' + str(i) + '/'
				mount_dir = mount_dir_prefix + postfix
				mount_dirs.append(mount_dir)
				cmd = 'ssh ' + self.worker_placement[i] + ' "mkdir -p ' + mount_dir + '"'
				os.system(cmd)
		return mount_dirs
	
	def set_container(self, image, script, prog, work_dir, mount_dir_prefix, volume='k8s-mxnet-volume'):
		'''container description'''
		self.image = image
		self.script = script
		self.prog = prog
		self.work_dir = work_dir
		self.ps_mount_dirs = self._set_mount_dirs('ps', mount_dir_prefix)
		self.worker_mount_dirs = self._set_mount_dirs('worker', mount_dir_prefix)
		self.volume = volume
		
	def set_data(self, data_train='', data_val='', hdfs_data_train='', hdfs_data_val=''):
		'''data specification'''
		self.data_train = data_train
		self.data_val = data_val
		self.hdfs_data_train = hdfs_data_train
		self.hdfs_data_val = hdfs_data_val
	
	def set_network(self, neural_network='', num_layers=''):
		'''neural network'''
		self.neural_network = neural_network
		self.num_layers = num_layers
		if num_layers == '':
			self.model_name = self.neural_network
		else:
			self.model_name = self.neural_network + '-' + self.num_layers
	
	def set_training(self, num_epochs='', batch_size='', kv_store='local', gpus=''):
		'''training hyper-parameters'''
		self.num_epochs = num_epochs
		self.kv_store = kv_store
		self.gpus = gpus
		
		# the batch size of each worker for sync training may be different
		if kv_store == 'dist_async':
			self.batch_sizes = [batch_size for i in range(self.num_worker)]
		elif kv_store == 'dist_sync' or kv_store == 'dist_device_sync':
			tot_batch_size = int(batch_size)
			avg_batch_size = tot_batch_size / self.num_worker
			rem_batch_size = tot_batch_size % self.num_worker
			batch_sizes = [avg_batch_size for i in range(self.num_worker)]
			for i in range(rem_batch_size):
				batch_sizes[i] = batch_sizes[i] + 1
			self.batch_sizes = [str(i) for i in batch_sizes]
	
	def set_disp(self, disp_batches):
		'''display frequency'''
		self.disp_batches = str(disp_batches)
	
	def set_mxnet(self, kv_store_big_array_bound):
		'''set env MXNET_KVSTORE_BIGARRAY_BOUND'''
		self.kv_store_big_array_bound = str(kv_store_big_array_bound)
	
	def __list_to_str(self, _listofstr):
		string = ''
		for i in xrange(len(_listofstr)):
			if i < len(_listofstr) - 1:
				string = string + _listofstr[i] + ','
			else:
				string = string + _listofstr[i]
		return string
		
	def _create(self):
		'''create job definition, i.e., yaml file'''

		variables = {}
		variables['JOB_NAME'] = self.name
		
		variables['IMAGE'] = self.image
		variables['SCRIPT'] = self.script
		variables['PROG'] = self.prog
		variables['WORK_DIR'] = self.work_dir
		variables['PS_MOUNT_DIRS'] = self.__list_to_str(self.ps_mount_dirs)
		variables['WORKER_MOUNT_DIRS'] = self.__list_to_str(self.worker_mount_dirs)
		variables['VOLUME'] = self.volume
		
		variables['NUM_PS'] = str(self.num_ps)
		variables['PS_CPU'] = self.ps_cpu
		variables['PS_MEM'] = self.ps_mem
		
		variables['NUM_WORKER'] = str(self.num_worker)
		variables['WORKER_CPU'] = self.worker_cpu
		variables['WORKER_MEM'] = self.worker_mem
		
		variables['DATA_TRAIN'] = self.data_train
		variables['DATA_VAL'] = self.data_val
		
		variables['PS_PLACEMENT'] = self.__list_to_str(self.ps_placement)
		variables['WORKER_PLACEMENT'] = self.__list_to_str(self.worker_placement)
		
		variables['NEURAL_NETWORK'] = self.neural_network
		variables['NUM_LAYERS'] = self.num_layers
		
		variables['NUM_EPOCHS'] = self.num_epochs
		variables['BATCH_SIZES'] = self.__list_to_str(self.batch_sizes)
		variables['KV_STORE'] = self.kv_store
		variables['GPUS'] = self.gpus
		
		variables['DISP_BATCHES'] = self.disp_batches
		
		variables['MXNET_KVSTORE_BIGARRAY_BOUND'] = self.kv_store_big_array_bound
		variables['PS_VERBOSE'] = self.ps_verbose
		
		# copy template file
		self.jinja = self.dir + self.name + '.jinja'
		os.system("cp ~/k8s-mxnet/templates/k8s-mxnet-template.jinja " + self.jinja)
		
		# replace variables in jinja file
		temp_file = self.jinja + '.temp'
		for key, value in variables.items():
			os.system('sed -e "s@\$' + key + '@' + value + '@g" "' + self.jinja + '"' + ' > ' + temp_file)
			os.system('rm ' + self.jinja)
			os.system('mv ' + temp_file + ' ' + self.jinja)
			
		# generate yaml file
		self.yaml = self.dir + self.name + '.yaml'
		os.system("python ~/k8s-mxnet/templates/render-template.py " + self.jinja + " > " + self.yaml)
	
	def _read_data(self):
		'''read data from HDFS'''
		if self.hdfs_data_train is None or self.hdfs_data_train == '':
			raise ValueError('hdfs_data_train is not specified')
		thread_list = []
		for i in xrange(self.num_worker):
			node = self.worker_placement[i]
			
			# get training data
			local_file = self.worker_mount_dirs[i] + self.data_train
			cmd_train = 'ssh ' + node + ' "/usr/local/hadoop/bin/hadoop fs -copyToLocal ' + self.hdfs_data_train + ' ' + local_file + '"'
			thread_train = threading.Thread(target=(lambda cmd_train=cmd_train: os.system(cmd_train)), args=())
			thread_train.start()
			thread_list.append(thread_train)
			#time.sleep(0.01)
			
			# get validation data
			if self.hdfs_data_val is not None and self.hdfs_data_val != '':
				local_file = self.worker_mount_dirs[i] +  self.data_val
				cmd_val = 'ssh ' + node + ' "/usr/local/hadoop/bin/hadoop fs -copyToLocal ' + self.hdfs_data_val + ' ' + local_file + '"'
				thread_val = threading.Thread(target=(lambda cmd_val=cmd_val: os.system(cmd_val)), args=())
				thread_val.start()
				thread_list.append(thread_val)
				#time.sleep(0.01)
		for thread in thread_list:
			thread.join()	# sometimes the thread would be blocked here due to unknown reason
	
	def _read_progress(self):
		'''get the job progress from each worker'''
		return
		
	def _read_training_speed(self):
		'''get the job training speed from each worker'''
		speed_fn = 'speed.txt'
		if self.speed_list is None or self.speed_list == []:
			self.speed_list = [0 for i in xrange(self.num_worker)]
		thread_list = []
		for i in xrange(self.num_worker):
			node = self.worker_placement[i]
			local_file = self.worker_mount_dirs[i] + speed_fn
			'''
			cmd = 'scp ' + node + ':' + local_file + ' ' + self.dir # the new txt will replace the old one, no need to delete
			os.system(cmd)
			try:
				with open(self.dir+speed_fn, 'r') as fh:
					stb_speed = float(fh.readline().replace('\n', '').split(' ')[1])
					self.speed_list[i] = float('%.3f'%(stb_speed))
			except Exception as e:
				print e
				continue
			'''
			cmd = "ssh " + node + " 'cat " + local_file + "'"
			def run(self, cmd, i):
				try:
					output = subprocess.check_output(cmd, shell=True)
					# the other side is opening and writing the file, try again
					counter = 0
					while(output == '' or output == None):
						output = subprocess.check_output(cmd, shell=True)
						time.sleep(0.001*(10**counter))
						counter = counter + 1
						if counter > 2:
							break
					stb_speed = float(output.replace('\n', '').split(' ')[1])
					self.speed_list[i] = float('%.3f'%(stb_speed))
				except Exception as e:
					print e
					
			thread = threading.Thread(target=run, args=(self, cmd, i))
			thread.start()
			thread_list.append(thread)
		for thread in thread_list:
			thread.join()
	
	def get_model_name(self):
		return self.model_name
			
	def get_training_speed(self):
		self._read_training_speed()
		return list(self.speed_list)
	
	def __get_pods(self, task):
		'''
		get the names of the pods belonging to the task
		
		NAME                                    READY     STATUS    RESTARTS   AGE
		1-measurement-imagenet-ps-0-mzv2z       1/1       Running   0          1m
		'''
		if task == 'ps':
			self.ps_pods = []
		elif task == 'worker':
			self.worker_pods = []
		else:
			raise ValueError('task can only either be ps or worker!') 

		cmd = 'kubectl get pods --selector=' + 'name=' + self.name + ',' + 'job=' + task + ' --namespace=default' + ' |grep ' + task
		output = subprocess.check_output(cmd, shell=True)
		lines = output.split('\n')
		for line in lines:
			if len(line) > 0:
				words = line.split(' ')
				if task == 'ps':
					self.ps_pods.append(words[0])
				else:
					self.worker_pods.append(words[0])
		
	def _read_metrics(self):
		'''get the metrics of the pods of this job'''
		
		# get ps pods
		self.__get_pods('ps')
		self.__get_pods('worker')
		
		# get heapster cluster ip
		# heapster               192.168.192.16    <none>        80/TCP              5d
		cmd = "kubectl get services --namespace=kube-system | grep heapster |awk '{print $2}'"
		heapster_cluster_ip = subprocess.check_output(cmd, shell=True).replace('\n','')
		if heapster_cluster_ip == '':
			heapster_cluster_ip = '192.168.192.16'
		
		'''
		{
		  "metrics": [
		   {
		    "timestamp": "2017-08-14T08:10:00Z",
		    "value": 0
		   }
		  ],
		  "latestTimestamp": "2017-08-14T08:10:00Z"
		 }
		'''
		self.ps_metrics = []
		self.worker_metrics = []
		metric_keys = ['cpu/usage_rate', 'memory/usage', 'network/tx_rate', 'network/rx_rate']	# cpu: milli core, mem: bytes, net: bytes/second
		for pod in (self.ps_pods + self.worker_pods):
			pod_metrics = {}
			for metric_key in metric_keys:
				url = 'http://' + heapster_cluster_ip + '/api/v1/model/namespaces/default/pods/' + pod + '/metrics/' + metric_key
				try:
					output = requests.get(url, verify=False).json()
					metric_value = int(output['metrics'][-1]['value'])	# get latest value, maybe empty since heapster update metrics per minute
				except:
					# print "ERROR when requesting pod metrics!"
					metric_value = 0
				pod_metrics[metric_key] = metric_value
			if pod in self.ps_pods:
				self.ps_metrics.append(pod_metrics)
			else:
				self.worker_metrics.append(pod_metrics)


	def get_metrics(self):
		self._read_metrics()
		return (list(self.ps_metrics), list(self.worker_metrics))
		
	
	def start(self):
		'''start the job in k8s'''
		self._create()
		self._read_data()
		os.system("kubectl create -f " + self.yaml)
		
		
	
	def delete(self, del_all=False):
		'''delete the job.
		Parameters
		----------
		del_all: whether to delete all, including histories.
		'''
		
		# shutdown job in k8s
		temp_dir = self.dir + 'temp/'
		os.system('mkdir -p ' + temp_dir)
		
		fh = open(self.yaml, 'r')
		yamls = fh.read().split('---\n')
		fh.close()
		
		thread_list = []
		for i in range(len(yamls)):
			if len(yamls[i]) <= 1:	#skip invalid
				continue
			name = temp_dir + str(i) + '.yaml'
			with open(name, 'w') as fh:
				fh.write(yamls[i])
			thread = threading.Thread(target=(lambda name=name: os.system('kubectl delete -f ' + name)), args=())
			thread.start()
			thread_list.append(thread)
			#time.sleep(0.01)	# to avoid thread conflict reading the same variable name
		
		for thread in thread_list:
			thread.join()
		os.system('rm -r ' + temp_dir)
		
		# in case not delete all
		os.system('kubectl delete jobs --selector=name=' + self.name)
		
		if del_all == False:
			return
		
		# remove mounted dirs on hosts
		thread_list = []
		for i in xrange(self.num_worker):
			node = self.worker_placement[i]
			worker_mount_dir = self.worker_mount_dirs[i]
			cmd = 'timeout 10 ssh ' + node + ' "sudo rm -r ' + worker_mount_dir + '"'
			thread = threading.Thread(target=(lambda cmd=cmd: os.system(cmd)), args=())
			thread.start()
			thread_list.append(thread)
			
		for i in xrange(self.num_ps):
			node = self.ps_placement[i]
			ps_mount_dir = self.ps_mount_dirs[i]
			cmd = 'timeout 10 ssh ' + node + ' "sudo rm -r ' + ps_mount_dir + '"'
			thread = threading.Thread(target=(lambda cmd=cmd: os.system(cmd)), args=())
			thread.start()
			thread_list.append(thread)
		for thread in thread_list:
			thread.join()
		# delete job working dir
		os.system('rm -r ' + self.dir)	
		
		
		
		
		
		
		
		
		
		