# trafficRL

## Installation instructions to follow (for Ubuntu)

### 1. Install SUMO:

  http://sumo.dlr.de/wiki/Downloads

### 2. Install MongoDB

Installation :
Follow the official instructions at:
  https://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/

Check mongo is installed by starting the server:

    mongod

### 3. Install PyMongo using pip

    python -m pip install --user pymongo

### 4. Clone repository

Clone the project using git and cd into it:

    git clone https://github.com/codemerlin19/trafficRL.git

    cd trafficRL

### 5. Run project

    python runner.py

##### NOTE: Ensure that SUMO_HOME path is defined in environment variables
