from pymongo import MongoClient, ASCENDING
from actionSelection import eGreedy, softmax
from learningMethods import qLearning, sarsa
from rewardDefinitions import queueBalanceReward, delayReward
import globals
import pprint

pp = pprint.PrettyPrinter(indent=4)
client = MongoClient()

# q = {"state":   "list",
#     "action":   0,
#     "qVal":     0,
#     "visits":   1}

# For fixed phasing


def initTrafficLight(ID):
    pre = 6 * [0]
    qValues = db['qValues' + ID]
    if (qValues.find({"state": pre}).count() != 0):
        return
    temp = []
    for i in range(0, globals.numActions):
        temp.append({"state": pre,
                     "action": i,
                     "qVal": 0,
                     "visits": 1})
    qValues.insert_many(temp)


def initRunCount(options):
    # noOfRuns to store run statistics
    global db
    db = client[options.dbName]
    nor = db['noOfRuns']
    if (nor.count() == 0):
        nor.insert_one({"count": 0})
    else:
        nor.update_one({}, {'$inc': {'count': 1}})


def getRunCount():
    nor = db['noOfRuns']
    run_count = nor.find_one()['count']
    return run_count


def saveStats(traffic_light_count, temp_stats):
    run_id = getRunCount()
    stats = []
    temp = []
    for id in range(traffic_light_count):
        stats.append(temp)
        stats[id] = db['stats' + str(id)]
        run_stats = []
        run_stats.append({"run_id": run_id, "data": temp_stats[id]})
        stats[id].insert_many(run_stats)


def dbFunction(curr, pre, preAction, age, currPhase, ID, options):
    reward = 0
    newQ = 0
    nextAction = 0

    qValues = db['qValues' + ID]
    currBSON = qValues.find({"state": curr}).sort("action", ASCENDING)
    temp = []
    if (currBSON.count() == 0):
        for i in range(0, globals.numActions):
            temp.append({"state": curr,
                         "action": i,
                         "qVal": 0,
                         "visits": 1})
        qValues.insert_many(temp)
        currBSON = temp
    # TO-DO: visits to be updated

    if (options.stateRep == '1'):
        reward = queueBalanceReward(pre, curr, globals.N)
    else:
        reward = delayReward(pre, curr, globals.N)

    currQ = qValues.find_one({"state": pre, "action": preAction})['qVal']

    # converts currBSON from cursor to list
    tempBSON = []
    for c in currBSON:
        tempBSON.append(c)
    currBSON = tempBSON

    nextMaxQ = currBSON[0]['qVal']
    for i in currBSON:
        nextMaxQ = max(nextMaxQ, i['qVal'])

    if (options.learn == '1'):
        newQ = qLearning(currQ, globals.alpha, globals.gamma, reward, nextMaxQ)
    else:
        nextQ = 0
        if (options.actionSel == '1'):
            nextQ = currBSON[eGreedy(
                globals.numActions, globals.E, age, currBSON)]['qVal']
        else:
            nextQ = currBSON[softmax(
                globals.numActions, options.numberCars, age, currBSON)]['qVal']
        newQ = sarsa(currQ, globals.alpha, globals.gamma, reward, nextQ)

    qValues.find_one_and_update({"state": pre, "action": preAction}, {
                                '$set': {"qVal": newQ}})

    currBSON = qValues.find({"state": curr}).sort("action", ASCENDING)

    # converts currBSON from cursor to list
    tempBSON = []
    for c in currBSON:
        tempBSON.append(c)
    currBSON = tempBSON

    # nextAction = 0 or 1 (0 = continue same phase, 1 = go to next phase)
    # i.e. index of next phase = (currPhaseIndex + action) % N

    if (options.actionSel == '1'):
        nextAction = eGreedy(globals.numActions, globals.E, age, currBSON)
    else:
        nextAction = softmax(globals.numActions,
                             options.numberCars, age, currBSON)

    if (options.phasing == '1'):
        nextAction = (nextAction + currPhase) % 10

    return nextAction
