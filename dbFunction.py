from pymongo import MongoClient
from eGreedy import eGreedy
from qLearning import qLearning
from queueBalanceReward import queueBalanceReward

client = MongoClient()
db = client['test']

qValues = db['qValues']

# q = {"state":   "list",
#     "action":   0,
#     "qVal":     0,
#     "visits":   1}

# For fixed phasing
def dbFunction(curr):
    currBSON = qValues.find({"state": curr})
    temp = []
    if (currBSON.count() == 0):
        for i in (0, numActions+1):
            temp.append({"state":   curr,
                        "action":   i,
                        "qVal":     0,
                        "visits":   1})
        qValues.insert_many(temp)
        currBSON = temp

    # TO-DO: visits to be updated

    reward = queueBalanceReward(pre, curr, N)

    currQ = qValues.find_one({"state":  pre,
                            "action":   preAction}).qVal

    nextMaxQ = currBSON[0].qVal
    for i in (0, numActions+1):
        nextMaxQ = max(nextMaxQ, currBSON[i].qVal)
    newQ = qLearning(currQ, alpha, gamma, reward, nextMaxQ)

    qValues.find_one_and_update({"state": pre, "action": preAction}, {'$set': {"qVal": newQ}})

    currBSON = qValues.find({"state": curr})

    nextMaxQ = currBSON[0].qVal
    greedyAction = 0
    for i in (0, numActions+1):
        if nextMaxQ < currBSON[i].qVal:
            nextMaxQ = currBSON[i].qVal
            greedyAction = currBSON[i].action

    # nextAction = 0 or 1 (0 = continue same phase, 1 = go to next phase)
    # i.e. index of next phase = (currPhaseIndex + action) % N
    nextAction = eGreedy(numActions, E, age, greedyAction)

    age = age + 1
    pre = curr
    preAction = nextAction

    return nextAction
