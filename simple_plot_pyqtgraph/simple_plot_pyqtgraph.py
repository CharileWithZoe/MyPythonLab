# -*- coding: utf-8 -*-
import datetime
print("1 ", datetime.datetime.now())
import sys
import pyqtgraph as pg
print("2 ", datetime.datetime.now())
import time
import json
import argparse
print("3 ", datetime.datetime.now())

## Force use of a specific graphics system
use_gs = 'default'
for gs in ['raster', 'native', 'opengl']:
    if gs in sys.argv:
        use_gs = gs
        pg.Qt.QtGui.QApplication.setGraphicsSystem(gs)
        break

try:
    import faulthandler

    faulthandler.enable()
except ImportError:
    pass

print("4 ", datetime.datetime.now())
# pg.setConfigOption('background', 'w')
# pg.setConfigOption('foreground', 'k')


class DateAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strns = []
        rng = max(values) - min(values)

        string = '%m/%d %H:%M'
        for x in values:
            try:
                strns.append(time.strftime(string, time.localtime(x)))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        return strns


class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        print("CustomViewBox1 ", datetime.datetime.now())
        pg.ViewBox.__init__(self, *args, **kwds)
        print("CustomViewBox2 ", datetime.datetime.now())
        self.setMouseMode(self.RectMode)
        print("CustomViewBox3 ", datetime.datetime.now())

    ## reimplement right-click to zoom out
    def mouseClickEvent(self, ev):
        if ev.button() == pg.Qt.QtCore.Qt.RightButton:
            self.autoRange()

    def mouseDragEvent(self, ev):
        if ev.button() == pg.Qt.QtCore.Qt.RightButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev)


def read_json_file(filename):
    data = {}
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    return data

file = None
print("5 ", datetime.datetime.now())
parser = argparse.ArgumentParser(description="Matplotlib with jsonfile")
# action: means when the arg is set, the value set to True. eg args.verbose=True
parser.add_argument('--verbose', '-v', action='store_true', help='verbose mode')
parser.add_argument('--file', '-f',
                    help='The json file to plot')

args = parser.parse_args()

if args.verbose is not None:
    print("args.verbose : %s" % args.verbose)
if args.file is not None:
    print("args.file : %s" % args.file)

if file is None:
    file = 'memory.json'
print("5.1 ", datetime.datetime.now())
data = read_json_file(file)
if len(data) >= 2 and data[0].get("type") == "json-config" and data[0].get("style") == "time-series":
    data = data[1:-1]
print("5.2 ", datetime.datetime.now())
# -1 means need init
X_MIN = -1
X_MAX = -1
Y_MIN = -1
Y_MAX = -1

app = pg.mkQApp()
print("5.3 ", datetime.datetime.now())
axis = DateAxis(orientation='bottom')
print("5.3.1 ", datetime.datetime.now())
vb = CustomViewBox()
print("5.3.2 ", datetime.datetime.now())
pw = pg.PlotWidget(viewBox=vb, axisItems={'bottom': axis},
                   enableMenu=False, title="MyPlot with pyqtgraph")
print("5.4 ", datetime.datetime.now())
pw.setWindowTitle('pyqtgraph')
pw.showGrid(x=True, y=True, alpha=0.5)
pw.addLegend()

label = pg.TextItem(text="Info:", color='r', anchor=(0.0, 1.0))
pw.addItem(label)
vLine = pg.InfiniteLine(angle=90, movable=False, )
hLine = pg.InfiniteLine(angle=0, movable=False, )
pw.addItem(vLine, ignoreBounds=True)
pw.addItem(hLine, ignoreBounds=True)
print("5.5 ", datetime.datetime.now())

def adjustPos(x, y):
    newx = x
    newy = y
    if x < X_MIN:
        newx = X_MIN
    if x > X_MAX:
        newx = X_MAX
    if y < Y_MIN:
        newy = Y_MIN
    if y > Y_MAX:
        newy = Y_MAX

    return newx, newy


def mouseMoved(evt):
    pos = evt[0]  ## using signal proxy turns original arguments into a tuple
    if pw.sceneBoundingRect().contains(pos):
        mousePoint = vb.mapSceneToView(pos)
        pos_x = int(mousePoint.x())
        pos_y = int(mousePoint.y())
        # print(pos_x, pos_y, x_min, x_max)
        time_struct = time.localtime(pos_x)
        timeStr = time.strftime("%Y/%m/%d %H:%M:%S", time_struct)
        label.setHtml("<p style='color:white'>x：{0}</p><p style='color:white'>y：{1}</p>".format(timeStr, pos_y))
        pos_x, pos_y = adjustPos(pos_x, pos_y)
        label.setPos(pos_x, pos_y)
        vLine.setPos(mousePoint.x())
        hLine.setPos(mousePoint.y())

print("5.6 ", datetime.datetime.now())
proxy = pg.SignalProxy(pw.scene().sigMouseMoved, rateLimit=30, slot=mouseMoved)

pens = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
for i in range(0, len(data)):
    print("for1 ", i, datetime.datetime.now())
    xs = []
    for d in data[i]['x']:
        d = "2018-" + d[0:-4]
        t = time.strptime(d, '%Y-%m-%d %H:%M:%S')
        xs.append(time.mktime(t))

    xmin = min(xs)
    xmax = max(xs)
    if xmin < X_MIN or X_MIN == -1:
        X_MIN = xmin
        print("X_MIN change to ", X_MIN)
    if xmax > X_MAX or X_MAX == -1:
        X_MAX = xmax
        print("X_MAX change to ", X_MAX)
    # print(xs)

    ys = []
    for dd in data[i]['y']:
        dd = dd[0:-1]
        temp = int(dd)
        ys.append(temp)

    ymax = max(ys)
    ymin = min(ys)
    if ymin < Y_MIN or Y_MIN == -1:
        Y_MIN = ymin
        print("Y_MIN change to ", Y_MIN)
    if ymax > Y_MAX or Y_MAX == -1:
        Y_MAX = ymax
        print("Y_MAX change to ", Y_MAX)
    print("for2 ", i, datetime.datetime.now())
    # print(ys)
    # c1 = plt.plot([1,3,2,4], pen='r', symbol='o', symbolPen='r', symbolBrush=0.5, name='red plot')
    pw.plot(x=xs, y=ys, pen=pens[i], name=data[i]['name'])
    pw.show()
    print("for3 ", i, datetime.datetime.now())

pw.setXRange(X_MIN - (X_MAX - X_MIN) / 10, X_MAX + (X_MAX - X_MIN) / 10, padding=0)
pw.setYRange(Y_MIN - (Y_MAX - Y_MIN) / 10, Y_MAX + (Y_MAX - Y_MIN) / 10, padding=0)
print("6 ", datetime.datetime.now())

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    print("7 ", datetime.datetime.now())
    pg.Qt.QtGui.QApplication.instance().exec_()
    print("8 ", datetime.datetime.now())
