# creating images
build:
	cd farmhub && make biothings_farmhub
	cd elastic && make elastic_farm
	cd rproxy && make rproxy_farm

save:
	cd farmhub && make biothings_farmhub save
	cd elastic && make elastic_farm save
	cd rproxy && make rproxy_farm save

sends3:
	cd farmhub && make biothings_farmhub sends3
	cd elastic && make elastic_farm sends3
	cd rproxy && make rproxy_farm sends3


# deploying images

download:
	wget https://biothings-containers.s3-us-west-2.amazonaws.com/biothings_farm/rproxy_farm-$$(git branch | grep ^\* | sed "s#\* ##").docker.xz -O - | unxz - | docker load
	wget https://biothings-containers.s3-us-west-2.amazonaws.com/biothings_farm/elastic_farm-$$(git branch | grep ^\* | sed "s#\* ##").docker.xz -O - | unxz - | docker load
	wget https://biothings-containers.s3-us-west-2.amazonaws.com/biothings_farm/biothings_farmhub-$$(git branch | grep ^\* | sed "s#\* ##").docker.xz -O - | unxz - | docker load
	wget https://biothings-containers.s3-us-west-2.amazonaws.com/biothings_farm/biothings_farmapi-$$(git branch | grep ^\* | sed "s#\* ##").docker.xz -O - | unxz - | docker load

network:
	docker network ls | grep biothings_farm || docker network create biothings_farm

run:
	docker run --network biothings_farm --rm --name rproxy -p 7080:7080 -d rproxy_farm:$$(git branch | grep ^\* | sed "s#\* ##")
	docker run --network biothings_farm --rm --name elastic -p 9200:9200 -d elastic_farm:$$(git branch | grep ^\* | sed "s#\* ##")
	docker run --network biothings_farm --rm --name farmapi -p 8000:8000 -e ES_HOST=elastic:9200 -d biothings_farmapi:$$(git branch | grep ^\* | sed "s#\* ##")

deploy: network download run


#hubid:= $(filter-out $@,$(MAKECMDGOALS)) # fetch farm hub id from command line
hub:
	$(eval FARM_HUB_ID := $(lastword $(MAKECMDGOALS)))
	@echo Starting container for Farm Hub $(FARM_HUB_ID)
	docker run --network biothings_farm --rm --name $(FARM_HUB_ID) -e ES_HOST=elastic:9200 -e FARM_HUB_ID=$(FARM_HUB_ID) -d biothings_farmhub:$$(git branch | grep ^\* | sed "s#\* ##")

create-user:
	$(eval EMAIL := $(lastword $(MAKECMDGOALS)))
	@echo Creating user $(EMAIL)
	aws cognito-idp admin-create-user --user-pool-id us-west-2_KAglRSC16 --username $(EMAIL) --user-attributes=Name=name,Value=$(EMAIL)

get-user:
	$(eval EMAIL := $(lastword $(MAKECMDGOALS)))
	aws cognito-idp admin-get-user --user-pool-id us-west-2_KAglRSC16 --username $(EMAIL)

# then admin adds custom attributes: biothings api name (= farm hub id). Comma separated for multiple
# $ aws cognito-idp admin-update-user-attributes --user-pool-id us-west-2_KAglRSC16 --username $(EMAIL) --user-attributes="Name=custom:biothings-api-name,Value=cgi"
# then user needs to update password (temp password is received by email)
# $ aws cognito-idp initiate-auth --auth-flow USER_PASSWORD_AUTH --client-id 668qr87fc875enqadve7o4fno7 --auth-parameters "USERNAME=$(EMAIL),PASSWORD=thepassword"
# cognito wants us to change password, we respond to the challenge
# $ aws cognito-idp respond-to-auth-challenge --client-id 668qr87fc875enqadve7o4fno7 --challenge-name NEW_PASSWORD_REQUIRED --challenge-responses NEW_PASSWORD=thenewpassword,USERNAME=$(EMAIL) --session "token"
# we also need to confirm email
# $ aws cognito-idp admin-update-user-attributes --user-pool-id us-west-2_KAglRSC16 --username $(EMAIL) --user-attributes Name=email_verified,Value=true
# each time we need a token for this user:
# $ aws cognito-idp initiate-auth --auth-flow USER_PASSWORD_AUTH --client-id 668qr87fc875enqadve7o4fno7 --auth-parameters "USERNAME=$(EMAIL),PASSWORD=thenewpassword"

%:
	@: # catch arg to "hub" target and do nothing to prevent error message

