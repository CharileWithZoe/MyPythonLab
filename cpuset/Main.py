import sys
sys.path.append('..')
from myutils.mylog import mylog
from myutils.adb import ADB

adb = ADB("adb")
log = mylog(level="info")

def get_package_info(adb):
    apps = adb.shell_command("pm list packages")
    for app in apps:
        path = adb.shell_command("pm path {}".format(app.split(':')[1]))
        print ("{}: {}".format(app,path))

"""
/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq
/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq
/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq
/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies
/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors
/sys/devices/system/cpu/cpu0/cpufreq/scaling_boost_frequencies
/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
/sys/devices/system/cpu/cpu0/cpufreq/scaling_driver
/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq
/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq
/sys/devices/system/cpu/cpu0/cpufreq/scaling_setspeed
/sys/devices/system/cpu/cpu0/cpufreq/schedutil
/sys/devices/system/cpu/cpu0/cpufreq/stats
"""

def cpu_get_freq_limit(cpu):
    min = adb.shell_command("cat /sys/devices/system/cpu/cpu%d/cpufreq/scaling_min_freq" % cpu)
    max = adb.shell_command("cat /sys/devices/system/cpu/cpu%d/cpufreq/scaling_max_freq" % cpu)

    min = int(min[0])
    max = int(max[0])
    #log.i("cpu_get_freq_limit(), min/max = %d/%d" % (min, max))

    return min, max

def cpu_get_available(cpu):
    l = []
    available = adb.shell_command("cat /sys/devices/system/cpu/cpu%d/cpufreq/scaling_available_frequencies" % cpu)

    available = available[0].split(' ')
    for val in available:
        l.append(int(val))
    return l

def adjust_freq_limit(ava_list, val):
    if val > ava_list[-1]:
        return ava_list[-1]
    elif val < ava_list[0]:
        return ava_list[0]

    for i in range(0, len(ava_list)):
        if ava_list[i] == val:
            return val
        elif ava_list[i] > val:
            return ava_list[i-1]

def cpu_set_freq_limit(cpu, min_in, max_in):
    ava = cpu_get_available(cpu)
    min = adjust_freq_limit(ava, min_in)
    max = adjust_freq_limit(ava, max_in)

    log.i("cpu_set_freq_limit(%d) ajust values (%d/%d) -> (%d/%d)" % (cpu, min_in, max_in, min, max))
    if min > max:
        log.i("wrong parameters, min(%d) < max(%d)" % (min, max))
        return

    cur_min, cur_max = cpu_get_freq_limit(cpu)
    """
    type 1:
        # current              |_________|
        # wanted     |*****|
        # set min first
    type 2:
        # current              |_________|
        # wanted            |*****|
        # No need take care of the order
    type 3:
        # current              |_________|
        # wanted                 |*****|
        # No need take care of the order
    type 4:
        # current              |_________|
        # wanted                 |**********|
        # No need take care of the order
    type 5:
        # current              |_________|
        # wanted                           |*******|
        # Set Max first    
    type 6:
        # current              |_________|
        # wanted            |**************|
        # No need take care of the order
    """

    if max <= cur_min:
        # current              |_________|
        # wanted     |*****|
        # set min first
        adb.shell_command("echo %d > /sys/devices/system/cpu/cpu%d/cpufreq/scaling_min_freq" % (min, cpu))
        adb.shell_command("echo %d > /sys/devices/system/cpu/cpu%d/cpufreq/scaling_max_freq" % (max, cpu))
    elif min >= cur_max:
        # current              |_________|
        # wanted                           |*******|
        # Set Max first
        adb.shell_command("echo %d > /sys/devices/system/cpu/cpu%d/cpufreq/scaling_max_freq" % (max, cpu))
        adb.shell_command("echo %d > /sys/devices/system/cpu/cpu%d/cpufreq/scaling_min_freq" % (min, cpu))
    else:
        # No need take care about the range
        adb.shell_command("echo %d > /sys/devices/system/cpu/cpu%d/cpufreq/scaling_min_freq" % (min, cpu))
        adb.shell_command("echo %d > /sys/devices/system/cpu/cpu%d/cpufreq/scaling_max_freq" % (max, cpu))

    cur_min, cur_max = cpu_get_freq_limit(cpu)
    log.i("cpu_set_freq_limit(%d) cur_min/wanted_min=(%d/%d) cur_max/wanted_max=(%d/%d)" % (cpu, cur_min, min, cur_max, max))

def cpu_hotplug(cpu, online):
    if online is 1:
        log.i("set cpu%d to Online" % cpu)
    elif online is 0:
        log.i("set cpu%d to Offline" % cpu)
    else:
        log.i("wrong parameters, need 0 or 1, but the value is %d" % online)
    adb.shell_command("echo %d > /sys/devices/system/cpu/cpu%d/online" % (online, cpu))

def main():
    log = mylog(level="info")
    # creates the ADB object
    adb.wait_for_device()
    log.i("adb is ready!")

    cpu_hotplug(7,0)
    cpu_hotplug(6,0)
    cpu_hotplug(5,0)
    cpu_hotplug(3,0)
    cpu_hotplug(2,0)
    cpu_hotplug(1,0)
    cpu_set_freq_limit(4, 800000, 800000)
    cpu_set_freq_limit(0, 2000000, 2000000)

if __name__ == "__main__":
    main()