from pymongo import MongoClient
from eGreedy import eGreedy
from qLearning import qLearning
from queueBalanceReward import queueBalanceReward
import globals
import pprint

client = MongoClient()
db = client['trafficLight']

# q = {"state":   "list",
#     "action":   0,
#     "qVal":     0,
#     "visits":   1}

# For fixed phasing

def initTrafficLight(ID):
    
    qValues = db['qValues' + ID]
    temp = []
    for i in range(0, globals.numActions+1):
        temp.append({"state":   globals.pre,
                    "action":   i,
                    "qVal":     0,
                    "visits":   1})
    qValues.insert_many(temp)


def initRunCount():
    #noOfRuns to store run statistics
    nor = db['noOfRuns']
    if ( nor.count() == 0 ):
        nor.insert_one({"count" : 0});
    else:
        nor.update_one({}, {'$inc':{'count':1}})

    run_count = nor.find_one()['count']
    return run_count

def getRunCount():
    nor = db['noOfRuns']
    run_count = nor.find_one()['count']
    return run_count


def saveStats( traffic_light_count, temp_stats ):
    run_id = getRunCount()
    stats = []
    temp = []
    for id in range(traffic_light_count):
        stats.append(temp)
        stats[id] = db['stats' + str(id)]
        run_stats = []
        run_stats.append({"run_id": run_id, "data": temp_stats[id]})
        stats[id].insert_many(run_stats)

def dbFunction(curr, ID):
    qValues = db['qValues' + ID]
    #initPre(ID)
    currBSON = qValues.find({"state": curr})
    temp = []
    if (currBSON.count() == 0):
        for i in range(0, globals.numActions+1):
            temp.append({"state":   curr,
                        "action":   i,
                        "qVal":     0,
                        "visits":   1})
        qValues.insert_many(temp)
        currBSON = temp
    # TO-DO: visits to be updated

    reward = queueBalanceReward(globals.pre, curr, globals.N)

    # print(globals.pre, globals.preAction)
    currQ = qValues.find_one({"state":  globals.pre, "action":   globals.preAction})['qVal']

    tempBSON = []
    for c in currBSON:
        tempBSON.append(c)
    currBSON = tempBSON

    nextMaxQ = currBSON[0]['qVal']
    for i in currBSON:
        nextMaxQ = max(nextMaxQ, i['qVal'])

    newQ = qLearning(currQ, globals.alpha, globals.gamma, reward, nextMaxQ)

    qValues.find_one_and_update({"state": globals.pre, "action": globals.preAction}, {'$set': {"qVal": newQ}})

    currBSON = qValues.find({"state": curr})

    nextMaxQ = currBSON[0]['qVal']
    greedyAction = 0
    for i in currBSON:
        if nextMaxQ < i['qVal']:
            nextMaxQ = i['qVal']
            greedyAction = i['action']

    # nextAction = 0 or 1 (0 = continue same phase, 1 = go to next phase)
    # i.e. index of next phase = (currPhaseIndex + action) % N
    nextAction = eGreedy(globals.numActions, globals.E, globals.age, greedyAction)

    globals.age += 1
    globals.pre = curr[:]
    globals.preAction = nextAction

    return nextAction
