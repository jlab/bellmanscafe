# Bellman's Café

Link to website: http://bellmanscafe.jlab.bio/

## Requirements
1. github account
2. ...




## Setup to run the website on your local computer

### 1. Required operating system: Ubuntu 20.04.3 (Linux)

### 2. Install the following packages: <br>
`sudo apt-get update` <br>
1. python 3.8 and python3-pip <br>
`sudo apt-get install python3.8 python3-pip` <br>
2. Flask  <br>
`sudo pip install flask==2.0.3` <br>

### 3. Install the following repositorys via SSH:
Make sure the ADP_collection is at the same folder level as bellmanscafe 
1. bellmanscafe (https://github.com/jlab/bellmanscafe) <br>
`git clone git@github.com:jlab/bellmanscafe.git`
2. ADP_collection (https://github.com/jlab/ADP_collection) <br>
`git clone git@github.com:jlab/ADP_collection.git`


After the environment has been set up, the following directory structure is required in order for bellmanscafe to work correctly:
```
project-dir
├── bellmanscafe
├── ADP_collection (User provided)
│   ├── irgendeinfile


```


### 4. run pull_and_copy_ADP_collection.sh <br>
navigate to the file pull_and_copy_ADP_collection.sh in bellmanscafe and execute it. <br>
`bash ./pull_and_copy_ADP_collection.sh`

### 5. Install gapc
**gapc** is the the compiler used for calculating the results on the webside therofore it has to be installed.

One possibility is to create a conda environement (via mamba) to use gapc: <br>
`conda create -n gapc_env` <br>
`conda install -c bioconda -c anaconda -c conda-forge bellmans-gapc`

(you can also follow the instructions on the gapc git webside: https://github.com/jlab/gapc) <br>


### 6. Start the webside localy: 
1. activate conda environment gapc_env <br>
`conda activate gapc_env`
2. run Bellmansgap.py <br>
`python3 Bellmansgap.py` 
3. click on the the link in your terminal to open the webite in the browser. <br>
http://127.0.0.1:5000/




## Server information the website is currently running on:

Operating system: Ubuntu 20.04.3 <br>
IP-address 134.176.31.227 <br>

The following packages were installed via apt/apt-get (except flask, which was installed via pip3):

1. git 2.25.1
2. python3 3.8.10
3. pip 20.0.2 (Python 3.8)
4. flask 2.0.3 (pip3)
5. nginx 1.18.0
6. gunicorn 20.0.4





## Updating changes of the website on the server

### Requirements
1. BCF account <br>
username: first letter of your first name plus your last name
2. Activation of BCF account for Bellman's Café access by admin (usually S. Janssen) - send e-mail

### 1. SSH to server
1. ssh lummerland <br>
https://dokuwiki.computational.bio.uni-giessen.de/doku.php?id=system:beginners:remoteaccess <br>

2. For first time access do the following: <br>
- ssh username:@134.176.31.227
- set a password
- create a new ssh key
- copy the public key to the .ssh/ directory ON THE SERVER
- save the public key as "authorized_keys" in the same directory

**you should have 2 different files containing the same public key**

2. When logging in after that do: <br>
- ssh  bellmanscafe


### 2. Updating the repositories and gapc
#### 2.1 Manually 
1. `cd ~/bellmanscafe`
2. kill the gunicorn pprocesses <br>
`sudo pkill -f gunicorn`
3. pull bellmanscafe and ADP_collection
4. restart website <br>
`gunicorn --workers=9 Bellmansgap:app --daemon`
5. check if website works
6. if not ooptional try <br>
`gunicorn --workers=9 Bellmansgap:app`

#### 2.2 automatically via cronjob
1. `cd ~\bellmanscafe`
2. `crontab -e`
3. open an editor
4. paste: `45 11 * * * /bin/bash /home/username/bellmanscafe/pull_and_copy_ADP_collection.sh`


## Setup new server hosting the bellmanscap website

### 1. SSH to bellmanscafe
ssh to the bellmanscafe server as shown above.

### 2. Install the packages named above

### 3. start the website


## FRAGE: 
- muss jeder User das Git Repo neu clonen? Oder gibt es einen Ordner auf den alle Zugriff haben?

