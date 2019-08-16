How to setup/install biothings-farm infrastructure on AWS
#########################################################

Deploy the main network infrastructure and ec2 starting point
-------------------------------------------------------------
This first is done using CloudFormation. Use /aws/cloudformation/cloudformation_biothings-farm.template
template in CloudFormation to create a brand new infrastructure (from the very beginning,
including VPC creation)

Note: you can also use Makefile:

$ make create-infra
(and delete-infra will delete everything, no question asked, you've been warned)


Create a Cognito User Pool
--------------------------
TODO.


Create API
----------
A CloudFormation template will create the API with the endpoints, a beta stage and then will deploy that stage
as a functional/reachable API.

First retrieve the VPCLink Id from previous step, go to CloudFormation webapp, stack "biothings-farm", "Outputs". Copy the value,
and create a environment variable

$ export VPCLINKID=<value>

Then run the makefile

$ make create-api



Initiate docker architecture
----------------------------
Create an EIP and assign it to biothings-farm-entry. SSH to that instance:

$ scp -i ~/.ssh/biothings_farm.pem ~/.ssh/biothings_farm.pem alpine@34.218.144.73:
$ ssh -i ~/.ssh/biothings_farm.pem alpine@x.x.x.x
$ mv biothings_farm.pem .ssh/
$ chmod 400 .ssh/biothings_farm.pem

Then ssh to biothings-farm-node1 instance, using private IP (there's no public IP, on purpose, that's why we use the NAT instance)

$ ssh -i ~/.ssh/biothings_farm.pem ubuntu@10.x.x.x

Create a dedicated docker network if it doesn't exist (important to have name resolution between containers)

$ docker network ls
$ docker network create biothings_farm

Run a reverse-proxy instance in that network, exposing 80:

$ docker images | grep btfarm-proxy
$ docker run --network biothings_farm --rm --name rproxy -p 80:80 -d btfarm-proxy
$ docker ps

For testing purpose, we can start a studio inside the network to check if the reverse-proxy forwards request from the api gateway
Don't expose any ports, all goes through rproxy

$ docker run --network biothings_farm --rm --name cgi -d biothings_studio:0.1f
$ docker ps

Check reverse proxy container can access it by hostname and check connectivity

$ docker exec -ti rproxy /bin/bash
# ping cgi
PING cgi (172.19.0.3) 56(84) bytes of data.
64 bytes from cgi.biothings_farm (172.19.0.3): icmp_seq=1 ttl=64 time=0.075 ms
64 bytes from cgi.biothings_farm (172.19.0.3): icmp_seq=2 ttl=64 time=0.068 ms
 ...

# curl cgi:7080 # direct access
{"result":{"name":"BioThings Studio","biothings_version":{"branch":"0.3.x","commit":"eb69f1","date":"2019-08-07T08:00:09-07:00"},"app_version":{"branch":"0.1f","commit":"4fb893","date":"2019-06-28T10:09:52-07:00"},"icon":null,"now":"2019-08-16T21:01:53.604Z"},"status":"ok"}
# curl localhost/farm/cgi # through nginx rules
{"result":{"name":"BioThings Studio","biothings_version":{"branch":"0.3.x","commit":"eb69f1","date":"2019-08-07T08:00:09-07:00"},"app_version":{"branch":"0.1f","commit":"4fb893","date":"2019-06-28T10:09:52-07:00"},"icon":null,"now":"2019-08-16T21:01:53.604Z"},"status":"ok"}
# exit
$ $ curl localhost/farm/cgi # from exposed port, outside of container
{"result":{"name":"BioThings Studio","biothings_version":{"branch":"0.3.x","commit":"eb69f1","date":"2019-08-07T08:00:09-07:00"},"app_version":{"branch":"0.1f","commit":"4fb893","date":"2019-06-28T10:09:52-07:00"},"icon":null,"now":"2019-08-16T21:04:38.172Z"},"status":"ok"}


