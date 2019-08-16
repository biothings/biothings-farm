How to setup/install biothings-farm infrastructure on AWS
#########################################################

Deploy the main network infrastructure and ec2 starting point
-------------------------------------------------------------

This first is done using CloudFormation. Use /aws/vpc_ec2/cloudformation_biothings-farm.template
template in CloudFormation to create a brand new infrastructure (from the very beginning,
including VPC creation)

Create NLB
----------
This step has to be done manually (I, Seb, tried to include that in CloudFormation but it fails with
some cryptic error about "Missing AllocationId property", while there's no such property described in the documentation.

Create a network load balancer, following this setup

image: create_nlb.png

Important: wait until the balancer is "active".

Create VPCLink
--------------

In API Gateway setup a VPCLink pointing the newly created NLB (it has to be active)
Follow this setup:

image: create_vpc.png

While until it's functional, note the VPC Link Id.

Create API
----------

Still in API gateway, create an API using the swagger file in aws/apigateway/biothings-farm-beta-swagger-apigateway.json.
First edit the file and replace "__vpclink__" by the VPC Link ID created in the previous step.

Then create the API using the swagger file.

Once created, deploy the API, create a new stage ("beta", "prod", ...).


Create a Cognito User Pool
--------------------------

TODO.

Initiate docker architecture
----------------------------

Create an EIP and assign it to biothings-farm-nat. SSH to that instance:

$ ssh -i ~/.ssh/biothings_farm.pem ec2-user@x.x.x.x

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

$ docker run --network biothings_farm --rm --name cgi -d demo_myvariant:master
$ docker ps

