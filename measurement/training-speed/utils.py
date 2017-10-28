import logging

# create logger
def getLogger(name='logger'):
	global logger
	
	logger = logging.getLogger(name) 
	logger.setLevel(logging.INFO)
	
	fh = logging.FileHandler(name + '.log') 
	fh.setLevel(logging.INFO) 

	ch = logging.StreamHandler() 
	ch.setLevel(logging.INFO) 
	
	formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s') 
	fh.setFormatter(formatter) 
	ch.setFormatter(formatter) 
	
	logger.addHandler(fh)
	logger.addHandler(ch)
	
	return logger