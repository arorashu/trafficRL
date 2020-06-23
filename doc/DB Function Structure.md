# DB Black Box Function Structure

1. Get state vector (size = 2+N where N = number of phases) from SUMO

1. Save it in curr

1. Check if state already exists in DB

   - If no, add all (curr,a) pairs to DB and initialize Q(curr,a) values to 0

1. Get reward by calling getReward function

   ```reward = queueBalanceReward(pre, curr, N)```

1. Update Q value of (pre, preAction) by calling Q learning function after setting variables

   ```
   currQ = Q(pre, preAction) # look up DB
   nextMaxQ = max( Q(curr,a) ) over all a #parse DB for  all a corresponding to curr

   newQ = qLearning(currQ, alpha, gamma, reward, nextMaxQ)

   Set Q(pre, preAction) to newQ in DB
   ```

1. Parse all (curr,a) pair values to get 'greedyAction'
  greedyAction = arg( max( Q( curr,a ) ) )   #merge with finding nextMaxQ, specified here for understanding

1. Call epsilon greedy function to tell nextAction (integer) to be taken in next time step. (TO BE PASSED TO SUMO)

   ```
   nextAction = eGreedy(numActions, E, age, greedyAction)
   ```

   - if Fixed Phasing:

     ```nextAction = 0 or 1 (0 = continue same phase, 1 = go to next phase)```
     i.e. index of next phase = (currPhaseIndex + action) % N

   - if Variable Phasing:

     ```0<= nextAction< N```
     i.e. index of next phase, if same as index of current phase then continue same phase)

1. Update variables after each time step

   ```
   age = age + 1
   pre = curr
   preAction = nextAction
   ```
