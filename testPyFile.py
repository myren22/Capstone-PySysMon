# print('hello kyle from git')

# #####
# import subprocess
#
# command = ['ls', '-l']
#
# p=subprocess.Popen(command, stdout=subprocess.PIPE)
#
# text = p.stdout.read()
# print(text)
# retcode = p.wait()
# #####

#####
# import subprocess
#
# command = ['top', 'ls']
#
# p=subprocess.Popen(command, stdout=subprocess.PIPE, st)
#
# text = p.stdout.read()
# # print(text)
# retcode = p.wait()
# print(text)
# #####
#
#!/usr/bin/env python
##############
# """Start process; wait 2 seconds; kill the process; print all process output."""
# import subprocess
# import tempfile
# import time
#
# def main():
#     # open temporary file (it automatically deleted when it is closed)
#     #  `Popen` requires `f.fileno()` so `SpooledTemporaryFile` adds nothing here
#     f = tempfile.TemporaryFile()
#
#     # start process, redirect stdout
#     p = subprocess.Popen(["top"], stdout=f)
#
#     # wait 2 seconds
#     time.sleep(2)
#
#     # kill process
#     #NOTE: if it doesn't kill the process then `p.wait()` blocks forever
#     p.terminate()
#     p.wait() # wait for the process to terminate otherwise the output is garbled
#
#     # print saved output
#     f.seek(0) # rewind to the beginning of the file
#     print (f.read()),
#     f.close()
#
# if __name__=="__main__":
#     main()

########
##this works and gives a list of all pids that is also stored in a dict
# from subprocess import Popen, PIPE
#
# process = Popen(['ps', '-eo' ,'pid,args'], stdout=PIPE, stderr=PIPE)
# stdout, notused = process.communicate()
# print(stdout)
# pidDict = {}
# for line in stdout.splitlines():
#
#     strLine = line.decode('utf-8')
#     strLine = strLine.lstrip(' ')
#     pid, cmdline = strLine.split(' ', 1)
#     print('')
#     print('pid:'+pid+', cmdline:'+cmdline)
#     pidDict[pid]=cmdline
# print('done')
# print('')
########
from subprocess import Popen, PIPE
import psutil
# 'ps', '-eo' ,'pid,args'
process = Popen(['top'], stdout=PIPE, stderr=PIPE)
stdout, notused = process.communicate()
print(stdout)
pidDict = {}
for line in stdout.splitlines():

    strLine = line.decode('utf-8')
    strLine = strLine.lstrip(' ')
    pid, cmdline = strLine.split(' ', 1)
    print('')
    print('pid:'+pid+', cmdline:'+cmdline)
    pidDict[pid]=cmdline
print('done')
print('')
###########

