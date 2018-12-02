import sys
sys.path.append('..')
from mylog import *
from adb import ADB

# C:\Users\Administrator\Downloads\ico1106\core\cpuset>python Main.py --help
# usage: Main.py [-h] [--verbose] [--config CONFIG] [--online ONLINE]
#
# Used to set cpu online/offline, set the freq limit of the cores
#
# optional arguments:
#   -h, --help            show this help message and exit
#   --verbose, -v         verbose mode
#   --config CONFIG, -c CONFIG
#                         the cpu config which input to the script, the format
#                         is core online/offline min_freq/max_freq
#   --online ONLINE, -o ONLINE
#                         input the list of cpus that need online, format is
#                         "0_1_2_3_4"
#
# python Main.py --config="0_1_1000000_1200000 2_1_1000000_1800000"
# python Main.py --online="0_1_2_3"

adb = ADB("adb")
log = mylog(level="info")


def get_package_info(adb):
    apps = adb.shell_command("pm list packages")
    for app in apps:
        path = adb.shell_command("pm path {}".format(app.split(':')[1]))
        print ("{}: {}".format(app,path))


def cpu_get_max_cpu_cores():
    cores = adb.shell_command("cat /sys/devices/system/cpu/kernel_max")
    return int(cores[0])


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


def cpu_set_config(configs):
    for config in configs:
        cpu = config[0]
        online = config[1]
        min = config[2]
        max = config[3]
        cpu_hotplug(cpu, online)
        cpu_set_freq_limit(cpu, min, max)


def cpu_set_online(online_cpus):
    cores = cpu_get_max_cpu_cores()
    for i in range(0, cores+1):
        if i in online_cpus:
            cpu_hotplug(i, 1)
        else:
            cpu_hotplug(i, 0)


# core online/offline min_freq/max_freq
# 0_1_0_0 4_1_1000000_1500000
def parse_config_args(s):
    log.d("parse_config_args(), args=%s" % s)
    ret = []
    v = s.split(" ")
    for v1 in v:
        temp_val = v1.split('_')
        if len(temp_val) != 4:
            log.e("cpuset config paramters %s != 4" % v1)
            exit(-1)
        l = []

        for v2 in temp_val:
            l.append(int(v2))

        ret.append(l)
    return ret


# core online/offline min_freq/max_freq
# 0_1_2_3
def parse_onine_args(s):
    ret = []
    v = s.split("_")
    for v1 in v:
        ret.append(int(v1))

    return ret


def test():
    cpu_hotplug(7, 1)
    cpu_hotplug(6, 1)
    cpu_hotplug(5, 1)
    cpu_hotplug(4, 1)
    cpu_hotplug(3, 1)
    cpu_hotplug(2, 1)
    cpu_hotplug(1, 1)
    cpu_hotplug(0, 1)
    cpu_set_freq_limit(4, 800000, 800000)
    cpu_set_freq_limit(0, 2000000, 2000000)


def main():
    import argparse

    # description: descript the usage of the script
    parser = argparse.ArgumentParser(description="Used to set cpu online/offline, set the freq limit of the cores")
    # action: means when the arg is set, the value set to True. eg args.verbose=True
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose mode')
    parser.add_argument('--config', '-c', type=parse_config_args,
                        help='the cpu config which input to the script, the format is core online/offline min_freq/max_freq')
    parser.add_argument('--online', '-o', type=parse_onine_args,
                        help='input the list of cpus that need online, format is \"0_1_2_3_4\"')

    args = parser.parse_args()
    if args.verbose:
        log.i("Verbose mode on!")
    else:
        log.i("Verbose mode off!")

    log.i("waiting for adb connect...")
    adb.wait_for_device()
    log.i("adb is ready!")

    if args.config is not None:
        log.i("args.config : %s" % args.config)
        cpu_set_config(args.config)
    if args.online is not None:
        log.i("args.online : %s" % args.online)
        cpu_set_online(args.online)


if __name__ == "__main__":
    main()

