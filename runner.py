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
    N = 3600  # number of time steps
    # demand per second from different directions

    pWE = 1. / 8
    pWN = 1. / 16
    pWS = 1. / 24
    pEW = 1. / 32
    pES = 1. / 40
    pEN = 1. / 48
    pSN = 1. / 56
    pSW = 1. / 64
    pSE = 1. / 72
    pNS = 1. / 80
    pNE = 1. / 88
    pNW = 1. / 96

    pA  = 1. /30
    pB  = 2. /30
    pC  = 1. /10
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
        for i in range(N):
            if random.uniform(0, 1) < pA:
                t="typeA"
            elif random.uniform(0, 1) < pB:
                t="typeB"
            else:
                t="typeC"
                
            if random.uniform(0, 1) < pNW:
                print('    <vehicle id="down_right_%i" type="%s" route="down_right" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pNE:
                print('    <vehicle id="down_left_%i" type="%s" route="down_left" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pNS:
                print('    <vehicle id="down_%i" type="%s" route="down" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pSE:
                print('    <vehicle id="up_right_%i" type="%s" route="up_right" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pSW:
                print('    <vehicle id="up_left_%i" type="%s" route="up_left" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pSN:
                print('    <vehicle id="up_%i" type="%s" route="up" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pEN:
                print('    <vehicle id="left_up_%i" type="%s" route="left_up" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pES:
                print('    <vehicle id="left_down_%i" type="%s" route="left_down" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pEW:
                print('    <vehicle id="left_%i" type="%s" route="left" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pWS:
                print('    <vehicle id="right_down_%i" type="%s" route="right_down" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pWN:
                print('    <vehicle id="right_up_%i" type="%s" route="right_up" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pWE:
                print('    <vehicle id="right_%i" type="%s" route="right" depart="%i" />' % (
                    vehNr, t, i), file=routes)
                vehNr += 1
                lastVeh = i   
        print("</routes>", file=routes)

# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#        <phase duration="31" state="GrGr"/>
#        <phase duration="6"  state="yryr"/>
#        <phase duration="31" state="rGrG"/>
#        <phase duration="6"  state="ryry"/>
#    </tlLogic>


def run():
    """execute the TraCI control loop"""
    step = 0
    # we start with phase 2 where EW has green
    traci.trafficlights.setPhase("0", 2)

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        # if traci.trafficlights.getPhase("0") == 2:
        #     # we are not already switching
        #     if traci.inductionloop.getLastStepVehicleNumber("0") > 0:
        #         # there is a vehicle from the north, switch
        #         traci.trafficlights.setPhase("0", 3)
        #     else:
        #         # otherwise try to keep green for EW
        #         traci.trafficlights.setPhase("0", 2)
        edges=[]
        queue_length=[]
        #num_vehicles= traci.edge.getLastStepVehicleNumber("1i")
        #print ("number of vehicles on 1st edge = " , num_vehicles ,"\n")
        #halting_vehicles=traci.edge.getLastStepHaltingNumber("1i")
        #print ("number of halting vehicles on 1st edge = " , halting_vehicles ,"\n" )
        #mean_length=traci.edge.getLastStepLength("1i")
        #print ("mean length of vehicles on 1st edge = " , mean_length ,"\n")
        lanes = traci.trafficlights.getControlledLanes("0")
        print(lanes)
        i=0;
        while i<len(lanes):
                edges.append(traci.lane.getEdgeID(lanes[i]))
                i+=4
        #edge= traci.lane.getEdgeID(lane)
        print (edges)
        for edge in edges:
            queue_length.append(traci.edge.getLastStepHaltingNumber(edge))
        print(queue_length,"\n")
        step += 1
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
    run()
