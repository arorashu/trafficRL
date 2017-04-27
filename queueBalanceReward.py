def queueBalanceReward(pre, curr, N):
    """pre = state in previous time step (2+N vector)
    curr = current state (2+N vector)
    N = number of phases"""
    reward = 0
    # print(curr, pre, N, "CURR PRE N")
    for i in range(0, N):
        reward = reward - (curr[i]**2 - pre[i]**2)
    #print(reward, "Reward")
    return reward

if __name__ == "__main__":
    pre=[0,0,1,2,3]
    curr=[0,0,5,6,7]
    N=3
    # print (getReward(pre,curr,N))
