#!/usr/bin/env python
"""
@file    runner.py
@author  Lena Kalleske
@author  Daniel Krajzewicz
@author  Michael Behrisch
@author  Jakob Erdmann
@date    2009-03-26
@version $Id$

Tutorial for traffic light control via the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.dlr.de/
Copyright (C) 2009-2017 DLR/TS, Germany

This file is part of SUMO.
SUMO is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.
"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
from dbFunction import dbFunction, initPre
from globals import init

#from sharedFunctions import getEdgeFromLane

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

def generate_routefile():
    random.seed(42)  # make tests reproducible
    N = 250000 # number of time steps
    # demand per second from different directions

    pWE = 12. / 12
    pWN = 11. / 12
    pWS = 10. / 12
    pEW = 9. / 12
    pES = 8. / 12
    pEN = 7. / 12
    pSN = 6. / 12
    pSW = 5. / 12
    pSE = 4. / 12
    pNS = 3. / 12
    pNE = 2. / 12
    pNW = 1. / 12

    pA  = 1. /30
    pB  = 2. /30
    pC  = 3. /30

    with open("data/cross.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="typeA" accel="0.8" decel="4.5" sigma="0.8" length="5" minGap="2.5" maxSpeed="20" guiShape="passenger/sedan "/>
        <vType id="typeB" accel="0.8" decel="4.5" sigma="0.6" length="7" minGap="3" maxSpeed="25" guiShape="bus"/>
        <vType id="typeC" accel="0.8" decel="4.5" sigma="0.9" length="3" minGap="1" maxSpeed="15" guiShape="passenger/hatchback"/>

        <route id="right" edges="51o 1i 2o 52i" />
        <route id="right_up" edges="51o 1i 4o 54i" />
        <route id="right_down" edges="51o 1i 3o 53i" />


        <route id="left" edges="52o 2i 1o 51i" />
        <route id="left_down" edges="52o 2i 3o 53i" />
        <route id="left_up" edges="52o 2i 4o 54i" />

        <route id="up" edges="53o 3i 4o 54i" />
        <route id="up_left" edges="53o 3i 1o 51i" />
        <route id="up_right" edges="53o 3i 2o 52i" />

        <route id="down" edges="54o 4i 3o 53i" />
        <route id="down_left" edges="54o 4i 3o 53i" />
        <route id="down_right" edges="54o 4i 1o 51i" />""", file=routes)

        lastVeh = 0
        vehNr = 0
        t = "typeA"
        for I in range(N/4):
            i = I*4
            tR = random.uniform(0, 1)
            rR = random.uniform(0, 1)
            if tR < pA:
                t="typeA"
            elif tR < pB:
                t="typeB"
            else:
                t="typeC"

            if rR < pNW:
                print('    <vehicle id="down_right_%i" type="%s" route="down_right" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            elif rR < pNE:
                print('    <vehicle id="down_left_%i" type="%s" route="down_left" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            elif rR < pNS:
                print('    <vehicle id="down_%i" type="%s" route="down" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            elif rR < pSE:
                print('    <vehicle id="up_right_%i" type="%s" route="up_right" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            elif rR < pSW:
                print('    <vehicle id="up_left_%i" type="%s" route="up_left" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            elif rR < pSN:
                print('    <vehicle id="up_%i" type="%s" route="up" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            elif rR < pEN:
                print('    <vehicle id="left_up_%i" type="%s" route="left_up" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            elif rR < pES:
                print('    <vehicle id="left_down_%i" type="%s" route="left_down" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            elif rR < pEW:
                print('    <vehicle id="left_%i" type="%s" route="left" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            elif rR < pWS:
                print('    <vehicle id="right_down_%i" type="%s" route="right_down" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            elif rR < pWN:
                print('    <vehicle id="right_up_%i" type="%s" route="right_up" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            else:
                print('    <vehicle id="right_%i" type="%s" route="right" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
        print("</routes>", file=routes)


def run():
    """execute the TraCI control loop"""
    step = 0
    # we start with phase 2 where EW has green
    traci.trafficlights.setPhase("0", 0)

    phase_vector = 6*[None]
    curr_phase = traci.trafficlights.getPhase("0")
    curr_time = 0

    min_green = 10
    max_green = 120
    yellow = 5
    pre = 6*[0]
    preAction = 0
    db_step = 100
    avg_qL = 0
    avg_qL_curr = 0

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        edges=[]
        queue_length=[]

        lanes = traci.trafficlights.getControlledLanes("0")
        lanes_uniq = []

        i = 0;
        while i < len(lanes):
            if (i%2 == 0) :
                lanes_uniq.append(lanes[i])
            i+=1

        lanes = lanes_uniq

        avg_qL_curr = 0
        for lane in lanes:
            queue_length.append(traci.lane.getLastStepHaltingNumber(lane))
            avg_qL_curr += traci.lane.getLastStepHaltingNumber(lane)

        avg_qL_curr = avg_qL_curr/(len(lanes)*1.0)

        avg_qL = (avg_qL*step + avg_qL_curr)/((step+1)*1.0)

        phase_vector[0] = int(round(max(queue_length[0], queue_length[1])/15))
        phase_vector[1] = int(round(max(queue_length[0], queue_length[5])/15))
        phase_vector[2] = int(round(max(queue_length[4], queue_length[5])/15))
        phase_vector[3] = int(round(max(queue_length[6], queue_length[7])/15))
        phase_vector[4] = int(round(max(queue_length[2], queue_length[6])/15))
        phase_vector[5] = int(round(max(queue_length[2], queue_length[3])/15))

        if (step%db_step == 0) :
            print(avg_qL, avg_qL_curr, step)
            nextAction, pre, preAction = dbFunction(phase_vector, pre, preAction)
            if (nextAction == 1):
                curr_phase = (curr_phase + 1)%6
                traci.trafficlights.setPhase("0", curr_phase)
                curr_time = 1
            else :
                curr_time += 1
        step += 1

    print(avg_qL, "Final")

    traci.close()
    sys.stdout.flush()

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
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

    # first, generate the route file for this simulation
    generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                             "-n", "data/cross.net.xml",
                             "-a", "data/cross.add.xml",
                             "--queue-output", "queue.xml",
                             "--tripinfo-output", "tripinfo.xml"])
    init()
    initPre()
    run()
