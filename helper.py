from xml.etree import ElementTree as et
import os
import random

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
