import math
import random
import numpy
"""numActions = number of actions ie 2 for fixed phasing and N for variable phasing
            fixed phasing:      0 = same phase, 1 = next phase
            variable phasing:   i = index of next phase (can be same as curr phase)
                                numActions = N-1 if indexing of phases starts from 0
    E = 0.05
    age = age of agent, increment at each time step
    currBSON = DB entry corresponding to current (curr) state
"""
def eGreedy(numActions, E, age, currBSON):
    epsilon = math.exp(-1*E*age)
    randNum = random.uniform(0,1)

    # print(epsilon, randNum, "epsilon and randNum", bool(randNum>epsilon))    

    """ split into 2 probability ranges separated by epsilon ie 0<=p<=epsilon and epsilon<p<=1
        if randNum<=epsilon, random action
        else greedy action
    """
    randAction = random.randint(0,numActions-1)
    # print(randAction, "randAction")

    # Flag for checking if every qVal is equal
    # if so, return a random action
    #flag = True
    if randNum<=epsilon:
        return randAction
    else:
        nextMaxQ = currBSON[0]['qVal']
        greedyAction = 0
        for i in currBSON:
            # print(i, "currG")
            if nextMaxQ < i['qVal']:
                nextMaxQ = i['qVal']
                greedyAction = i['action']
                #flag = False
        # print(greedyAction, "greedy")
        """
        if(flag):
            # print(currBSON)
            return randAction
        """
        if(numActions!=2):
            # variable phasing
            # ensures selection of random action if multiple actions have qVal = nextMaxQ
            # i.e. when there are multiple candidates for greedy action
            selAction=[]
            for i in currBSON:
                if(i['qVal']==nextMaxQ):
                    selAction.append(i['action'])
            greedyAction = selAction[random.randint(0,len(selAction)-1)]

            if (len(selAction)>1):
                print("new segment", greedyAction)

        return greedyAction

def softmax(numActions, numberCars, age, currBSON):
    temperature = math.exp(-1*age/int(numberCars))
    options = numActions*[None]
    selProb = numActions*[None]
    selProbSum = 0
    for i in range(0, numActions):
        options[i] = currBSON[i]['action']
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
