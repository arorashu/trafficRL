# GLOBAL VALUES INITIALIZATION

<pre>
 N = 6 (number of phases)
 E = 0.05
 gamma = 0.8
 age = 0
 numActions =
            fixed phasing : 2 (where 0 = same phase, 1 = next phase)
            variable phasing: N (if indexing of phases starts from 0, else N)

    pre = N*[0]    #intitial state - all queue lengths zero, start with phase 0 and initially duration of phase is 0
    preAction = 0      #continue in phase 0 for some time
 alpha = <>
</pre>

### NOTE - decide initialization values for alpha (keep const. now for simplicity)

### NOTE - SUMO simulation start phase should have index 0

### NOTE - indexing of phases starts from 0

### NOTE - Initialize DB to have ( (0,0,0,0,0,0,0,0), a) pairs with Q values = 0

### NOTE - Ensure lane length approximation to control DB size
