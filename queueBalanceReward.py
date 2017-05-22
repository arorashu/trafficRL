""" pre = state in previous time step (2+N vector)
    curr = current state (2+N vector)
    N = number of phases """

def queueBalanceReward(pre, curr, N):
    # STATE REPRESENTATION IS QUEUE LENGTH

    reward = 0
    # print(curr, pre, N, "CURR PRE N")
    for i in range(0, N):
        reward = reward - (curr[i]**2 - pre[i]**2)
    #print(state reward, "Reward")
    return reward

def delayReward(pre, curr, N):
    # STATE REPRESENTATION IS CUMULATIVE DELAY

    reward = 0
    # print(curr, pre, N, "CURR PRE N")
    for i in range(0, N):
        reward = reward - (curr[i] - pre[i])
    #print(delay reward, "Reward")
    return reward

if __name__ == "__main__":
    pre=[0,0,1,2,3]
    curr=[0,0,5,6,7]
    N=3
    #print (delayReward(pre,curr,N))