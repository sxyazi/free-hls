import os

def exec(cmd):
	return os.popen(cmd).read().strip()
