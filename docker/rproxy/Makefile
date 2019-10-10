# typical workflow
# 1. build docker image
#   make rproxy_farm
# 2. save/export image
#   make rproxy_farm save
# 3. upload image to S3
#   make rproxy_farm sends3

rproxy_farm:
	docker build -t rproxy_farm:$$(git branch | grep ^\* | sed "s#\* ##") .

run:
	docker run --network biothings_farm --rm --name reverse_proxy -p 80:80 -d rproxy_farm:$$(git branch | grep ^\* | sed "s#\* ##")

save:
	$(eval CONTAINER := $(firstword $(MAKECMDGOALS)))
	docker save $(CONTAINER):$$(git branch | grep ^\* | sed "s#\* ##") | xz > containers/$(CONTAINER)-$$(git branch | grep ^\* | sed "s#\* ##").docker.xz

sends3:
	$(eval CONTAINERFILE := $(firstword $(MAKECMDGOALS)))
	# must be some easier way...
	$(eval S3FOLDER := $(subst containers/,,$(CONTAINERFILE)))
	$(eval S3FOLDER := $(subst .docker,,$(S3FOLDER)))
	aws s3 cp containers/$(CONTAINERFILE)-$$(git branch | grep ^\* | sed "s#\* ##").docker.xz s3://biothings-containers/biothings_farm/

