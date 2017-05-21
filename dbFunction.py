from pymongo import MongoClient
from eGreedy import eGreedy
from qLearning import qLearning
from queueBalanceReward import queueBalanceReward
import globals
import pprint

client = MongoClient()
db = client['test']

# q = {"state":   "list",
#     "action":   0,
#     "qVal":     0,
#     "visits":   1}

# For fixed phasing

def initPre(ID):
    # if (qValues.find_one({"state": globals.pre})):
    #     return
    qValues = db['qValues' + ID]
    temp = []
    for i in range(0, globals.numActions+1):
        temp.append({"state":   globals.pre,
                    "action":   i,
                    "qVal":     0,
                    "visits":   1})
    qValues.insert_many(temp)

def dbFunction(curr, ID):
    qValues = db['qValues' + ID]
    initPre(ID)
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
