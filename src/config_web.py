import os
from biothings.web.settings.default import *
from web.api.handlers import SharedBiothingHandler, SharedMetadataHandler, \
                             SharedQueryHandler

ES_HOST = os.environ["ES_HOST"]

# All path are prefixed by the Farm Hub ID, ie. index name
#- invisible -#
APP_LIST = [
    (r"/(.+)/metadata/?", SharedMetadataHandler),
    (r"/(.+)/metadata/fields/?", SharedMetadataHandler),
    (r"/(.+)/query/?", SharedQueryHandler), # it could match BiothingHandler is doc_type == "query"
    (r"/(.+)/(.+)/(.+)/?", SharedBiothingHandler), # for GET
    (r"/(.+)/(.+)/?$", SharedBiothingHandler), # for POST
]
