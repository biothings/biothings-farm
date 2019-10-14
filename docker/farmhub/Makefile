# typical workflow
# 1. build docker image
#   make farmhub
# 2. save/export image
#   make farmhub save
# 3. upload image to S3
#   make farmhub sends3

biothings_farmhub:
	docker build \
    --build-arg BIOTHINGS_GIT_VERSION=release_manager \
    --build-arg STANDALONE_GIT_VERSION=master \
    --build-arg FARM_GIT_VERSION=master \
    --build-arg PROD=1 \
	-t biothings_farmhub:$$(git branch | grep ^\* | sed "s#\* ##") .

run:
	docker run --network biothings_farm --rm --name cgi -e ES_HOST=elastic:9200 -e FARM_HUB_ID=cgi -d biothings_farmhub:$$(git branch | grep ^\* | sed "s#\* ##")

save:
	$(eval CONTAINER := $(firstword $(MAKECMDGOALS)))
	docker save $(CONTAINER):$$(git branch | grep ^\* | sed "s#\* ##") | xz > containers/$(CONTAINER)-$$(git branch | grep ^\* | sed "s#\* ##").docker.xz

sends3:
	$(eval CONTAINERFILE := $(firstword $(MAKECMDGOALS)))
	# must be some easier way...
	$(eval S3FOLDER := $(subst containers/,,$(CONTAINERFILE)))
	$(eval S3FOLDER := $(subst .docker,,$(S3FOLDER)))
	aws s3 cp containers/$(CONTAINERFILE)-$$(git branch | grep ^\* | sed "s#\* ##").docker.xz s3://biothings-containers/biothings_farm/
