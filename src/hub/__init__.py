from standalone.hub import AutoHubServer
from hub.uploader import FarmBioThingsUploader

class FarmHubServer(AutoHubServer):

    DEFAULT_UPLOADER_CLASS = FarmBioThingsUploader
