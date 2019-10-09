from config_hub import *
import os

# These params are set through "docker run" using environment vars (-e)

ES_INDEX_NAME = os.environ.get("ES_INDEX_NAME")
ES_HOST = os.environ.get("ES_HOST")
