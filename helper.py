from xml.etree import ElementTree as et
import os
import random
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from dbFunction import getRunCount

client = MongoClient()


def getDBName(options):
    name = options.dbName
    if (options.learn == '0'):
        return name + '_preTimed'
    elif (options.learn == '1'):
        name += '_Q-Lrn'
    else:
        name += '_SARSA'

    if (options.stateRep == '1'):
        name += '_queue'
    else:
        name += '_delay'

    if (options.actionSel == '1'):
        name += '_greedy'
    else:
        name += '_softmx'

    if (options.phasing == '1'):
        name += '_fix'
    else:
        name += '_var'

    return name


def updateVehDistribution():
    fileDir = os.path.dirname(os.path.realpath('__file__'))
    src = et.parse(os.path.join(fileDir, 'data/cross.src.xml'))
    dst = et.parse(os.path.join(fileDir, 'data/cross.dst.xml'))

    srcEdges = src.findall('*/edge')
    dstEdges = dst.findall('*/edge')

    # generate uniformly dstributed random numbers that sum to 1
    listRandSrc = [0, 1]
    listRandDst = [0, 1]
    for i in range(len(srcEdges) - 1):
        listRandSrc.append(round(random.uniform(0, 1), 4))
        listRandDst.append(round(random.uniform(0, 1), 4))
    listRandSrc.sort()
    listRandDst.sort()

    for i, edge in enumerate(srcEdges):
        edge.set('value', str(listRandSrc[i + 1] - listRandSrc[i]))

    for i, edge in enumerate(dstEdges):
        edge.set('value', str(listRandDst[i + 1] - listRandDst[i]))

    src.write(os.path.join(fileDir, 'data/cross.src.xml'))
    dst.write(os.path.join(fileDir, 'data/cross.dst.xml'))

# fringeFactor=10
# this uses randomtrips.py to generate a routefile with random traffic


def generate_routefile(numberCars):
    # generating route file using randomTrips.py
    if (os.name == "posix"):
        vType = '\"\'typedist1\'\"'
    else:
        vType = '\'typedist1\''
    fileDir = os.path.dirname(os.path.realpath('__file__'))
    filename = os.path.join(fileDir, 'data/cross.net.xml')
    os.system("python randomTrips.py -n " + filename
              + " --weights-prefix " + os.path.join(fileDir, 'data/cross')
              + " -e " + str(numberCars)
              + " -p  4" + " -r " + os.path.join(fileDir, 'data/cross.rou.xml')
              # + " --fringe-factor " + str(fringeFactor)
              + " --trip-attributes=\"type=\"" + vType + "\"\""
              + " --additional-file " + \
              os.path.join(fileDir, 'data/type.add.xml')
              + " --edge-permission emergency passenger taxi bus truck motorcycle bicycle"
              )


def plotGraph(xVar, yVar):
    hl.set_xdata(np.append(hl.get_xdata(), xVar))
    hl.set_ydata(np.append(hl.get_ydata(), yVar))
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    # plt.pause(0.0001)
    return


def savePlot(dbName):
    ax.set_title(dbName)

    plt.tight_layout()
    plt.grid(alpha=0.8)
    plt.savefig('outputs/ql' + dbName + '.png')
    plt.savefig('outputs/ql' + dbName + '.pdf')


if __name__ != "__main__":
    global fig, ax, hl

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.set_xlabel('Time Step (x300)')
    ax.set_ylabel('Average Queue Length')

    hl, = ax.plot([], [])

    plt.ion()
    # plt.show()
else:
    # Runs when helper is directly executed
    # For testing purposes
    random.seed(42)
    updateVehDistribution()
