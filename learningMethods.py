""" Returns value to be updated as Q value of (st,at) i.e. (pre, preAction)
    alpha = learning rate
    gamma = discount factor
    reward = from getReward function
"""
def qLearning(currQ, alpha, gamma, reward, nextMaxQ):
    """ nextMaxQ =   max possible reward from next step i.e. max over Q of (st+1, at+1)
        scan DB for next possible actions of curr state and find nextMaxQ
    """
    newQ = currQ + alpha*(reward + gamma*nextMaxQ - currQ)
    #update currQ to newQ in DB
    return newQ

def sarsa(currQ, alpha, gamma, reward, nextQ):
    """ nextQ = Q(curr, nextAction)
                where nextAction is selected according to policy - eGreedy or softmax
    """
    newQ = currQ + alpha*(reward + gamma*nextQ - currQ)
    #update currQ to newQ in DB
    return newQ

if __name__=="__main__":
    #example values to test function
    currQ = 10
    alpha = 0.5
    gamma = 0.7
    reward = 2
    nextMaxQ= 5
    # print(qLearning(currQ, alpha, gamma, reward, nextMaxQ))
