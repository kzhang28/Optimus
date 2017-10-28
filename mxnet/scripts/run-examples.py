import os
import sys
import subprocess
import time
import logging

logging.basicConfig(filename="run-examples.log", filemode="w", level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

LOGDIR="/home/net/run-examples"

	
# train CNN-rand
def run_CNN_rand_MR():
	cmd = "cd ~/mxnet/example/cnn_text_classification; "
	cmd += "python text_cnn.py --gpus 0 --kv-store device --num-epochs 200 --optimizer rmsprop --dropout 0; "
	cmd += "cp cnn-text-classification.log " + LOGDIR + "/CNN-rand_MR.log"
	return cmd


# train language model, error after epoch 126
def run_RNN_LSTM_Dropout_PTB():
	cmd = "cd ~/mxnet/example/gluon/word_language_model; "
	cmd += "python train.py --cuda --epochs 200 --dropout 0.2 > word_language_model.log; "
	cmd += "cp word_language_model.log " + LOGDIR + "/RNN-LSTM-Dropout_PTB.log"
	return cmd

	
# train DSSM
def run_DSSM_text8():
	cmd = "cd ~/mxnet/example/nce-loss; "
	cmd += "python wordvec_subwords.py --gpu; "
	cmd += "cp wordvec_subwords.log " + LOGDIR + "/DSSM_text8.log"
	return cmd
	

# train cifar10
def run_ResNext_50_CIFAR10():
	cmd = "cd ~/mxnet/example/image-classification; "
	cmd += "python train_cifar10.py --network resnext --num-layers 50 --gpus 0,1  --num-epochs 200 --kv-store local; "
	cmd += "cp cifar10.log " + LOGDIR + "/ResNext-50_CIFAR10.log"
	return cmd
	
	
def run_ResNext_110_CIFAR10():
	cmd = "cd ~/mxnet/example/image-classification; "
	cmd += "python train_cifar10.py --network resnext --num-layers 110 --gpus 0,1  --num-epochs 200 --kv-store local; "
	cmd += "cp cifar10.log " + LOGDIR + "/ResNext-110_CIFAR10.log"
	return cmd
	
	
def run_ResNext_152_CIFAR10():
	cmd = "cd ~/mxnet/example/image-classification; "
	cmd += "python train_cifar10.py --network resnext --num-layers 152 --gpus 0,1  --num-epochs 200 --kv-store local; "
	cmd += "cp cifar10.log " + LOGDIR + "/ResNext-152_CIFAR10.log"
	return cmd
	
	
# train mnist	
def run_MLP_MNIST():
	cmd = "cd ~/mxnet/example/image-classification; "
	cmd += "python train_mnist.py --gpus 0; "
	cmd += "cp mnist.log " + LOGDIR + "/MLP_MNIST.log"
	return cmd

	
def main(ids):
	
	start = time.time()
	
	if not os.path.exists(LOGDIR):
		os.system("mkdir " + LOGDIR)
	
	ids = [int(id) for id in ids.split(',')]
	if len(ids) == 1 and ids[0] == 0:
		logging.info("running all examples...")
		ids = [i for i in range(1,8)]
		
	for id in ids:
		if id == 1:
			logging.info("running ResNext-50_CIFAR10...")
			cmd = run_ResNext_50_CIFAR10()
		elif id == 2:
			logging.info("running ResNext-110_CIFAR10...")
			cmd = run_ResNext_110_CIFAR10()
		elif id == 3:
			logging.info("running ResNext-152_CIFAR10...")
			cmd = run_ResNext_152_CIFAR10()
		elif id == 4:
			logging.info("running MLP_MNIST...")
			cmd = run_MLP_MNIST()
		elif id == 5:
			logging.info("running DSSM_text8...")
			cmd = run_DSSM_text8()
		elif id == 6:
			logging.info("running CNN-rand_MR...")
			cmd = run_CNN_rand_MR()
		elif id == 7:
			logging.info("running RNN-LSTM-Dropout_PTB...")
			cmd = run_RNN_LSTM_Dropout_PTB()
		
		tic = time.time()
		try:
			subprocess.check_output(cmd, shell=True)
		except Exception as e:
			logging.error(str(e))
		toc = time.time()
		logging.info("id: " + str(id) + ", running time: " + '%.3f'%((toc-tic)*1.0/60/60) + "h.")

	end = time.time()
	logging.info("total running time: " + '%.3f'%((end-start)*1.0/60/60) + "h.")

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Description: run mxnet examples"
		print "Usage: python run-examples.py id1,id2"
		sys.exit(1)
	main(sys.argv[1])
