# trafficRL

## Installation instructions to follow

### 1. Install SUMO:

  http://sumo.dlr.de/wiki/Downloads

### 2. Install MongoDB

Installation :
Follow the official instructions at:
  https://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/ (for ubuntu)
  https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/ (for windows)

Check mongo is installed by starting the server from the command line:

For Ubuntu:
    mongod

For Windows:
    "C:\Program Files\MongoDB\Server\3.4\bin\mongod.exe"

### 3. Install PyMongo using pip

    python -m pip install --user pymongo

### 4. Clone repository

Clone the project using git and cd into it:

    git clone https://github.com/codemerlin19/trafficRL.git

    cd trafficRL

### 5. Run project

    python runner.py

##### Usage: runner.py [options]:

      -h, --help          show this help message and exit
      --nogui             run the commandline version of sumo
      -C NUM, --cars=NUM  specify the number of cars generated for simulation
      --bracket=BRACKET   specify the number with which to partition the range of
                          queue length/cumulative delay
      --learning=NUM      specify learning method (1 = Q-Learning, 2 = SARSA)
      --state=NUM         specify traffic state representation to be used (1 =
                          Queue Length, 2 = Cumulative Delay)
      --phasing=NUM       specify phasing scheme (1 = Fixed Phasing, 2 = Variable
                          Phasing)
      --action=NUM        specify action selection method (1 = epsilon greedy, 2 =
                          softmax)

##### NOTE: Ensure that SUMO_HOME path is defined in environment variables
