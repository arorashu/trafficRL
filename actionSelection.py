import math
import random
import numpy
"""numActions = number of actions ie 2 for fixed phasing and N for variable phasing
            fixed phasing:      0 = same phase, 1 = next phase
            variable phasing:   i = index of next phase (can be same as curr phase)
                                numActions = N-1 if indexing of phases starts from 0
        E = 0.05
        age = age of agent, increment at each time step
"""
def eGreedy(numActions, E, age, currBSON):
    epsilon = math.exp(-1*E*age)
    rand = random.uniform(0,1)
    #print(epsilon-rand, "epsilon - rand")
    """ split into 2 probability ranges separated by epsilon ie 0<=p<=epsilon and epsilon<p<=1
        if rand<=epsilon, random action
        else greedy action
    """
    a = random.randint(0,numActions-1)
    # print(a, "rand")

    # Flag for checking if every qVal is equal
    flag = True
    if rand<=epsilon:
        return a
    else:
        nextMaxQ = currBSON[0]['qVal']
        greedyAction = 0
        for i in currBSON:
            # print(i, "currG")
            if nextMaxQ < i['qVal']:
                nextMaxQ = i['qVal']
                greedyAction = i['action']
                flag = False
        # print(greedyAction, "greedy")
        if(flag):
            # print(currBSON)
            return a
        return greedyAction

def softmax(numActions, numberCars, age, currBSON):
    # currBSON = DB entry corresponding to current (curr) state
    temperature = math.exp(-1*age/int(numberCars))
    options = numActions*[None]
    selProb = numActions*[None]
    selProbSum = 0
    for i in range(0, numActions):
        options[i] = i
        selProb[i] = math.exp(currBSON[i]['qVal']/temperature)
        selProbSum += selProb[i]

    for i in range(0, numActions):
        selProb[i] /= selProbSum

    return int(numpy.random.choice(options, p=selProb))

if __name__=="__main__":
    numActions = 5
    E = 0.05
    age = 10
    greedyAction = 2
    #print(softmax(numActions, E, age, currBSON))