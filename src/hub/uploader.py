from pprint import pformat

from biothings.hub.autoupdate import BiothingsUploader
from biothings import config


class FarmBioThingsUploader(BiothingsUploader):

    def get_snapshot_repository_config(self, build_meta):
        """
        Return repo name and config, following this exception when hub runs in a farm:

        For security reasons, we don't allow type "s3" repo in the farm, as we would need
        to store access/secret keys in the repo config (or in keystore, which would complicate
        things even more). Since ES cluster is shared, we want to mitigate risks of having such
        keys exposed somewhow.

        That's why snapshot are first created locally on the hub data is prepared, using
        type "fs" repo. An archive is then created containing local snapshot folders and is
        uploaded to S3. The archive URL is part of the metadata, while the repo type settings
        is still "fs" when snapshot is published.

        When we want to deploy data, we need to download the archive and change the repo type:
        if we keep type "fs" is means we need to send the data to the ES cluster, which means
        farm hub needs more privileges, which we want to minimize. Instead of type "fs", we
        switch to type "url", where the URL uses http protocol, while a web server located on
        the farm hub serves this data. That way, it's the ES cluster initiating data retrieval,
        restoring snapshot from data located on the farm hub.
        """
        repo_name, repo_settings = list(build_meta["metadata"]["repository"].items())[0]
        # only "fs" type is expected, with an "archive_url", just to make sure we're in the context
        # described in the docstring section
        if not (repo_settings["type"] == "fs" and "archive_url" in build_meta["metadata"]):
            raise ValueError("In farm hubs, expecting repo type 'fs' with 'archive_url', " + \
                    "can't allow to create repository using config %s" % pformat(repo_settings))
        # replace setting with type "url"
        location = repo_settings["settings"]["location"]
        # web server serves location DATA_ARCHIVE_ROOT folder
        # in this folder, we have api_name/version/<files>
        # and we expect the snapshot archive has been uncompressed there
        # ex:
        # - /data/farmhub/mygene/20191009/20191009.json # this is the release metadata
        # - /data/farmhub/mygene/20191009/snapshot/* # this is the uncompressed folder containing ES snapshot data
        # generate URL:
        # - twice location, because first is the S3 folder containing the json metadata file
        #   and second is coming from archiving the snapshot folder (see bt.h.datarelease.publisher/step_archive())
        # - trailing "/" important, otherwise ES removes it and can't find snapshot data)
        location = location.strip("/")
        snapshot_url = ("/".join([config.BASE_REPOSITORY_URL,location,location]) + "/")
        repo_settings = {"type" : "url", "settings" : {"url" : snapshot_url}}
        self.logger.debug("Repository settings is now: %s" % pformat(repo_settings))

        return  (repo_name,repo_settings)
