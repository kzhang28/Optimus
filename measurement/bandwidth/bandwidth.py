import sys
import os
import time
import requests
import socket
import operator
import logging
import threading
import subprocess

logging.basicConfig(level=logging.INFO,	format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

HOST_NAME = os.getenv("HOSTNAME") # exported by k8s
POD_IP = socket.gethostbyname(HOST_NAME)

APISERVER = "http://10.28.1.1:8080"	
API = "/api/v1/namespaces/"
NAMESPACE = "default"
DAEMON_SELECTOR = "labelSelector=app="
DAEMON_NAME = os.getenv("DAEMON_NAME")	# export via env


'''
Get all pods of this job
'''
def get_podlist():
	global DAEMON_NAME
	
	pod = API + NAMESPACE + "/pods?"
	if len(DAEMON_NAME) == 0:
		DAEMON_NAME = "pinger"
	url = APISERVER + pod + DAEMON_SELECTOR + DAEMON_NAME
	logging.debug(url)
	token_path = '/var/run/secrets/kubernetes.io/serviceaccount/token'
	
	if os.path.isfile(token_path):
		token = open(token_path, 'r').read()
		bearer = "Bearer " + token
		headers = {"Authorization": bearer}
		return requests.get(url, headers=headers, verify=False).json()
	else:
		return requests.get(url,verify=False).json()
	

'''
check whether all pods are running
'''
def is_all_running(podlist):
	require = len(podlist["items"])
	running = 0
	for pod in podlist["items"]:
		if pod["status"]["phase"] == "Running":
			running += 1
	logging.info("waiting for pods running, require:" + str(require) + ", running:" + str(running))
	if require == running:
		return True
	else:
		return False

		
'''
get map: [(pod ip, node ip), ...]
'''
def get_map(podlist):
	map = {}
	for pod in podlist["items"]:
		podIP = pod["status"]["podIP"]
		nodeIP = pod["status"]["hostIP"]
		map[podIP] = nodeIP
	sorted_map = sorted(map.items(), key=operator.itemgetter(1))	
	return sorted_map


'''
get self node IP
'''
def get_self_nodeIP(sorted_map):
	for (podIP, nodeIP) in sorted_map:
		if str(podIP) == str(POD_IP):
			return nodeIP
	
	
	
	
def main():
	logging.info("starting bandwidth measurer ...")
	
	# start iperf -s 
	iperf_server = threading.Thread(target=(lambda: subprocess.check_output('iperf -s', shell=True)), args=())
	iperf_server.start()
	
	# check pod status
	podlist = get_podlist()
	while not is_all_running(podlist):
		time.sleep(3)
		podlist = get_podlist() 
	sorted_map = get_map(podlist)
	
	logging.info(str(sorted_map))
	
	self_nodeIP = get_self_nodeIP(sorted_map)
	
	self_id = sorted_map.index((POD_IP,self_nodeIP))
	assert self_id > -1
	time.sleep(self_id*120)
	for (podIP, nodeIP) in sorted_map:
		if podIP == POD_IP:	# skip measure self
			continue
		response = subprocess.check_output("iperf -c " + podIP + " | grep 'Gbits/sec'", shell=True)
		logging.info(str(self_nodeIP) + "(" + str(POD_IP) + ")" + " --->>> " + str(nodeIP) + "(" + str(podIP) + ")" + ": \n" + response)
	logging.info("\n")
		



if __name__ == '__main__':
	if len(sys.argv) != 1:
		print "Description: bandwidth measurement script in k8s cluster"
		print "Usage: python bandwidth.py"
		sys.exit(1)
	main()
