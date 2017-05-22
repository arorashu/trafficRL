"""

"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
from dbFunction import dbFunction, initTrafficLight, initRunCount, saveStats
from globals import init


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

def run(options):

    runID = initRunCount()
    tempStats = []
    temp = []

    # get list of traffic lights
    trafficLights = traci.trafficlights.getIDList()
    trafficLightsNumber = traci.trafficlights.getIDCount()

    # we set every light to phase 0
    for ID in trafficLights:
        traci.trafficlights.setPhase(ID, 0)
        initTrafficLight(ID)
        tempStats.append(temp)

    phaseVector = 6*[None]
    ages = trafficLightsNumber*[0]
    prePhase = trafficLightsNumber*[phaseVector]
    preAction = trafficLightsNumber*[0]
    currPhase = trafficLightsNumber*[0]
    currTime = 0
    dbStep = 100
    avgQL = trafficLightsNumber*[0]
    avgQLCurr = trafficLightsNumber*[0]

    # execute the TraCI control loop
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        # current phase index number
        i = 0
        for ID in trafficLights:

            # get lanes for each traffic light
            lanes = traci.trafficlights.getControlledLanes(ID)
            lanesUniq = []
            j = 0
            while j < len(lanes):
                if (j%2 == 0):
                    lanesUniq.append(lanes[j])
                j+=1
            lanes = lanesUniq


            # get average queue length for current time step
            queueLength=[]
            avgQLCurr[i] = 0
            for lane in lanes:
                queueLength.append(traci.lane.getLastStepHaltingNumber(lane))
                avgQLCurr[i] += traci.lane.getLastStepHaltingNumber(lane)
            avgQLCurr[i] = avgQLCurr[i]/(len(lanes)*1.0)


            # get average queue length till now
            avgQL[i] = (avgQL[i]*step + avgQLCurr[i])/((step+1)*1.0)

            # run only for every db_step
            if (step%dbStep == 0) :

                # generate current step's phase vector
                phaseVector[0] = int(round(max(queueLength[0], queueLength[1])/options.qlBracket))
                phaseVector[1] = int(round(max(queueLength[0], queueLength[5])/options.qlBracket))
                phaseVector[2] = int(round(max(queueLength[4], queueLength[5])/options.qlBracket))
                phaseVector[3] = int(round(max(queueLength[6], queueLength[7])/options.qlBracket))
                phaseVector[4] = int(round(max(queueLength[2], queueLength[6])/options.qlBracket))
                phaseVector[5] = int(round(max(queueLength[2], queueLength[3])/options.qlBracket))

                # print and save current stats
                print(avgQL[i], avgQLCurr[i], step, ID)
                tempStats[int(ID)].append({"step": step,
                                            "curr_qL": avgQLCurr[i],
                                            "avgQL": avgQL[i],
                                            "ID": ID})

                nextAction = dbFunction(phaseVector, prePhase[i], preAction[i], ages[i], ID)
                ages[i] += 1
                prePhase[i] = phaseVector[:]
                preAction[i] = nextAction
                if (nextAction == 1):
                    currPhase[i] = (currPhase[i] + 1)%6
                    traci.trafficlights.setPhase(ID, currPhase[i])
                    currTime = 1
                else :
                    currTime += 1

            # incremetn current phase index
            i+=1
        step += 1

    avgQLTotal = 0
    i = 0
    for avgQLC in avgQL:
        print(avgQLC, "Final", i)
        i += 1
        avgQLTotal += avgQLC
    avgQLTotal = avgQLTotal/(trafficLightsNumber*1.0)
    print(avgQLTotal, "Final Total")

    saveStats(trafficLightsNumber, tempStats)

    traci.close()
    sys.stdout.flush()

# this gets the input parameters specified to the program
def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    optParser.add_option("--cars", "-C", dest="numberCars", default=20000, metavar="NUM",
                         help="specify the number of cars generated for simulation")
    optParser.add_option("--qlBracket", dest="qlBracket", default=10, metavar="BRACKET",
                         help="specify the number with which to partition the range of queue length")
    options, args = optParser.parse_args()
    return options

# this uses randomtrips.py to generate a routefile with random traffic
def generate_routefile(options):
    #generating route file using randomTrips.py
    fileDir = os.path.dirname(os.path.realpath('__file__'))
    print(str(options.numberCars))
    filename = os.path.join(fileDir, 'data/cross.net.xml')
    os.system("python randomTrips.py -n " + filename
        + " --weights-prefix " + os.path.join(fileDir, 'data/cross') + " -e " + str(options.numberCars)
        + " -p  4" + " -r " + os.path.join(fileDir, 'data/cross.rou.xml'))


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # generate the route file for this simulation
    generate_routefile(options)

    # Sumo is started as a subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                             "-n", "data/cross.net.xml",
                             "-r", "data/cross.rou.xml",
                             "--queue-output", "queue.xml",
                             "--tripinfo-output", "tripinfo.xml"])
    init()
    run(options)
