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

network:
	docker network ls | grep biothings_farm || docker network create biothings_farm

run:
	docker run --network biothings_farm --rm --name rproxy -p 7080:7080 -d rproxy_farm:$$(git branch | grep ^\* | sed "s#\* ##")
	docker run --network biothings_farm --rm --name elastic -p 9200:9200 -d elastic_farm:$$(git branch | grep ^\* | sed "s#\* ##")

deploy: network download run


#hubid:= $(filter-out $@,$(MAKECMDGOALS)) # fetch farm hub id from command line
hub:
	$(eval FARM_HUB_ID := $(lastword $(MAKECMDGOALS)))
	@echo Starting container for Farm Hub $(FARM_HUB_ID)
	docker run --network biothings_farm --rm --name $(FARM_HUB_ID) -e ES_HOST=elastic:9200 -e ES_INDEX_NAME=$(FARM_HUB_ID) -e FARM_HUB_ID=$(FARM_HUB_ID) -d biothings_farmhub:$$(git branch | grep ^\* | sed "s#\* ##")

%:
	@: # catch arg to "hub" target and do nothing to prevent error message
