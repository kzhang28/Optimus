import os
import logging
import time
import subprocess
import sys


logging.basicConfig(level=logging.INFO,	format='%(asctime)s.%(msecs)03d %(module)s %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
ROLE = os.getenv("ROLE")

# read the log file and monitor the training progress
# give log file name
# give record file name
# run the function in a separate thread
def update_speed(logfile, recordfile):
	filesize = 0
	line_number = 0
	
	# logfile = 'training.log'
	# recordfile = 'speed.txt'	# change to the correct path ....../data/mxnet-data/......
	
	with open(recordfile, 'w') as fh:
		fh.write('0 0\n')
	logging.info('starting speed monitor to track average training speed ...')

	speed_list = []
	while True:
		time.sleep(5)
		
		try:
			cursize = os.path.getsize(logfile)
		except OSError as e:
			logging.warning(e)
			continue
		if cursize == filesize:	# no changes in the log file
			continue
		else:
			filesize = cursize
		
		# Epoch[0] Time cost=50.885
		# Epoch[1] Batch [70]	Speed: 1.08 samples/sec	accuracy=0.000000
		with open(logfile, 'r') as f:
			for i in xrange(line_number):
				f.next()
			for line in f:
				line_number += 1
				
				start = line.find('Speed')
				end = line.find('samples')	
				if start > -1 and end > -1 and end > start:
					string = line[start:end].split(' ')[1]
					try:
						speed = float(string)
						speed_list.append(speed)
					except ValueError as e:
						logging.warning(e)
						break
		
		if len(speed_list) == 0:
			continue
			
		avg_speed = sum(speed_list)/len(speed_list)
		logging.info('Average Training Speed: ' + str(avg_speed))
		
		stb_speed = 0
		if len(speed_list) <= 5:
			stb_speed = avg_speed
		else:
			stb_speed = sum(speed_list[5:])/len(speed_list[5:])
			
		logging.info('Stable Training Speed: ' + str(stb_speed))
		
		with open(recordfile, 'w') as fh:
			fh.write(str(avg_speed) + ' ' + str(stb_speed) + '\n')
	
	

def main():
	logfile = '/training.log'
	recordfile =  '/mxnet/example/image-classification/data/' + 'speed.txt'
	if ROLE == 'worker':
		update_speed(logfile, recordfile)
	
	
	
if __name__ == '__main__':
	if len(sys.argv) != 1:
		print "Description: monitor training progress in k8s cluster"
		print "Usage: python update_progress.py"
		sys.exit(1)
	main()
