import os
import sys
import optparse
import subprocess
import random
import globals
from globals import init
from helper import updateVehDistribution, generate_routefile, getDBName
from runner import run

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    optParser.add_option("--cars", "-C", dest="numberCars", default=200000, metavar="NUM",
                         help="specify the number of cars generated for simulation")
    optParser.add_option("--bracket", dest="bracket", default=4, metavar="BRACKET",
                         help="specify the number with which to partition the range of queue length/cumulative delay")
    optParser.add_option("--start", dest="start", default=0, metavar="NUM",
                         help="specify the start index of the combinations to run")
    optParser.add_option("--end", dest="end", default=15, metavar="BRACKET",
                         help="specify the end index of the combinations to run")
    optParser.add_option("--seed", dest="seed", default=42, metavar="BRACKET",
                         help="specify the seed for random to so that results can be repeated")
    optParser.add_option("--learning", dest="learn", default='1', metavar="NUM", choices= ['0', '1', '2'],
                         help="specify learning method (0 = No Learning, 1 = Q-Learning, 2 = SARSA)")
    optParser.add_option("--state", dest="stateRep", default='1', metavar="NUM", choices= ['1', '2'],
                         help="specify traffic state representation to be used (1 = Queue Length, 2 = Cumulative Delay)")
    optParser.add_option("--phasing", dest="phasing", default='1', metavar="NUM", choices= ['1', '2'],
                         help="specify phasing scheme (1 = Fixed Phasing, 2 = Variable Phasing)")
    optParser.add_option("--action", dest="actionSel", default='1', metavar="NUM", choices= ['1', '2'],
                         help="specify action selection method (1 = epsilon greedy, 2 = softmax)")
    optParser.add_option("--dbName", dest="dbName", default='tl', metavar="STRING",
                         help="specify dbName prefix")
    options, args = optParser.parse_args()
    return options

# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # give random a seed so that results are repeatable and same vehicle distribution is generated for same seed
    random.seed(options.seed)
    updateVehDistribution()

    edgeWidth=5
    lateral_resolution_width=2.5
    lateral_resolution_width=float(edgeWidth/5)
    lateral_resolution_width=str(lateral_resolution_width)


    options.start = int(options.start)
    options.end = int(options.end)

    # generate the route file for this simulation
    generate_routefile(options)

    if (options.start == 0):
        # 0. No learning
        print("0")
        options.learn = '0'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross_no_learn.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--queue-output", "queue.xml",
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Final Average QL for no learning : ", run(options))

    ## Fixed Phasing
    options.phasing = '1'

    if (options.start <= 1 and options.end >= 1):
        # 1. stateRep = queue, learning = Q-learn, action selection = e-greedy
        print("1")
        options.stateRep = '1'
        options.learn = '1'
        options.actionSel = '1'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--queue-output", "queue.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for Q-learning with state=queue and actSel=e-greedy FIXED: ", run(options))

    if (options.start <= 2 and options.end >= 2):
        # 2. stateRep = queue, learning = Q-learn, action selection = softmax
        print("2")
        options.stateRep = '1'
        options.learn = '1'
        options.actionSel = '2'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--queue-output", "queue.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for Q-learning with state=queue and actSel=softmax FIXED: ", run(options))

    if (options.start <= 3 and options.end >= 3):
        # 3. stateRep = queue, learning = SARSA, action selection = e-greedy
        print("3")
        options.stateRep = '1'
        options.learn = '2'
        options.actionSel = '1'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--queue-output", "queue.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for SARSA with state=queue and actSel=e-greedy FIXED: ", run(options))

    if (options.start <= 4 and options.end >= 4):
        # 4. stateRep = queue, learning = SARSA, action selection = softmax
        print("4")
        options.stateRep = '1'
        options.learn = '2'
        options.actionSel = '2'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--queue-output", "queue.xml",
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for SARSA with state=queue and actSel=softmax FIXED: ", run(options))

    if (options.start <= 5 and options.end >= 5):
        # 5. stateRep = delay, learning = Q-learning, action selection = e-greedy
        print("5")
        options.stateRep = '2'
        options.learn = '1'
        options.actionSel = '1'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--queue-output", "queue.xml",
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for Q-learning with state=delay and actSel=e-greedy FIXED: ", run(options))

    if (options.start <= 6 and options.end >= 6):
        # 6. stateRep = delay, learning = Q-learning, action selection = softmax
        print("6")
        options.stateRep = '2'
        options.learn = '1'
        options.actionSel = '2'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--queue-output", "queue.xml",
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for Q-learning with state=delay and actSel=softmax FIXED: ", run(options))

    if (options.start <= 7 and options.end >= 7):
        # 7. stateRep = delay, learning = SARSA, action selection = e-greedy
        print("7")
        options.stateRep = '2'
        options.learn = '2'
        options.actionSel = '1'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--queue-output", "queue.xml",
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for SARSA with state=delay and actSel=e-greedy FIXED : ", run(options))

    if (options.start <= 8 and options.end >= 8):
        # 8. stateRep = delay, learning = SARSA, action selection = softmax
        print("8")
        options.stateRep = '2'
        options.learn = '2'
        options.actionSel = '2'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--queue-output", "queue.xml",
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for SARSA with state=delay and actSel=softmax FIXED: ", run(options))

    ## Variable Phasing
    options.phasing = '2'
    globals.numActions = 6

    if (options.start <= 9 and options.end >= 9):
        # 9. stateRep = queue, learning = Q-learn, action selection = e-greedy
        print("9")
        options.stateRep = '1'
        options.learn = '1'
        options.actionSel = '1'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross_variable.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--queue-output", "queue.xml",
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for Q-learning with state=queue and actSel=e-greedy VARIABLE: ", run(options))

    if (options.start <= 10 and options.end >= 10):
        # 10. stateRep = queue, learning = Q-learn, action selection = softmax
        print("10")
        options.stateRep = '1'
        options.learn = '1'
        options.actionSel = '2'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross_variable.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--queue-output", "queue.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for Q-learning with state=queue and actSel=softmax VARIABLE: ", run(options))

    if (options.start <= 11 and options.end >= 11):
        # 11. stateRep = queue, learning = SARSA, action selection = e-greedy
        print("11")
        options.stateRep = '1'
        options.learn = '2'
        options.actionSel = '1'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross_variable.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--queue-output", "queue.xml",
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for SARSA with state=queue and actSel=e-greedy VARIABLE: ", run(options))

    if (options.start <= 12 and options.end >= 12):
        # 12. stateRep = queue, learning = SARSA, action selection = softmax
        print("12")
        options.stateRep = '1'
        options.learn = '2'
        options.actionSel = '2'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross_variable.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--queue-output", "queue.xml",
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for SARSA with state=queue and actSel=softmax VARIABLE: ", run(options))

    if (options.start <= 13 and options.end >= 13):
        # 13. stateRep = delay, learning = Q-learning, action selection = e-greedy
        print("13")
        options.stateRep = '2'
        options.learn = '1'
        options.actionSel = '1'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross_variable.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--queue-output", "queue.xml",
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for Q-learning with state=delay and actSel=e-greedy VARIABLE: ", run(options))

    if (options.start <= 14 and options.end >= 14):
        # 14. stateRep = delay, learning = Q-learning, action selection = softmax
        print("14")
        options.stateRep = '2'
        options.learn = '1'
        options.actionSel = '2'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross_variable.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--queue-output", "queue.xml",
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for Q-learning with state=delay and actSel=softmax VARIABLE: ", run(options))

    if (options.start <= 15 and options.end >= 15):
        # 15. stateRep = delay, learning = SARSA, action selection = e-greedy
        print("15")
        options.stateRep = '2'
        options.learn = '2'
        options.actionSel = '1'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross_variable.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--queue-output", "queue.xml",
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for SARSA with state=delay and actSel=e-greedy VARIABLE: ", run(options))

    if (options.start <= 16 and options.end >= 16):
        # 16. stateRep = delay, learning = SARSA, action selection = softmax
        print("16")
        options.stateRep = '2'
        options.learn = '2'
        options.actionSel = '2'
        options.dbName = getDBName(options)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                 "-n", "data/cross.net.xml",
                                 "-a", "data/cross_variable.add.xml",
                                 "-r", "data/cross.rou.xml",
                                 "--lateral-resolution",lateral_resolution_width,
                                 "--queue-output", "queue.xml",
                                 "--tripinfo-output", "tripinfo.xml",
                                 "--duration-log.statistics", "true",
                                 "--output-prefix", 'outputs/logs/' + options.dbName
                                 ])
        init(options)
        print("Average QL for SARSA with state=delay and actSel=softmax VARIABLE: ", run(options))
