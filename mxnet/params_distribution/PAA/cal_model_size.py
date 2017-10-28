def cal_model_size(sym, data_iter):
	arg_shape, output_shape, aux_shape = sym.infer_shape(data=data_iter.provide_data[0].shape)	#check all the necessary input shape
		
	data_shape = arg_shape[0]
	label_shape = arg_shape[-1]
	param_shape = arg_shape[1:len(arg_shape)-1]
	
	param_sizes = []
	for tuple in param_shape:
		size = 1
		for elem in tuple:
			size *= elem
			param_sizes.append(size)
	print 'model size: ', '%.2f'%(1.0*sum(param_sizes)/(10**6)) ,'M'
