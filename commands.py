#!commands.py

# Command Line Interpreter module for Vesta

# Standard Python modules
import cmd
import readline
import os
import sys
import select
import socket
from pathlib import Path
from pprint import pprint # Pretty print for devs list
from datetime import datetime
from datetime import timedelta
from subprocess import call
# App-specific Python modules
import devices
import devcmds
import queue
import events
import telegesis
import variables
import rules
import vesta
import log
import iottime
import database
import synopsis
import heating
import schedule
import report

sck = ""
cliSck = ""
sckLst = []

def EventHandler(eventId, eventArg):
    global sckLst, sck, cliSck
    if eventId == events.ids.INIT:
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create socket
        sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sck.setblocking(0) # accept() is no longer blocking
        port = 12345
        try:
            sck.bind(('', port))    # Listen on all available interfaces
        except OSError as err: # "OSError: [Errno 98] Address already in use"
            database.NewEvent(0, "Socket bind failed with " + err.args[1]) # 0 is always hub
            vesta.Reboot()
        sck.listen(0)
        sckLst = [sck]
    if eventId == events.ids.SECONDS:
        if select.select([sys.stdin], [], [], 0)[0]:    # Read from stdin (for working with the console)
            cmd = sys.stdin.readline()
            if cmd:
                Commands().onecmd(cmd)
        rd, wr, er = select.select(sckLst, [], [], 0)   # Read from remote socket (for working with web pages)
        for s in rd:
            if s is sck:
                cliSck, addr = sck.accept()
                sckLst.append(cliSck)
                #log.debug("New connection from client")
            else:
                try:
                    cmd = cliSck.recv(100)
                except OSError as err:  # OSError: [Errno 9] Bad file descriptor"
                    synopsis.problem("Socket Client command failed with ", err.args[1])
                    cmd = ""    # No command if there was a failure
                if cmd:
                    cmd = cmd.decode()
                    log.debug("Got cmd \""+ cmd+"\" from web page")
                    sys.stdout = open("cmdoutput.txt", "w") # Redirect stdout to file
                    Commands().onecmd(cmd)
                    sys.stdout = sys.__stdout__ # Put stdout back to normal (will hopefully also close the file)
                    f = open("cmdoutput.txt", "r")
                    cmdOut = f.read()
                    cliSck.send(str.encode(cmdOut))
                    call("rm cmdoutput.txt", shell=True) # Remove cmd output after we've used it
                #else:
                    #log.debug("Closing socket")
                    #cliSck.close() # Can't do this, since server can't close the socket
                    #if cliSck in sckLst:
                    #    sckLst.remove(cliSck)
    # End of Command EventHandler

class Commands(cmd.Cmd):
    def do_info(self, line):
        """info
        Displays useful information"""
        events.Issue(events.ids.INFO)

    def do_restart(self, line):
        """restart
        Restarts program execution"""
        os.execl(sys.executable, sys.executable, *sys.argv)
        #sys.exit()

    def do_reqrpt(self, deviceId):
        """reqrpt deviceId
        Request report as dict with useful info for use with ESP32 display, etc.  Might also include device-specific command to eg dim the display"""
        dictText = report.MakeText(deviceId) # Keep time, etc. up to date
        if dictText:
            #log.debug("reqrpt sending:" + dictText) # Cannot have any debugging in commands, since the log gets sent back to client!
            print(dictText+"'\n") # Terminating \n looked by by ESP32 code to terminate the string

    def do_uptime(self, line):
        """uptime
        Shows time app has been running"""
        upTime = datetime.now() - iottime.appStartTime
        print("%d days, %.2d:%.2d" % (upTime.days, upTime.seconds//3600, (upTime.seconds//60)%60))  # Used by web page

    def do_version(self, line):
        """version
        Shows version of this app"""
        print("Vesta v" + vesta.GetVersion())

    def do_radio(self, item):
        """radio
        Shows info about the radio (channel, power, PAN id)"""
        events.Issue(events.ids.RADIO_INFO) # Used by web page for hub info

    def do_vars(self, item):
        """vars [item]
        Show all variables, or just variables that contain item"""
        if item == "":
            vars = variables.varList
            sortedVars = sorted(vars, key=lambda str: str[0].lower())  # Case-insensitive sorting
            pprint (sortedVars)
        else:
            itemisedList = []
            for v in variables.varList:
                if item.lower() in v[0].lower():
                    itemisedList.append(v)
            # end for loop
            try:
                pprint(sorted(itemisedList, key = lambda val: val[1]))
            except:
                pprint(itemisedList)    # If it's not sortable (mix of floats and strs), then just print it in any order

    def do_set(self, line):
        """set name value
        Set named variable to value"""
        if " " in line:
            argList = line.split(" ")
            name = argList[0]
            val = argList[1]
            variables.Set(name, val)
        else:
            variables.Del(line)

    def do_open(self, line):
        """open
        Opens network (for 60s) to allow new device to join"""
        queue.EnqueueCmd(0, ["AT+PJOIN", "OK"])

    def do_identify(self, line):
        """identify name seconds
        Sends identify command to named device.  Use 0 seconds to stop immediately"""
        argList = line.split()
        if len(argList) >= 2:
            devKey = devices.FindDev(argList[0])
            if devKey != None:
                timeS = int(argList[1])
                devcmds.Identify(devKey, timeS)
        else:
            log.fault("Insufficient Args")

    def do_toggle(self, devId):
        """toggle name
        Sends toggle on/off command to named device"""
        devKey = devices.FindDev(devId)
        if devKey != None:
            database.NewEvent(devKey, "Toggle", "UICmd")
            devcmds.Toggle(devKey)

    def do_on(self, devId):
        """on name
        Sends on command to named device"""
        devKey = devices.FindDev(devId)
        if devKey != None:
            database.NewEvent(devKey, "SwitchOn", "UICmd")
            devcmds.SwitchOn(devKey)

    def do_off(self, devId):
        """off name
        Sends off command to named device"""
        devKey = devices.FindDev(devId)
        if devKey != None:
            database.NewEvent(devKey, "SwitchOff", "UICmd")
            devcmds.SwitchOff(devKey)

    def do_dim(self, line):
        """dim name percentage
        Sends level command to named device"""
        argList = line.split()
        if len(argList) >= 2:
            percentage = int(argList[1])
            devKey = devices.FindDev(argList[0])
            if devKey != None:
                database.NewEvent(devKey, "Dim", "UICmd")
                devcmds.Dim(devKey, percentage)
        else:
            log.fault("Insufficient Args")

    def do_hue(self, line):
        """hue name hue
        Sends ColorCtrl command to named device, where 0<hue<360"""
        argList = line.split()
        if len(argList) >= 2:
            hue = int(argList[1])
            devKey = devices.FindDev(argList[0])
            if devKey != None:
                database.NewEvent(devKey, "Hue", "UICmd")
                devcmds.Hue(devKey, hue)
        else:
            log.fault("Insufficient Args")

    def do_sat(self, line):
        """sat name sat
        Sends ColorCtrl command to named device, where 0<sat<100"""
        argList = line.split()
        if len(argList) >= 2:
            sat = int(argList[1])
            devKey = devices.FindDev(argList[0])
            if devKey != None:
                database.NewEvent(devKey, "Sat", "UICmd")
                devcmds.Sat(devKey, sat)
        else:
            log.fault("Insufficient Args")

    def do_at(self, line):
        """at cmd
        Sends AT command to Telegesis stick"""
        queue.EnqueueCmd(0, ["AT"+line, "OK"])

    def do_devat(self, line):
        """devat name cmd
        Sends AT command to named device"""
        argList = line.split()
        if len(argList) >= 2:
            cmd = argList[1]
            devKey = devices.FindDev(argList[0])
            if devKey != None:
                queue.EnqueueCmd(devKey, ["AT"+cmd, "OK"])

    def do_getAttr(self, line):
        """getAttr name clstr attr
        Get attribute on cluster from named device"""
        argList = line.split()
        if len(argList) >= 3:
            devKey = devices.FindDev(argList[0])
            clstr = argList[1]
            attr = argList[2]
            if devKey != None:
                telegesis.TxReadDevAttr(devKey, clstr, attr) # WOrk out details and send command via queue

    def do_newSchedule(self, name):
        """newSchedule name
        Creates new schedule"""
        heating.NewSchedule(name)

    def do_delSchedule(self, name):
        """delSchedule name
        Deletes named schedule"""
        heating.DelSchedule(name)

    def do_getSchedule(self, devId):
        """getSchedule id
        Gets heating schedule from device"""
        devKey = devices.FindDev(devId)
        if devKey != None:
            heating.GetSchedule(devKey)

    def do_setSchedule(self, line):
        """setSchedule id name
        Sets schedule on device using name (eg Heating, etc.)"""
        argList = line.split()
        if len(argList) >= 2:
            devKey = devices.FindDev(argList[0])
            scheduleName = argList[1]
            if devKey != None:
                heating.SetSchedule(devKey, scheduleName)

    def do_setTargetTemp(self, line):
        """setTargetTemp id temp durationS
        Sets the target temperature on the thermostat device for durationS"""
        argList = line.split()
        if len(argList) >= 3:
            devKey = devices.FindDev(argList[0])
            temp = argList[1]
            timeoutS = argList[2]
            if devKey != None:
                schedule.Override(devKey, temp, timeoutS)

    def do_getTargetTemp(self, devId):
        """getTargetTemp id
        Gets the target temperature from a thermostat device"""
        devKey = devices.FindDev(devId)
        if devKey != None:
            heating.GetTargetTemp(devKey)

    def do_getSourceTemp(self, devId):
        """getSourceTemp id
        Gets the source temperature from a thermostat device"""
        devKey = devices.FindDev(devId)
        if devKey != None:
            heating.GetSourceTemp(devKey)

    def do_rptTemp(self, line): # NB As a version of SetSourceTemp
        """rptTemp id temp
        Reports the temperature to a device"""
        argList = line.split()
        if len(argList) >= 2:
            devKey = devices.FindDev(argList[0])
            temp = argList[1]
            if devKey != None:
                heating.RptTemp(devKey, temp)

    def do_getTime(self, devId):
        """getTime id
        Gets the time from the device using the time cluster"""
        devKey = devices.FindDev(devId)
        if devKey != None:
            iottime.GetTime(devKey)

    def do_removeDevice(self, devId):
        """removeDevice id
        Tells device to leave the network and remove it from the database"""
        devKey = devices.FindDev(devId)
        if devKey != None:
            devices.Remove(devKey)

    def do_rolllog(self, line):
        """rolllog
        Rolls the logs - automatically done at midnight"""
        log.RollLogs()

    def do_synopsis(self, line):
        """synopsis
        Constructs synopsis.html page"""
        synopsis.BuildPage()

    def do_config(self, line):
        """config devKey field
        Tells app to use new reporting configuration field from database"""
        argList = line.split()
        if len(argList) >= 2:
            confField = argList[1]
            devKey = argList[0]
            if devKey != None:
                devices.Config(devKey, confField)
        else:
            log.fault("Insufficient Args")

