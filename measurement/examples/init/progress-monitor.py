import os
import logging
import time
import sys
import subprocess

logging.basicConfig(level=logging.INFO,	format='%(asctime)s.%(msecs)03d %(module)s %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
ROLE = os.getenv("ROLE")
WORK_DIR = os.getenv("WORK_DIR")

# read the log file and monitor the training progress
# give log file name
# give record file name
# run the function in a separate thread
def update_progress(logfile, recordfile):
	filesize = 0
	line_number = 0
	
	# logfile = 'training.log'
	# recordfile = 'progress.txt'
	# epoch batch

	logging.info('starting progress monitor to track training progress ...')

	# Epoch[0] Time cost=50.885
	# Epoch[0] Batch [70]	Speed: 1.08 samples/sec	accuracy=0.000000
	# Epoch[0] Train-accuracy=0.116071
	# Epoch[0] Train-cross-entropy=2.297981
	# Epoch[0] Time-cost=565.757 seconds
	# Epoch[0] Validation-accuracy=0.113854
	# Epoch[0] Validation-cross-entropy=2.301194
	epoch = 0
	batch = 0
	train_acc = []
	train_loss = []
	val_acc = []
	val_loss = []
	time_cost = []
	stat_dict = dict()
	disp_interval = 0
	with open(recordfile, 'w') as fh:
		fh.write(str(stat_dict) + '\n')
		fh.flush()

	while True:
		time.sleep(5)
		disp_interval += 5
		try:
			cursize = os.path.getsize(logfile)
		except OSError as e:
			logging.warning(e)
			continue
		if cursize == filesize:	# no changes in the log file
			continue
		else:
			filesize = cursize
		logging.debug("real number of lines" + str(subprocess.check_output("cat " + logfile + " | wc -l", shell=True)))
		with open(logfile, 'r') as f:
			for i in xrange(line_number):
				try:
					f.next()
				except Exception as e:
					logging.error(str(e) + "line_number: " +str(line_number))

			for line in f:
				line_number += 1
				logging.debug("line number: " + str(line_number))
				logging.debug("real number of lines" + str(subprocess.check_output("cat " + logfile + " | wc -l", shell=True)))
				line = line.replace('\n','')
				# only work for image-classification example
				epoch_index = line.find('Epoch')
				if epoch_index > -1:
					epoch = int(line[line.find("[", epoch_index) + 1 : line.find("]", epoch_index)])

					# batch
					batch_index = line.find('Batch')
					if batch_index > -1:
						batch = int(line[line.find("[", batch_index) + 1 : line.find("]", batch_index)])
					else:
						batch = -1 # the end of this epoch
					# train-acc
					train_acc_index = line.find('Train-accuracy')
					if train_acc_index > -1:
						train_acc.append((epoch, float(line[(line.find('=')+1):])))

					train_loss_index = line.find('Train-cross-entropy')
					if train_loss_index > -1:
						train_loss.append((epoch, float(line[(line.find('=')+1):])))

					val_acc_index = line.find('Validation-accuracy')
					if val_acc_index > -1:
						val_acc.append((epoch, float(line[(line.find('=')+1):])))

					val_loss_index = line.find('Validation-cross-entropy')
					if val_loss_index > -1:
						val_loss.append((epoch, float(line[(line.find('=')+1):])))

					time_cost_index = line.find('Time-cost')
					if time_cost_index > -1:
						time_cost.append((epoch, float(line[(line.find('=')+1):].split(' ')[0])))

		stat_dict['progress'] = (epoch, batch)
		stat_dict['train-acc'] = train_acc
		stat_dict['train-loss'] = train_loss
		stat_dict['val-acc'] = val_acc
		stat_dict['val-loss'] = val_loss
		if len(time_cost) > 0:
			tot_time_cost = 0
			for (epoch, cost) in time_cost:
				tot_time_cost += cost
			stat_dict['time-cost'] = tot_time_cost/len(time_cost)
		else:
			stat_dict['time-cost'] = 0

		if disp_interval == 30:
			logging.info('Progress: Epoch: ' + str(epoch) + ', Batch: ' + str(batch) + \
		             ', Train-accuracy: ' + str(train_acc) + ', Train-loss: ' + str(train_loss) + \
		             ', Validation-accuracy: ' + str(val_acc) + ', Validation-loss: ' + str(val_loss) + \
		             ', Time-cost: ' + str(time_cost))
			disp_interval = 0
		
		with open(recordfile, 'w') as fh:
			fh.write(str(stat_dict) + '\n')
			fh.flush()


def main():
	logfile = WORK_DIR + 'training.log'
	recordfile =  WORK_DIR + 'progress.txt'
	if ROLE == 'worker':
		update_progress(logfile, recordfile)
	
	
	
if __name__ == '__main__':
	if len(sys.argv) != 1:
		print "Description: monitor training progress in k8s cluster"
		print "Usage: python progress-monitor.py"
		sys.exit(1)
	main()
