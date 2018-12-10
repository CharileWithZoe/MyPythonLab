import datetime
print("1 ", datetime.datetime.now())
import os
import sys
from mylog import mylog
# import matplotlib
# This code need add before plt, to set the backend
# matplotlib.use('tkagg')
print("2 ", datetime.datetime.now())
# import matplotlib.dates as mdates
print("2.1 ", datetime.datetime.now())
import matplotlib.pyplot as plt
print("3 ", datetime.datetime.now())
import json
import argparse

sys.path.append('..')

log = mylog(level="error", filename=None)

def scan_json_files(path):
    log.i("scan_json_files(), path=%s" % path)
    jsfiles = []
    for rt, dirs, files in os.walk(path):
        for f in files:
            ff = os.path.join(rt,f)
            if ".json" == os.path.splitext(ff)[-1]:
                jsfiles.append(ff)
                log.i("json file: %s" % ff)
    return jsfiles


def write_json_file(filename, data):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def read_json_file(filename):
    data = {}
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    return data

def plot_in_subplot(data):
    plt.figure(1)
    num = len(data)
    for i in range(0, len(data)):
        plt.subplot(num, 1, i+1)
        plt.plot(data[i]['x'], data[i]['y'], label=data[i]['name'])
        plt.title(data[i]['name'])
        plt.grid(True)
    plt.show()


def plot_in_one_figure(data):
    plt.figure(2)
    plt.subplot(1, 1, 1)
    for i in range(0, len(data)):
        plt.plot(data[i]['x'], data[i]['y'], label = data[i]['name'])
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.show()


def plot_with_date(data):
    print("plot_with_date1 ", datetime.datetime.now())
    # plt.figure(3)
    print("plot_with_date2 ", datetime.datetime.now())
    plt.subplot(1, 1, 1)
    print("plot_with_date3 ", datetime.datetime.now())
    for i in range(0, len(data)):
        # "11-13 07:16:30.577",
        # datetime.strptime(s, '%m-%d %H:%M:%S').date()
        # xs = [datetime.strptime(d, '%m-%d %H:%M:%S').date() for d in data[i]['x']]
        xs = []
        for d in data[i]['x']:
            d = "2018-" + d[0:-4]
            temp = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
            xs.append(temp)
        # print(xs)
        ys = []
        for dd in data[i]['y']:
            dd = dd[0:-1]
            temp = int(dd)
            ys.append(temp)
        # print(ys)
        plt.plot(xs, ys, label = data[i]['name'])
    print("plot_with_date4 ", datetime.datetime.now())
    # config the x axis
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    # if set, only the major is show
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gcf().autofmt_xdate()  # auto spin the label
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.show()
    print("plot_with_date5 ", datetime.datetime.now())

def plot(jsonfile):
    data = read_json_file(jsonfile)
    if len(data) >= 2 and data[0].get("type") == "json-config" and data[0].get("style") == "time-series":
        plot_with_date(data[1:-1])
    else:
        plot_in_subplot(data)
        plot_in_one_figure(data)


def parse_config_args(s):
    log.d(s)
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


def main():
    print("4 ", datetime.datetime.now())
    # description:  the usage of the script
    parser = argparse.ArgumentParser(description="Matplotlib with jsonfile")
    # action: means when the arg is set, the value set to True. eg args.verbose=True
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose mode')
    parser.add_argument('--example', '-e', type=int,
                        help='Run MyPlot with the choosed example\n'
                             '\t1: testdata/memory.json\n'
                             '\t2: testdata/power_123.json\n')
    parser.add_argument('--file', '-f',
                        help='The json file to plot')
    parser.add_argument('--config', '-c', type=parse_config_args,
                        help='configs for MyPlot')

    args = parser.parse_args()

    if args.verbose is not None:
        log.i("args.verbose : %s" % args.verbose)
    if args.config is not None:
        log.i("args.config : %s" % args.config)
    if args.example is not None:
        log.i("args.example :  %d" % args.example)
    if args.file is not None:
        log.i("args.file : %s" % args.file)

    file = 'testdata\\memory.json'
    if args.example == 1:
        file = 'testdata\\memory.json'
    elif args.example == 2:
        file = 'testdata\\power_123.json'

    if args.file is not None:
        file = args.file
    print("5 ", datetime.datetime.now())
    plot(file)
    print("6 ", datetime.datetime.now())


if __name__ == '__main__':
    #import cProfile
    #cProfile.run('main()')
    log.i("Start")
    main()

