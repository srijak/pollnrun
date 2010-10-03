# Simple script to poll all files of interest below the current working directory
# for changes. On change, it will run w/e commands you want. For me, it has
# been helpful in restarting tornado web nodes.
import os
import re
import time
import signal
from subprocess import Popen
 
# define what you want to run here:
# each task is a list of command/arguments to run, popen style
tasks = [['python','httpDatabase.py'],['python','main.py']]
 
# define the file types you want to trigger on
# I opted for .py and html files.
file_regexp = re.compile("(.py$|.html$)")
 
def files_have_changed(old_stats, new_stats):
    if len(old_stats) != len(new_stats):
        return True
    for k in old_stats:
        if new_stats[k] != old_stats[k]:
            return True
    return False
 
def get_stats():
    stats = {}
    f = []
    for root, folders, files in os.walk(os.getcwd()):
        f.extend([os.path.join(root,x) for x in files if file_regexp.search(x)])
    for file in f:
        try:
            stats[file] = time.localtime(os.stat(file)[8])
        except:
            pass
    return stats
 
 
handles = []
def stop_current():
    if len(handles) > 0:
        for h in handles:
            print "Killing %d" % (h.pid)
            os.kill(h.pid, signal.SIGTERM)
        del handles[:]
 
def restart():
    print "Files changed. Restarting"
    stop_current()
    for t in tasks:
        p = Popen(t)
        print "Started %s. PID:%d" % (" ".join(t),p.pid)
 
        handles.append(p)
 
 
last_stats = {} 
while 1:
    current_stats = get_stats()
 
    if (files_have_changed(last_stats, current_stats)):
        last_stats = current_stats
        restart()
    time.sleep(1)
