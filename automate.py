import os
import sys
import optparse
import subprocess
import random
import globals
from helper import updateVehDistribution, generate_routefile
from runner import run_sim, get_options


def get_automate_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--cars", "-C", dest="numberCars", default=200000, metavar="NUM",
                         help="specify the number of cars generated for simulation")
    optParser.add_option("--seed", dest="seed", default=42, metavar="BRACKET",
                         help="specify the seed for random to so that results can be repeated")
    optParser.add_option("--start", dest="start", default=0, metavar="NUM",
                         help="specify the start index of the combinations to run")
    optParser.add_option("--end", dest="end", default=16, metavar="BRACKET",
                         help="specify the end index of the combinations to run")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    automate_options = get_automate_options()
    options = get_options()
    options.numberCars = automate_options.numberCars

    # give random a seed so that results are repeatable and same vehicle
    # distribution is generated for same seed
    random.seed(automate_options.seed)
    updateVehDistribution()

    automate_options.start = int(automate_options.start)
    automate_options.end = int(automate_options.end)

    # generate the route file for this simulation
    generate_routefile(options.numberCars)

    if (automate_options.start == 0):
        options.learn = '0'
        run_sim(0, "No learning", options)

    # Fixed Phasing
    options.phasing = '1'

    if (automate_options.start <= 1 and automate_options.end >= 1):
        options.stateRep = '1'
        options.learn = '1'
        options.actionSel = '1'
        run_sim(
            1,
            "Q-learning with state=queue and actSel=e-greedy FIXED",
            options)

    if (automate_options.start <= 2 and automate_options.end >= 2):
        options.stateRep = '1'
        options.learn = '1'
        options.actionSel = '2'
        run_sim(
            2,
            "Q-learning with state=queue and actSel=softmax FIXED",
            options)

    if (automate_options.start <= 3 and automate_options.end >= 3):
        options.stateRep = '1'
        options.learn = '2'
        options.actionSel = '1'
        run_sim(3, "SARSA with state=queue and actSel=e-greedy FIXED", options)

    if (automate_options.start <= 4 and automate_options.end >= 4):
        options.stateRep = '1'
        options.learn = '2'
        options.actionSel = '2'
        run_sim(4, "SARSA with state=queue and actSel=softmax FIXED", options)

    if (automate_options.start <= 5 and automate_options.end >= 5):
        options.stateRep = '2'
        options.learn = '1'
        options.actionSel = '1'
        run_sim(
            5,
            "Q-learning with state=delay and actSel=e-greedy FIXED",
            options)

    if (automate_options.start <= 6 and automate_options.end >= 6):
        options.stateRep = '2'
        options.learn = '1'
        options.actionSel = '2'
        run_sim(
            6,
            "Q-learning with state=delay and actSel=softmax FIXED",
            options)

    if (automate_options.start <= 7 and automate_options.end >= 7):
        options.stateRep = '2'
        options.learn = '2'
        options.actionSel = '1'
        run_sim(7, "SARSA with state=delay and actSel=e-greedy FIXED", options)

    if (automate_options.start <= 8 and automate_options.end >= 8):
        options.stateRep = '2'
        options.learn = '2'
        options.actionSel = '2'
        run_sim(8, "SARSA with state=delay and actSel=softmax FIXED", options)

    # Variable Phasing
    options.phasing = '2'
    globals.numActions = 6

    if (automate_options.start <= 9 and automate_options.end >= 9):
        options.stateRep = '1'
        options.learn = '1'
        options.actionSel = '1'
        run_sim(
            9,
            "Q-learning with state=queue and actSel=e-greedy VARIABLE",
            options)

    if (automate_options.start <= 10 and automate_options.end >= 10):
        options.stateRep = '1'
        options.learn = '1'
        options.actionSel = '2'
        run_sim(
            10,
            "Q-learning with state=queue and actSel=softmax VARIABLE",
            options)

    if (automate_options.start <= 11 and automate_options.end >= 11):
        options.stateRep = '1'
        options.learn = '2'
        options.actionSel = '1'
        run_sim(
            11,
            "SARSA with state=queue and actSel=e-greedy VARIABLE",
            options)

    if (automate_options.start <= 12 and automate_options.end >= 12):
        options.stateRep = '1'
        options.learn = '2'
        options.actionSel = '2'
        run_sim(
            12,
            "SARSA with state=queue and actSel=softmax VARIABLE",
            options)

    if (automate_options.start <= 13 and automate_options.end >= 13):
        options.stateRep = '2'
        options.learn = '1'
        options.actionSel = '1'
        run_sim(
            13,
            "Q-learning with state=delay and actSel=e-greedy VARIABLE",
            options)

    if (automate_options.start <= 14 and automate_options.end >= 14):
        options.stateRep = '2'
        options.learn = '1'
        options.actionSel = '2'
        run_sim(
            14,
            "Q-learning with state=delay and actSel=softmax VARIABLE",
            options)

    if (automate_options.start <= 15 and automate_options.end >= 15):
        options.stateRep = '2'
        options.learn = '2'
        options.actionSel = '1'
        run_sim(
            15,
            "SARSA with state=delay and actSel=e-greedy VARIABLE",
            options)

    if (automate_options.start <= 16 and automate_options.end >= 16):
        options.stateRep = '2'
        options.learn = '2'
        options.actionSel = '2'
        run_sim(
            16,
            "SARSA with state=delay and actSel=softmax VARIABLE",
            options)
