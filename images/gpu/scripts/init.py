import threading
import logging
import os
import os.path
import sys
import time


logging.basicConfig(level=logging.INFO,	format='%(asctime)s.%(msecs)03d %(module)s %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")


def main():
	logging.info("start init process ...")
	
	logging.info("start training thread ...")
	train = threading.Thread(target=(lambda: os.system("python /start.py")), args=())
	train.setDaemon(True)
	train.start()
	
	logging.info("start speed monitor thread ...")
	speed_monitor = threading.Thread(target=(lambda: os.system("python /speed-monitor.py")), args=())
	speed_monitor.setDaemon(True)
	speed_monitor.start()

	logging.info("start progress monitor thread ...")
	progress_monitor = threading.Thread(target=(lambda: os.system("python /progress-monitor.py")), args=())
	progress_monitor.setDaemon(True)
	progress_monitor.start()

	while True:
		time.sleep(60)


if __name__ == '__main__':
	if len(sys.argv) != 1:
		print "Description: MXNet init script in k8s cluster"
		print "Usage: python init.py"
		sys.exit(1)
	main()