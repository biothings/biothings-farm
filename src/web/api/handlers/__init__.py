"""
The following handlers act as proxy over usual Biothings web handlers. The goal
is to share an API app over multiple indices. As a consequence, all handlers expect
the first argument to be an index name.
"""

from biothings.web.api.es.handlers.base_handler import BaseESRequestHandler
from biothings.web.api.es.handlers.metadata_handler import MetadataHandler
from biothings.web.api.es.handlers import QueryHandler
from biothings.web.api.es.handlers import BiothingHandler

class BaseSharedESRequestHandler(BaseESRequestHandler):

    # doc type per index, cache
    DOC_TYPES = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.index = None

    def check_and_set(self, index, doc_type):
        self.index = index
        self.doc_type = self.get_doc_type()
        if doc_type:
            assert self.doc_type == doc_type, "Document type in mapping doesn't match query"

    def get_doc_type(self):
        assert self.index
        if self.index in self.__class__.DOC_TYPES:
            return self.__class__.DOC_TYPES[self.index]
        # explore mapping to fetch doc type
        mapping = list(self.web_settings.es_client.indices.get_mapping(index=self.index)
                       .values())[0]["mappings"]
        doc_type = list(mapping.keys())[0]
        self.__class__.DOC_TYPES[self.index] = doc_type
        return doc_type

    def _get_es_doc_type(self, options):
        doc_type = self.get_doc_type()
        return doc_type

    def _get_es_index(self, options):
        assert self.index
        return self.index


class SharedBiothingHandler(BaseSharedESRequestHandler,BiothingHandler):

    def get(self, index, doc_type, bid, **kwargs):
        self.check_and_set(index,doc_type)
        super().get(bid)

    def post(self, index, doc_type, ids=None, **kwargs):
        self.check_and_set(index,doc_type)
        super().post(ids)


class SharedMetadataHandler(BaseSharedESRequestHandler, MetadataHandler):

    def get(self, index):
        self.index = index
        super().get()


class SharedQueryHandler(BaseSharedESRequestHandler, QueryHandler):

    def get(self, index):
        self.check_and_set(index,doc_type=None)
        super().get()

    def post(self, index):
        self.check_and_set(index,doc_type=None)
        super().post()


