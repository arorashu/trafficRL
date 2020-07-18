# Scope

## PROBLEMS

* SUMO lane length approximation for state representation
  * re-consider when increasing no. of intersections

* Effect of min. green time
  * if min green time = 10 and step = 5, one step of computation will be useless
  * update of variables at the end of this step will also be wrong. especially, action updates
  * will also increase size of DB as new state will be created that needn't be analyzed and added to DB

  **POSSIBLE SOLUTION**: If time in curr phase (2nd entry in state vector) is less than min. green time, then let process sleep. Sleep before adding to DB (if at all it doesn't exist)

* Effect of yellow phase time
  * what will be state if queried at this time
  * effect of RL computations at this time

  POSSIBLE SOLUTION: Set yellow time and step so as to avoid this

* Making alpha i.e. learning rate variable
  * done in paper

   **POSSINLE SOLUTION:** Keep count of visits to pair (s,a) in DB

## IMPROVEMENTS

* Consider emergency vehicles

* Consider 3 roads intersections
  * present in real world
  * will be present when importing map from OSM
