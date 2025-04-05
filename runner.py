from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
from collections import Counter
from pymongo import MongoClient
from dbFunction import dbFunction, initTrafficLight, initRunCount, saveStats, getRunCount
from globals import init
from helper import updateVehDistribution, plotGraph, savePlot, generate_routefile, getDBName


# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "Please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci
client = MongoClient()


def run(options):
    initRunCount(options)
    db = client[options.dbName]
    tempStats = []
    temp = []

    # get list of traffic lights
    trafficLights = traci.trafficlight.getIDList()
    trafficLightsNumber = traci.trafficlight.getIDCount()

    # we set every light to phase 0
    for ID in trafficLights:
        traci.trafficlight.setPhase(ID, 0)
        initTrafficLight(ID)
        tempStats.append(temp)

    phaseVector = 6 * [None]
    prePhase = trafficLightsNumber * [phaseVector]
    preAction = trafficLightsNumber * [0]
    currPhase = trafficLightsNumber * [0]
    currTime = 0
    dbStep = 10
    avgQL = trafficLightsNumber * [0]
    avgQLCurr = trafficLightsNumber * [0]
    oldVeh = trafficLightsNumber * [None]
    cumuDelay = trafficLightsNumber * [None]
    ages = trafficLightsNumber * [0]
    avgPlot = 0

    # get age value from DB
    i = 0
    for ID in trafficLights:
        qValues = db['qValues' + ID]
        if (qValues.count_documents({"ageExists": True}) != 0):
            ages[i] = qValues.find_one({"ageExists": True})['age']
        i += 1

    # execute the TraCI control loop
    step = 1
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        # current traffic light index number
        i = 0
        for ID in trafficLights:

            # get lanes for each traffic light
            lanes = traci.trafficlight.getControlledLanes(ID)
            lanesUniq = []
            # get unique lanes
            j = 0
            while j < len(lanes):
                lanesUniq.append(lanes[j])
                j += 2
                lanesUniq.append(lanes[j])
                j += 3
            lanes = lanesUniq

            # get average queue length for current time step
            queueLength = []
            avgQLCurr[i] = 0
            for lane in lanes:
                queueLength.append(traci.lane.getLastStepHaltingNumber(lane))
                avgQLCurr[i] += traci.lane.getLastStepHaltingNumber(lane)
            avgQLCurr[i] = avgQLCurr[i] / (len(lanes) * 1.0)

            # get average queue length till now
            avgQL[i] = (avgQL[i] * step + avgQLCurr[i]) / ((step + 1) * 1.0)

            # call plot graph with avg ql every 10*dbDtep
            if(i == trafficLightsNumber - 1 and step % (dbStep * 30) == 0):
                avgPlot /= dbStep * 10
                plotGraph(step / (dbStep * 30), avgPlot)
                avgPlot = 0
            elif(i == trafficLightsNumber - 1):
                avgQLTotal = 0
                for avgQLC in avgQLCurr:
                    avgQLTotal += avgQLC
                avgQLTotal = avgQLTotal / (trafficLightsNumber * 1.0)
                avgPlot += avgQLTotal

            options.bracket = int(options.bracket)

            # run only for every db_step and when phase is not yellow
            # yellow compulsory
            currPhase[i] = traci.trafficlight.getPhase(ID)
            condition = True
            if (options.phasing == '1'):
                condition = currPhase[i] != 2 and currPhase[i] != 4 and currPhase[i] != 7 and currPhase[i] != 9

            if (step % dbStep == 0 and condition):
                # emergency vehicle
                for x in range(len(lanes)):
                    listVehicles = traci.lane.getLastStepVehicleIDs(lanes[x])
                    for veh in listVehicles:
                        if(traci.vehicle.getTypeID(veh) == "v1"):
                            queueLength[x] += 5

                # print and save current stats
                # print(avgQL[i], avgQLCurr[i], step, ID, "AvgQLs, step, ID")
                tempStats[int(ID)].append({"step": step,
                                           "curr_qL": avgQLCurr[i],
                                           "avgQL": avgQL[i],
                                           "ID": ID})

                # skip everything and run according to default values
                if (options.learn == '0'):
                    i += 1
                    continue

                if (options.stateRep == '1'):
                    # generate current step's phase vector - with queueLength
                    phaseVector[0] = int(
                        round(max(queueLength[4], queueLength[5]) / options.bracket))
                    phaseVector[1] = int(
                        round(max(queueLength[0], queueLength[4]) / options.bracket))
                    phaseVector[2] = int(
                        round(max(queueLength[0], queueLength[1]) / options.bracket))
                    phaseVector[3] = int(
                        round(max(queueLength[3], queueLength[2]) / options.bracket))
                    phaseVector[4] = int(
                        round(max(queueLength[2], queueLength[6]) / options.bracket))
                    phaseVector[5] = int(
                        round(max(queueLength[6], queueLength[7]) / options.bracket))

                elif (options.stateRep == '2'):
                    # get cumulative delay
                    cumulativeDelay = cumuDelay[i]
                    oldVehicles = oldVeh[i]
                    vehicles = []
                    for z in lanes:
                        vehicles.append(Counter())
                    if(cumulativeDelay is None):
                        cumulativeDelay = len(lanes) * [0]
                    if(oldVehicles is None):
                        oldVehicles = []
                        for z in lanes:
                            oldVehicles.append(Counter())
                    j = 0
                    for lane in lanes:
                        listVehicles = traci.lane.getLastStepVehicleIDs(lane)
                        for veh in listVehicles:
                            vehicles[j][veh] = oldVehicles[j][veh]
                            if (traci.vehicle.isStopped(veh)):
                                vehicles[j][veh] += 1
                                cumulativeDelay[j] += 1
                        vehToDelete = oldVehicles[j] - vehicles[j]
                        for veh, vDelay in vehToDelete.most_common():
                            cumulativeDelay[j] -= vDelay
                        oldVehicles[j] = vehicles[j]
                        j += 1
                    cumuDelay[i] = cumulativeDelay
                    oldVeh[i] = oldVehicles

                    # generate current step's phase vector - with
                    # cumulativeDelay
                    phaseVector[0] = int(
                        round(cumulativeDelay[4] + cumulativeDelay[5]) / options.bracket)
                    phaseVector[1] = int(
                        round(cumulativeDelay[0] + cumulativeDelay[4]) / options.bracket)
                    phaseVector[2] = int(
                        round(cumulativeDelay[0] + cumulativeDelay[1]) / options.bracket)
                    phaseVector[3] = int(
                        round(cumulativeDelay[3] + cumulativeDelay[2]) / options.bracket)
                    phaseVector[4] = int(
                        round(cumulativeDelay[2] + cumulativeDelay[6]) / options.bracket)
                    phaseVector[5] = int(
                        round(cumulativeDelay[6] + cumulativeDelay[7]) / options.bracket)

                # update values
                nextAction = dbFunction(
                    phaseVector, prePhase[i], preAction[i], ages[i], currPhase[i], ID, options)
                ages[i] += 0.01
                prePhase[i] = phaseVector[:]

                if(options.phasing == '1'):
                    traci.trafficlight.setPhase(ID, nextAction)
                    if(nextAction != currPhase[i]):
                        nextAction = 1
                    else:
                        nextAction = 0
                else:
                    if(nextAction != currPhase[i]):
                        oldRGYState = traci.trafficlight.getRedYellowGreenState(
                            ID)
                        traci.trafficlight.setPhase(ID, nextAction)
                        newRGYState = traci.trafficlight.getRedYellowGreenState(
                            ID)
                        # print(oldRGYState, newRGYState, "old new")

                        midRGYState = ""
                        for k, c in enumerate(oldRGYState):
                            if (c == 'G' and newRGYState[k] == 'r'):
                                midRGYState += 'Y'
                            elif(c == 'G' and newRGYState[k] == 'g'):
                                midRGYState += 'g'
                            else:
                                midRGYState += c
                        # print(midRGYState, "mid")

                        traci.trafficlight.setRedYellowGreenState(
                            ID, midRGYState)
                        tempCounter = 5
                        while(tempCounter > 0):
                            traci.simulationStep()
                            tempCounter -= 1
                        traci.trafficlight.setProgram(ID, 'custom2')
                        traci.trafficlight.setPhase(ID, nextAction)
                    else:
                        traci.trafficlight.setPhase(ID, nextAction)

                preAction[i] = nextAction

            # increment traffic light index
            i += 1
        step += 1

    # update age in DB
    i = 0
    for ID in trafficLights:
        qValues = db['qValues' + ID]
        qValues.find_one_and_update(
            {"ageExists": True}, {"$set": {"age": ages[i]}}, upsert=True)
        i += 1

    # print final average
    avgQLTotal = 0
    i = 0
    for avgQLC in avgQL:
        # print(avgQLC, "Final", i)
        i += 1
        avgQLTotal += avgQLC
    avgQLTotal = avgQLTotal / (trafficLightsNumber * 1.0)
    # print(avgQLTotal, "Final Total")

    saveStats(trafficLightsNumber, tempStats)
    savePlot(options.dbName + str(getRunCount()))

    traci.close()
    sys.stdout.flush()

    return avgQLTotal

# this gets the input parameters specified to the program


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    optParser.add_option("--cars", "-C", dest="numberCars", default=1000, metavar="NUM",
                         help="specify the number of cars generated for simulation")
    optParser.add_option("--bracket", dest="bracket", default=4, metavar="BRACKET",
                         help="specify the number with which to partition the range of queue length/cumulative delay")
    optParser.add_option("--learning", dest="learn", default='1', metavar="NUM", choices=['0', '1', '2'],
                         help="specify learning method (0 = No Learning, 1 = Q-Learning, 2 = SARSA)")
    optParser.add_option("--state", dest="stateRep", default='1', metavar="NUM", choices=['1', '2'],
                         help="specify traffic state representation to be used (1 = Queue Length, 2 = Cumulative Delay)")
    optParser.add_option("--phasing", dest="phasing", default='1', metavar="NUM", choices=['1', '2'],
                         help="specify phasing scheme (1 = Fixed Phasing, 2 = Variable Phasing)")
    optParser.add_option("--action", dest="actionSel", default='1', metavar="NUM", choices=['1', '2'],
                         help="specify action selection method (1 = epsilon greedy, 2 = softmax)")
    optParser.add_option("--sublane", dest="sublaneNumber", default=5, metavar="FLOAT",
                         help="specify number of sublanes per edge (max=6) ")
    optParser.add_option("--dbstep", dest="sbStep", default=10, metavar="NUM",
                         help="specify dbStep, default is 10 ")
    optParser.add_option("--dbName", dest="dbNamePrefix", default='trafficRL', metavar="STRING",
                         help="specify dbName prefix")
    optParser.add_option("--seed", dest="seed", default=42, metavar="BRACKET",
                         help="Only for automate.py")
    optParser.add_option("--start", dest="start", default=0, metavar="NUM",
                         help="Only for automate.py")
    optParser.add_option("--end", dest="end", default=16, metavar="BRACKET",
                         help="Only for automate.py")
    options, args = optParser.parse_args()
    return options


def run_sim(mode_num, options):
    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    options.dbName = getDBName(options)

    traci_add_option = "data/cross.add.xml"
    if (options.learn == '0'):
        traci_add_option = "data/cross_no_learn.add.xml"
    elif (options.phasing == '2'):
        traci_add_option = "data/cross_variable.add.xml"

    edgeWidth = 5
    lateral_resolution_width = 2.5
    if(int(options.sublaneNumber) <= 6.0):
        lateral_resolution_width = float(
            edgeWidth / int(options.sublaneNumber))
    else:
        print("WARNING: sublanes is greater than 6, defaulting to 2")
    lateral_resolution_width = str(lateral_resolution_width)
    mode_description = "No Learning"
    if (options.learn != '0'):
        mode_description = 'Learning=%s, with State=%s, ActionSelection=%s and %s Phasing' % (
            "Q-learning" if options.learn == '1' else "SARSA", "Queue Length" if options.stateRep == '1' else "Cumulative Delay", "e-greedy" if options.actionSel == '1' else "softmax", "Fixed" if options.phasing == '1' else "Variable")

    print("\n****************\nMode", mode_num, ":", mode_description, "\n****************\n")
    init(options)
    traci.start([sumoBinary, "-a", traci_add_option,
                 "-c", "data/cross.sumocfg",
                 "-n", "data/cross.net.xml",
                 "-r", "data/cross.rou.xml",
                 "--lateral-resolution", lateral_resolution_width,
                 "--queue-output", "queue.xml",
                 "--tripinfo-output", "tripinfo.xml",
                 "--duration-log.statistics", "true",
                 "--output-prefix", 'outputs/logs/' + options.dbName
                 ])
    print("\n****************\nAverage QL for", mode_description, " =", run(options), "\n****************\n")


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()
    # generate the route file for this simulation
    generate_routefile(options.numberCars)

    # Sumo is started as a subprocess and then the python script connects
    run_sim("Custom", options)
