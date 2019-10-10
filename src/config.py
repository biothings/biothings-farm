from config_hub import *
import os

# These params are set through "docker run" using environment vars (-e)

ES_INDEX_NAME = os.environ.get("ES_INDEX_NAME")
ES_HOST = os.environ.get("ES_HOST")

# Farm Hub ID: unique amongst all the biothings farm nodes
# Used to set container hostname, api gateway uses it to forward request
# to proper reverse proxy, etc.. it has to be unique
#- invisible -#
FARM_HUB_ID = os.environ.get("FARM_HUB_ID")
