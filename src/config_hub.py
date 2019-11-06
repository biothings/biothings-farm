#- invisible -#
HUB_DB_BACKEND = {
        "module" : "biothings.utils.sqlite3",
        "sqlite_db_folder" : "./db"
        }
#- invisible -#
DATA_HUB_DB_DATABASE = "hubdb"
#- invisible -#
EVENT_COLLECTION = "event"
#- invisible -#
DATA_SRC_DUMP_COLLECTION = 'src_dump'
#- invisible -#
DATA_SRC_MASTER_COLLECTION = 'src_master'
#- invisible -#
DATA_SRC_BUILD_COLLECTION = 'src_build'
#- invisible -#
CMD_COLLECTION = 'cmd'

import os
from biothings.utils.loggers import setup_default_log
#- invisible -#
LOGGER_NAME = "hub"
#- invisible -#
DATA_ARCHIVE_ROOT = "/data/farmhub"
#- invisible -#
LOG_FOLDER = os.path.join(DATA_ARCHIVE_ROOT,"logs")
logger = setup_default_log(LOGGER_NAME, LOG_FOLDER)

#* Job Manager *#
#- readonly-#
HUB_MAX_WORKERS = int(os.cpu_count() / 4)
#* Job Manager *#
#- readonly-#
HUB_MAX_THREADS = HUB_MAX_WORKERS
#* Job Manager *#
#- readonly-#
HUB_MAX_MEM_USAGE = None
#* Job Manager *#
#- readonly-#
MAX_QUEUED_JOBS = 10

#- invisible -#
RUN_DIR = '/data/run'

#- invisible -#
DATA_SRC_DATABASE = ''
#- invisible -#
DATA_SRC_SERVER = ''
#- invisible -#
DATA_SRC_PORT = None

#* Data releases *#
# List of URLs pointing to versions.json. When data release is published
# a file named versions.json is created and updated for each publications.
# It contains all available releases and represents the entry point to access
# data releases.
VERSION_URLS = []

from biothings import ConfigurationError

#- invisible -#
ES_HOST = os.environ.get("ES_HOST",ConfigurationError("Define ElasticSearch host where release data is updated"))
#- invisible -#
# placeholder
ES_DOC_TYPE = None

#* Credentials *#
# AWS access and secret keys to access S3 buckets (if not public)
STANDALONE_AWS_CREDENTIALS = {
        "AWS_ACCESS_KEY_ID" : None,
        "AWS_SECRET_ACCESS_KEY" : None,
        }
#- invisible -#
HUB_SSH_PORT = 7022
#- invisible -#
HUB_API_PORT = 7080
#- invisible -#
HUB_PASSWD = {"guest":"9RKfd8gDuNf0Q"}
# Farm Hub ID: unique amongst all the biothings farm nodes
# Used to set container hostname, api gateway uses it to forward request
# to proper reverse proxy, etc.. it has to be unique
#- invisible -#
FARM_HUB_ID = os.environ.get("FARM_HUB_ID",ConfigurationError("Define farm hub unique ID"))
# base URL serving snapshot repo type "url"
#- invisible -#
BASE_REPOSITORY_URL = "http://%s:8080" % FARM_HUB_ID

#* *#
# By default, a sanity check is performed to make sure hub is running
# versions compatible with these declared in data releases. Set to true
# to skip this check (not recommanded)
SKIP_CHECK_COMPAT = False

#* General *#
# BioThings Hub's name displayed at the top
HUB_NAME = "BioThings Hub"
# URL to icon representing this BioThings Hub
HUB_ICON = "https://biothings.io/static/img/biothings-studio-color.svg"

#- invisible -#
# This "hard-codes" which ES host and index this hub can deal with
# it's not, and should *not* be made  editable.
STANDALONE_CONFIG = {
        "_default" : {
            "es_host" : ES_HOST,
            "index" : FARM_HUB_ID, # docker hostname == index name, restricting access
            }
        }

CONFIG_READONLY = False
