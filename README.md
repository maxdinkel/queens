# QUEENS #

This repository is contains the python version of the QUEENS framework.

[![build status](https://gitlab.lrz.de/jbi/queens/badges/master/build.svg)](https://gitlab.lrz.de/jbi/queens/commits/master)

[![coverage report](https://gitlab.lrz.de/jbi/queens/badges/master/coverage.svg)](https://codecov.io/bitbucket/jbi35/pqueens/commit/6c9c94b0e6e8f6c2b5aad07b34e69c72a4d1edce)

## Dependencies
All necessary third party libraries are listed in the requirements.txt file.
To install all of these dependencies using pip, simply run:   
`pip install -r requirements.txt`


## Installation directions
The use a virtual environment like [Anaconda](https://www.continuum.io/downloads) is highly recommended.
After setting up Anaconda and a new, dedicated QUEENS development environment via
`conda create -n <name_of_new_environment> python=3.6`   
, all required third party libraries can be simply installed by running:  
`pip install -r requirements.txt`  
Next, if Anaconda is used, QUEENS can be installed using:     
`/Applications/anaconda/envs/<your-environment-name>/bin/python setup.py develop`   
If you encounter any problems try using the --user flag.

Otherwise the command is simply:  
`python setup.py develop`

To uninstall QUEENS run:  
`python setup.py develop --uninstall`

To update Python packages in your Anaconda environment type:  
`conda update --all`

### Setup of MongoDB
QUEENS writes results into a MongoDB database, therefore QUEENS needs to have write access to a MongoDB databases. However, MongoDB does not necessarily have to run on the same machine as QUEENS. In certain situations, it makes sense to have the database running on a different computer and connect to the database via port-forwarding.

#### Installation of MongoDB
Installation instructions if you are running OSX can be found [here](https://docs.mongodb.com/master/tutorial/install-mongodb-on-os-x/?_ga=2.181134695.1149150790.1494232459-1730069423.1494232449)  
Installation instructions for LNM workstations running Fedora 22 are as follows.
https://blog.bensoer.com/install-mongodb-3-0-on-fedora-22/   

#### Starting MongoDB
After installation, you need to start MongoDB. For LNM machines this requires that you can execute the commands:   
`systemctl start mongod`   

`systemctl stop mongod`   

`systemctl restart`

It could be that you have to edit the sudoers file `/etc/sudoers.d/` together with your administrator in order get the execution rights.

On a Mac you have to run
`mongod --dbpath <path_to_your_database>`

#### LNM specific issues
In order to connect to a MongoDB instance running on one of the LNM machines, one needs to be able to connect port 27017 from a remote host.
By default,  the fire wall software `firewalld` blocks every incoming request. Hence, to enable a connections, we have add so called rules to firewalld in order to connect to the database.   

First type   
`sudo firewall-cmd --list-all`   
to see what firewall rules are already in place.
If there is no rule in place which allows you to connect to port 27017, you can add such a rule by running the following command on the machine MongoDD is running on.   
`sudo firewall-cmd --zone=work --add-rich-rule 'rule family=ipv4 source address=<adress-you-want-to-connnect-to>port port=27017 protocol=tcp accept' --permanent`   
Note that if you want to connect to the database from a cluster, you will also need to add this rule to the clusters master node.
Also, to apply the changes run
`sudo firewall-cmd --reload`  

### some IP-adresses
Cauchy:129.187.58.39
Schmarrn:129.187.58.24
Jonas Laptop:129.187.58.120

#### QUEENS and cluster jobs on Kaiser
QUEENS offers the possibility to perform the actual model evaluations on a HPC-cluster
such as Kaiser. Setting things up is unfortunately not really as straightforward as it could be yet. However, the following steps can be used as guidance to set up QUEENS such that QUEENS is running on one machine, the MongoDB is running on a second machine and the model evaluations are performed on a third machine, in this case Kaiser.
To avoid confusion, these three machine will be referred to as
- localhost (Local machine running QUEENS)
- db_server  (machine running MongoDB, e.g., Cauchy)
- compute machine (HPC-cluster, e.g., Kaiser)   

in the following.

##### Preparing the compute machine
First we have to install some software on the compute cluster. The following steps
are tried and tested on the LNM Kaiser system. It is not guaranteed that the steps
will be the same on other systems

1. Install miniconda3 with python 3.6 on Kaiser
2. Add public ssh-key of Kaiser to LRZ GitLab repo in order to be able to clone it from Kaiser
3. Clone this repo
4. Install requirements and QUEENS using pip on Kaiser

##### Preparing the db_server
The machine running the MongoDB database does not need to be the same as either the
machine running QUEENS or the compute cluster. However, the other machines need to be
able to connect to the MongoDB via tcp in order to write data. For that to work
within the LNM network, all of the machines need to be connected to the internal network.

1. Install MongoDB. If you are using CentOS, a nice guide can be found
[here](https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-centos-7).
2. Make sure you can connect to the database from the computer running QUEENS.
This usually entails two steps.
  1. Open the respective ports in the firewall and allowing both localhost and the
  compute machine to connect to the db_server. This can be achieved by adding
  rich-rules to firewalld using firewall-cmd as described above.
  2. Edit the MongoDB config file such that it allows connections from anywhere
  (probably not the safest option, but ok for now). If you followed the standard
  installation instructions, you should edit the config file using   
  `sudo vim /etc/mongod.conf`  
  And comment out the `bindIp` like shown   
  ```shell
  # network interfaces
   net:
   port: 27017
   # bindIp: 127.0.0.1  <- comment out this line
   ```   

##### Preparing localhost
1. Install QUEENS
2. Activate ssh-port-forwarding so that you can connect to the compute machines
 without having to enter your password. To learn more about how ssh port forwarding
 work click [here](https://chamibuddhika.wordpress.com/2012/03/21/ssh-tunnelling-explained/).
 Without explanation of all the details, here is an example. Assuming the compute machine is Kaiser
 and the db_server is cauchy, you have to run the following command on your localhost to
 set up ssh port forwarding  
 `ssh -fN -L 9001:kaiser.lnm.mw.tum.de:22 biehler@cauchy.lnm.mw.tum.de`   
 To see if port forwarding works type  
 `ssh -p 9001 biehler@localhost`  
 to connect to Kaiser.   
 Connecting via ssh to the compute machine needs to work without having to type your
 password. This can be achieved by copying your ssh key from localhost to kaiser.
 Depending on your system, you need to locate the file with the ssh keys. On my mac I can
 activate passwordless ssh to Kaiser by running the following   
`cat .ssh/id_rsa.pub | ssh biehler@kaiser 'cat >> .ssh/authorized_keys'`   
 The easiest way to disable ssh port forwarding is to run   
 `killall ssh`  
 Beware, this kills all ssh processes not just the port forwarding one.


## Building the documentation
QUEENS uses sphinx to automatically build a html documentation from  docstring.
To build it, navigate into the doc folder and type:    
`make html`  

After adding new modules or classes to QUEENS, one needs to rebuild the autodoc index by running:    
`sphinx-apidoc -o doc/source pqueens -f`  
before the make command.

## Run the test suite
QUEENS has a couple of unit and regression test. To run the test suite type:  
`python -m unittest discover pqueens/tests`

In order to get a detailed report showing code coverage etc., the test have to be run using the coverage tool. This is triggered by running the using:    
`coverage run -m unittest discover -s pqueens/tests`  

To view the created report, run:  
`coverage report -m`


## Run the Bitbucket pipeline locally
It is possible to test Bitbucket pipelines locally on your machine using
Docker containers. The main purpose of this is to be able to try and test
the Bitbucket pipeline as well as the overall bitbucket setup locally on
your machine. This can help to fix differences between test results obtained
locally and results obtained online in the bitbucket repository. Testing
things locally in a Docker container matching the bitbucket setup repository
is often very helpful speeds up the debugging process considerably.  

Bitbuckets own documentation about how to test the pipelines locally
can be found
[here](https://confluence.atlassian.com/bitbucket/debug-your-pipelines-locally-with-docker-838273569.html)

In any case, the steps are fairly straightforward:  

- If [Docker](https://www.docker.com/) is not already installed, install Docker on your machine
   by following these [instructions](https://www.docker.com/docker-mac)
- Copy the QUEENS code to a dedicated testing directory, e.g.,
  `/Users/jonas/work/adco/test_bibucket_pipeline_locally/pqueens`
- Run the following command to launch a Docker container with a Debian based Anaconda image and the source code from testing directory mounted as local folder in the Docker container:  
```shell
docker run -it --volume=/Users/jonas/work/adco/test_bibucket_pipeline_locally/pqueens:/localDebugRepo
--workdir="/localDebugRepo" --memory=4g --memory-swap=4g  
--entrypoint=/bin/bash continuumio/anaconda3
```
- You should now be in the docker container and inside the queens directory
- Setup QUEENS following the instructions above
- From here, you can now run the individual commands in your pipeline.


## GitLab
To get started with Gitlab checkout the help section [here](https://gitlab.lrz.de/help/ci/README.md)

CI with with gitlab requires the setup of so called runners that build and test the code.
To turn a machine into a runner, you have to install some software as described
[here](https://docs.gitlab.com/runner/install/linux-repository.html)
As of 02/2018 the steps are as follows:  
1. For RHEL/CentOS/Fedora run  
`curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm. h | sudo bash`
2. To install run:
`sudo yum install gitlab-runner`


Next, you have to register the runner with your gitlab repo as described
[here](https://docs.gitlab.com/runner/register/index.html)


## Anaconda tips and tricks
1. Create new anaconda environment
`conda create -n <name_of_new_environment> python=3.6`  
2. List all packages linked into an anaconda environment
`conda list -n <your_environment_name`
3. Activate environment
`source activate <your_environment_name>
