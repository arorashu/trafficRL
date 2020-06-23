# Traffic Reinforcement Learning (RL)

## Run

### Setup

1. Install SUMO: <http://sumo.dlr.de/wiki/Downloads>

1. Install MongoDB: Follow the official instructions at:

    <https://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/> (for ubuntu)
    <https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/> (for windows)

    Check mongo is installed by starting the server from the command line:

    For Ubuntu:
        `mongod`

    For Windows:
        `C:\Program Files\MongoDB\Server\3.4\bin\mongod.exe`

1. Clone the project using git and cd into it:

        ```sh
        git clone https://github.com/codemerlin19/trafficRL.git

        cd trafficRL
        ```

1. (Optionally) Install Virtual Env

        ```sh
        pip3 install virtualenv
        virtualenv .venv
        source .venv/bin/activate
        ```

1. Install requirements

        ```sh
        pip3 install -r requirements.txt
        ```

1. Run project

        ```sh
        python runner.py
        ```

### Usage: runner.py [options]

    ```sh
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
    ```

##### NOTE: Ensure that SUMO_HOME path is defined in environment variables

## Uses

### [SUMO](https://github.com/eclipse/sumo)

Last tested with Eclipse SUMO Version 1.6.0.

- [Traci](https://sumo.dlr.de/docs/TraCI.html)

## Development

### Linting

For auto fixes use `autopep8`:

        ```sh
        python -m pip install autopep8
        autopep8 --in-place --aggressive  --exclude "__pycache__,.venv"  ./*.py
        ```
