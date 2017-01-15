#!log.py

from datetime import datetime
from subprocess import call

def log(msg):
    timedMsg = "<" + str(datetime.now()) + ">"+ msg
    open("debug.log", "a").write(timedMsg+"\n")
    print(timedMsg)  # To stdout

def fault(msg):
    timedMsg = "<" + str(datetime.now()) + ">"+ msg
    open("fault.log", "a").write(timedMsg+"\n")
    print("FAULT! "+ msg)  # To stdout

def NewLog():
    call("rm old_debug.log", shell=True) # Remove yesterday's old log
    call("mv debug.log old_debug.log", shell=True) # Move today's log to yesterday's, getting ready to start new log from now

