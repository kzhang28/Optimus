import sys
from importlib import import_module


def main():
	fn = 'model_shapes.txt'
	fh = open(fn, 'w')
	fh.close()
	data_names = ['data']
	label_names = ['softmax_label']
	input_names = data_names + label_names
	
	# model = (network, num_layers, num_classes, image_shape, batch_size)
	# image_shape = 'nchannel, height, width'
	models = []
	
	lenet = ('lenet', None, 1000, '3,54,54', 1)
	mlp = ('mlp', None, 1000, '3,54,54', 1)
	resnet50 = ('resnet', 50, 1000, '3,54,54', 1)	# the layer can be 18,34,50,101,152,200,269
	resnet101 = ('resnet', 101, 1000, '3,224,224', 1)
	resnet152 = ('resnet', 152, 1000, '3,224,224', 1)
	resnext50 = ('resnext', 50, 1000, '3,224,224', 1)
	resnext101 = ('resnext', 101, 1000, '3,224,224', 1)
	resnext152 = ('resnext', 152, 1000, '3,224,224', 1)
	alexnet = ('alexnet', None, 1000, '3,224,224', 1)
	alexnet_fp16 = ('alexnet_fp16', None, 1000, '3,224,224', 1)
	inception_bn = ('inception-bn', None, 1000, '3,224,224', 1)
	inception_v3 = ('inception-v3', None, 1000, '3,300,300', 1)
	googlenet = ('googlenet', None, 1000, '3,300,300', 1)
	vgg = ('vgg', None, 1000, '3,224,224', 1)
	# and more ...
	
	models.append(lenet)
	models.append(mlp)
	models.append(resnet50)
	models.append(resnet101)
	models.append(resnet152)
	models.append(resnext50)
	models.append(resnext101)
	models.append(resnext152)
	models.append(alexnet)
	models.append(alexnet_fp16)
	models.append(inception_bn)
	models.append(inception_v3)
	models.append(googlenet)
	models.append(vgg)
	
	
	for model in models:
		print model
		(network, num_layers, num_classes, image_shape, batch_size) = model
		net = import_module('symbols.'+network)
		sym = net.get_symbol(num_classes=num_classes, num_layers=num_layers, image_shape=image_shape)	# '3,54,54'
		
		arg_names = sym.list_arguments()
		param_names = [x for x in arg_names if x not in input_names]
		
		image_shape = [int(l) for l in image_shape.split(',')]
		(nchannel, height, width) = image_shape
		arg_shape, output_shape, aux_shape = sym.infer_shape(data=(batch_size, nchannel, height, width))
		
		data_shape = arg_shape[0]
		label_shape = arg_shape[-1]
		param_shape = arg_shape[1:len(arg_shape)-1]
		
		assert len(param_names) == len(param_shape)
		param_sizes = []
		for tuple in param_shape:
			size = 1
			for elem in tuple:
				size *= elem
			param_sizes.append(size)
		
		# write to file, or line by line
		with open(fn,'a') as f:
			f.write(str((model, param_sizes)) + '\n')



if __name__ == '__main__':
	if len(sys.argv) != 1:
		print "Get the size of each model"
		print "Usage: python params_distr.py"
		sys.exit(1)
	main()
