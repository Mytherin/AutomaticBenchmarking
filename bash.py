
import os

def system(logfile, syscall):
	logfile.write(syscall + '\n')
	logfile.flush()
	return os.system(syscall)