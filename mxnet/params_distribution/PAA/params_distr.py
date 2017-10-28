import math
import sys
import operator
import ast

num_ps = 10


# MXNet
def mxnet(model):
	THRESHOLD = 1000*1000
	pskv = [[] for i in range(num_ps)]
	
	for params_size in model:
		key = model.index(params_size)
		if params_size < THRESHOLD:	# a randomly picked server
			server = (key * 9973) % num_ps
			pskv[server].append((key, params_size))
		else:	# partition to all servers
			for i in range(num_ps):
				part_size = int(round(float(params_size)/num_ps*(i+1)) - round(float(params_size)/num_ps*i))
				pskv[i].append((key, part_size))
			
	# sum each server's workload and connection
	sizes = [0 for i in range(num_ps)]
	conns = [0 for i in range(num_ps)]
	for i in range(num_ps):
		server_params_blocks = pskv[i]
		for (key, params_size) in server_params_blocks:
			sizes[i] += params_size
			conns[i] += 1
			
	print '-------------- MXNet scheme --------------'
	print 'load distribution: ', sizes
	print 'load max diff: ', max(sizes)-min(sizes)
	print 'conn distribution: ', conns
	print '# of connections: ', sum(conns)
	print 'partion extent index: ', float(sum(conns))/len(model)
	
	return (pskv, sizes, sum(conns))



# TensorFlow
def tf(model):
	pskv = [[] for i in range(num_ps)]
	for params_size in model:
		key = model.index(params_size)
		server = key % num_ps	# round-robin
		pskv[server].append((key, params_size))
		
	# sum each server's workload and connection
	sizes = [0 for i in range(num_ps)]
	conns = [0 for i in range(num_ps)]
	for i in range(num_ps):
		server_params_blocks = pskv[i]
		for (key, params_size) in server_params_blocks:
			sizes[i] += params_size
			conns[i] += 1
	print '-------------- TensorFlow scheme --------------'
	print 'load distribution: ', sizes
	print 'load max diff: ', max(sizes)-min(sizes)
	print 'conn distribution: ', conns
	print '# of connections: ', sum(conns)
	print 'partion extent index: ', float(sum(conns))/len(model)
	
	return (pskv, sizes, sum(conns))


def best_fit_descend(model):
	pskv = [[] for i in range(num_ps)]
	sizes = [0 for i in range(num_ps)]
	conns = [0 for i in range(num_ps)]
	avg = int(math.ceil(sum(model)/num_ps))
	OVERFLOWRATE = 1.0	# adjust this to obtain better results, to balance communication overhead since the largest one has lower comm overhead
	SMALLSIZERATE = 1/(float(num_ps))/100	# if the size of a parameter block is too small (<0.1% of the model size), the main overhead is comm.
	sorted_model = sorted(enumerate(model), key=operator.itemgetter(1), reverse=True)	# sorted from high to low
	
	# best fit algorithm
	def best_fit_alg(cap, cur_sizes, item_size):
		min_fit_size = sys.maxint
		server = -1
		for size in cur_sizes:
			surplus = cap - size - item_size		# need more consideration
			if surplus >= 0 and surplus < min_fit_size:
				min_fit_size = surplus
				server = cur_sizes.index(size)
		
		if server == -1:	# can not be fitted, must overflow, place it to the bin with most empty space
			bottom = min(cur_sizes)
			server = cur_sizes.index(bottom)
		return server
		
	params_ps_map = {}
	for (key, params_size) in sorted_model:
		params_ps_map[key] = []
		if params_size <= SMALLSIZERATE*sum(model):
			server = conns.index(min(conns))
			pskv[server].append((key, params_size))
			sizes[server] += params_size
			conns[server] += 1
			params_ps_map[key] = [(server, params_size)]
			
		elif params_size <= avg:
			server = best_fit_alg(avg, sizes, params_size)
			pskv[server].append((key, params_size))
			sizes[server] += params_size
			conns[server] += 1
			params_ps_map[key] = [(server, params_size)]
		else:
			sorted_sizes = sorted(enumerate(sizes), key=operator.itemgetter(1))	# sorted from low to high
			counter = 0
			while params_size > 0:
				(server, size) = sorted_sizes[counter]
				surplus = int(OVERFLOWRATE*avg) - size
				if params_size >= surplus:
					pskv[server].append((key, surplus))
					sizes[server] += surplus
					conns[server] += 1
					params_ps_map[key].append((server, surplus))
					params_size -= surplus
					counter += 1
				else:	# the last part uses best fit
					server = best_fit_alg(avg, sizes, params_size)
					pskv[server].append((key, params_size))
					sizes[server] += params_size
					conns[server] += 1
					params_ps_map[key].append((server, params_size))
					params_size -= params_size
	
	for key, elem in params_ps_map.items():
		elem.sort(key=operator.itemgetter(0))
	#print params_ps_map
	
	# sum each server's workload and connection
	print '-------------- BestFit Descending scheme --------------'
	print 'load distribution: ', sizes
	print 'load max diff: ', max(sizes)-min(sizes)
	print 'conn distribution: ', conns
	print '# of connections: ', sum(conns)
	print 'partion extent index: ', float(sum(conns))/len(model)
	
	return (pskv, sizes, sum(conns))
	
		
	
def main():
	# size of each parameter block for each model
	models = []
	
	# read models from file
	fn = 'model_shapes.txt'
	with open(fn, 'r') as fh:
		for line in fh:
			models.append(ast.literal_eval(line.replace('\n','')))

	for model in models:
		(model_spec, model_shape) = model
		#if 'inception-bn' not in model_spec:
		#	continue
		print '****************', model_spec, '****************'
		print 'model args #:', len(model_shape), ', model size:', '%.2f'%(1.0*sum(model_shape)/(10**6))+'M'
		# print model_shape
		mxnet(model_shape)
		tf(model_shape)
		best_fit_descend(model_shape)
	
		
		
if __name__ == '__main__':
	if len(sys.argv) != 1:
		print "Compare different algorithms of parameter distribution on parameter servers"
		print "Usage: python params_distr.py"
		sys.exit(1)
	main()
		
		
		
		