# typical workflow
# 1. build docker image
#   make farmhub
# 2. save/export image
#   make farmhub save
# 3. upload image to S3
#   make farmhub sends3

# --force-rm \

biothings_farmhub:
	docker build \
    --build-arg BIOTHINGS_GIT_VERSION=release_manager \
    --build-arg STANDALONE_GIT_VERSION=master \
    --build-arg FARM_GIT_VERSION=master \
    --build-arg PROD=1 \
	-t biothings_farmhub:$$(git branch | grep ^\* | sed "s#\* ##") .

run:
	docker run --rm --name mvcgi -e "ES_HOST=su03:9200" -e "ES_INDEX_NAME=mvcgi" -p 7022:7022 -p 7080:7080 -d biothings_farmhub:$$(git branch | grep ^\* | sed "s#\* ##")

save:
	$(eval CONTAINER := $(firstword $(MAKECMDGOALS)))
	docker save $(CONTAINER):$$(git branch | grep ^\* | sed "s#\* ##") | xz > containers/$(CONTAINER)-$$(git branch | grep ^\* | sed "s#\* ##").docker.xz

sends3:
	$(eval CONTAINERFILE := $(firstword $(MAKECMDGOALS)))
	# must be some easier way...
	$(eval S3FOLDER := $(subst containers/,,$(CONTAINERFILE)))
	$(eval S3FOLDER := $(subst .docker,,$(S3FOLDER)))
	aws s3 cp containers/$(CONTAINERFILE)-$$(git branch | grep ^\* | sed "s#\* ##").docker.xz s3://biothings-containers/$(S3FOLDER)/

ec2docker:
	aws ec2 request-spot-instances --instance-count 1 --type one-time --spot-price 0.03 --launch-specification file://dockerspot.json --valid-until `date -d '+1 hour' +%FT%T%z`
	# then on ec2 instance, trigger a webhook
	# curl -vs -H "X-SpotIP: `curl http://instance-data/latest/meta-data/local-ipv4`" http://172.30.1.189:8080/generic-webhook-trigger/invoke
