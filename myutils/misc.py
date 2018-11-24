#-*-coding:utf-8-*-
import sys
import os
import subprocess
import re

def read_file(filename):
    if not os.path.isfile(filename):
        return []
    with open(filename, "r") as f:
        return f.readlines()
    return []


def write_file(filename, lines):
    with open(filename, "w+") as f:
        for l in lines:
            f.write(l)

def info(string):
    sys.stdout.write("%s\n" % string)

def is_substring(str1, str2):
    if str1.find(str2) >= 0:
        return True;
    else:
        return False;

def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            info('Subprogram output: [{}]'.format(line))
    if p.returncode == 0:
        info(cmd + 'subprocess run success')
        return True
    else:
        info(cmd + 'subprocess run fail')
        return False


def connectDevcie():
    '''check the adb connect or not'''
    try:
        #get the device list, and split with \r\n
        deviceInfo = subprocess.check_output('adb devices').split("\r\n")
        # If the second element is '', it means not connect
        if deviceInfo[1] == '':
            return False
        else:
            return True
    except Exception as e:
        info("Device Connect Fail:" + e)


def getAndroidVersion():
    try:
        if connectDevcie():
            sysInfo = subprocess.check_output('adb shell cat /system/build.prop')
            androidVersion = re.findall("version.release=(\d\.\d)*", sysInfo, re.S)[0]
            return androidVersion
        else:
            return "Connect Fail, Please reconnect Device..."
    except Exception as e:
        info("getAndroidVersion() error " + e)

def getDeviceName():
    try:
        if connectDevcie():
            deviceInfo = subprocess.check_output('adb devices -l')
            deviceName = re.findall(r'device product:(.*)\smodel', deviceInfo, re.S)[0]
            return deviceName
        else:
            return "Connect Fail, Please reconnect Device..."
    except Exception as e:
        info("getDeviceName() error " + e)
