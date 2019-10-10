#!/usr/bin/env python

import sys, os, logging
# shut some mouths...
import botocore
logging.getLogger("elasticsearch").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("tornado").setLevel(logging.ERROR)
logging.getLogger("botocore").setLevel(logging.ERROR)

import config, biothings
from biothings.utils.version import set_versions
from standalone.utils.version import set_standalone_version

# sanity check, making sure farm hub is properly restricted to
# ES host, index, etc...
assert config.ES_HOST, "ES_HOST must be set"
assert config.ES_INDEX_NAME, "ES_INDEX_NAME must be set"
assert config.FARM_HUB_ID, "FARM_HUB_ID must be set"

# fill app & autohub versions
set_versions(config,"..")
set_standalone_version(config,"standalone")
biothings.config_for_app(config)
# now use biothings' config wrapper
config = biothings.config
logging.info("Hub DB backend: %s" % config.HUB_DB_BACKEND)
logging.info("Hub database: %s" % config.DATA_HUB_DB_DATABASE)

from hub import FarmHubServer

server = FarmHubServer(config.VERSION_URLS,source_list=None,name="Farm Hub",
                       api_config=None,dataupload_config=False,websocket_config=False)


if __name__ == "__main__":
        server.start()

