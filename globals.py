def init(options):
    global N, E, alpha, gamma, numActions
    N = 6
    E = 0.01
    gamma = 0.8
    numActions = 2
    if(options.phasing == '2'):
        numActions = 6
    alpha = 0.4
