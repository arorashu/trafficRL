import math
import random
def eGreedy(numActions, E, age, greedyAction):
    """numActions = number of actions ie 1 for fixed phasing and N-1 for variable phasing
            fixed phasing:      0 = same phase, 1 = next phase
            variable phasing:   i = index of next phase (can be same as curr phase)
                                numActions = N-1 if indexing of phases starts from 0
        E = 0.05
        age = age of agent, increment at each time step
        greedyAction = action with best Q(s,a)
    """
    epsilon = math.exp(-1*E*age)
    rand = random.uniform(0,1)
    """ split into 2 probability ranges separated by epsilon ie 0<=p<=epsilon and epsilon<p<=1
        if rand<=epsilon, random action
        else greedy action
    """
    if rand<=epsilon:
        return random.randint(0,numActions)
    else:
        return greedyAction

if __name__=="__main__":
    numActions = 5
    E = 0.05
    age = 10
    greedyAction = 2
    # print(eGreedy(numActions, E, age, greedyAction))
