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

    run_id = initRunCount()
    temp_stats = []
    temp = []

    # get list of traffic lights
    trafficLights = traci.trafficlights.getIDList()
    trafficLightsNumber = traci.trafficlights.getIDCount()

    # we set every light to phase 0
    for ID in trafficLights:
        traci.trafficlights.setPhase(ID, 0)
        initTrafficLight(ID)
        temp_stats.append(temp)

    phase_vector = 6*[None]
    curr_phase = trafficLightsNumber*[0]
    curr_time = 0
    db_step = 100
    avg_qL = 0
    avg_qL_curr = 0
    #temp_stats = []

    # execute the TraCI control loop
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        # current phase index number
        i = 0
        for ID in trafficLights:

            # get lanes for each traffic light
            lanes = traci.trafficlights.getControlledLanes(ID)
            lanes_uniq = []
            j = 0
            while j < len(lanes):
                if (j%2 == 0):
                    lanes_uniq.append(lanes[j])
                j+=1
            lanes = lanes_uniq


            # get average queue length for current time step
            queue_length=[]
            avg_qL_curr = 0
            for lane in lanes:
                queue_length.append(traci.lane.getLastStepHaltingNumber(lane))
                avg_qL_curr += traci.lane.getLastStepHaltingNumber(lane)
            avg_qL_curr = avg_qL_curr/(len(lanes)*1.0)


            # get average queue length till now
            avg_qL = (avg_qL*step + avg_qL_curr)/((step+1)*1.0)

            # run only for every db_step
            if (step%db_step == 0) :

                # generate current step's phase vector
                phase_vector[0] = int(round(max(queue_length[0], queue_length[1])/options.qlBracket))
                phase_vector[1] = int(round(max(queue_length[0], queue_length[5])/options.qlBracket))
                phase_vector[2] = int(round(max(queue_length[4], queue_length[5])/options.qlBracket))
                phase_vector[3] = int(round(max(queue_length[6], queue_length[7])/options.qlBracket))
                phase_vector[4] = int(round(max(queue_length[2], queue_length[6])/options.qlBracket))
                phase_vector[5] = int(round(max(queue_length[2], queue_length[3])/options.qlBracket))

                # print and save current stats
                print(avg_qL, avg_qL_curr, step)
                print(ID)
                temp_stats[int(ID)].append({"step": step,
                                            "curr_qL": avg_qL_curr,
                                            "avg_qL": avg_qL})

                nextAction = dbFunction(phase_vector, ID)
                if (nextAction == 1):
                    curr_phase[i] = (curr_phase[i] + 1)%6
                    traci.trafficlights.setPhase(ID, curr_phase[i])
                    curr_time = 1
                else :
                    curr_time += 1

            # incremetn current phase index
            i+=1
        step += 1

    print(avg_qL, "Final")
    saveStats(trafficLightsNumber, temp_stats)

    traci.close()
    sys.stdout.flush()

# this gets the input parameters specified to the program
def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    optParser.add_option("--cars", dest="numberCars", default=2000, metavar="NUM",
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
