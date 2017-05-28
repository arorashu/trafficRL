from xml.etree import ElementTree as et
import os
import random
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient

client = MongoClient()
db = client['trafficLight']

def getDBName(options):
    asd

def updateVehDistribution():
    fileDir = os.path.dirname(os.path.realpath('__file__'))
    src = et.parse(os.path.join(fileDir, 'data/cross.src.xml'))
    dst = et.parse(os.path.join(fileDir, 'data/cross.dst.xml'))

    srcEdges = src.findall('*/edge')
    dstEdges = dst.findall('*/edge')

    # generate uniformly dstributed random numbers that sum to 1
    listRandSrc = [0, 1]
    listRandDst = [0, 1]
    for i in range(len(srcEdges)-1):
        listRandSrc.append(round(random.uniform(0, 1), 4))
        listRandDst.append(round(random.uniform(0, 1), 4))
    listRandSrc.sort()
    print(listRandDst)
    listRandDst.sort()

    for i, edge in enumerate(srcEdges):
        edge.set('value', str(listRandSrc[i+1] - listRandSrc[i]))

    for i, edge in enumerate(dstEdges):
        edge.set('value', str(listRandDst[i+1] - listRandDst[i]))

    src.write(os.path.join(fileDir, 'data/cross.src.xml'))
    dst.write(os.path.join(fileDir, 'data/cross.dst.xml'))

def plotGraph(xVar, yVar):
    hl.set_xdata(np.append(hl.get_xdata(), xVar))
    hl.set_ydata(np.append(hl.get_ydata(), yVar))
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    # plt.pause(0.0001)
    return

def savePlot(options):
    plt.savefig('outputs/foo.png')
    plt.savefig('outputs/foo.pdf')


if __name__ != "__main__":
    global fig, ax, hl

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.set_xlabel('Time Step')
    ax.set_ylabel('Average Queue Length')
    ax.set_title('Title')

    hl, = ax.plot([], [])

    plt.ion()
    # plt.show()
