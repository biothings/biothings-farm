# -*- coding: utf-8 -*-
# Simple template example used to instantiate a new biothing API
from biothings.web.index_base import main, options
from web.settings import GenericFarmWebSettings

# Instantiate settings class to configure biothings web
web_settings = GenericFarmWebSettings(config='config')

if __name__ == '__main__':
    # set debug level on app settings
    web_settings.set_debug_level(options.debug)
    app_list = web_settings.generate_app_list()
    main(app_list, debug_settings={"debug": True},sentry_client_key=None)
