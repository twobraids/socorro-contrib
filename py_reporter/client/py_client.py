import traceback

import json
import urllib2
import poster

from configman import Namespace, RequiredConfig
from configman.converters import class_converter
from configman.dotdict import DotDict

poster.streaminghttp.register_openers()

#==============================================================================
class CrashSubmitter(RequiredConfig):
    required_config = Namespace()
    required_config.add_option(
        'crash_submission_url',
        doc="The url of the Socorro collector to submit to",
        default="http://127.0.0.1:8882/submit"
    )

    #--------------------------------------------------------------------------
    def __init__(self, config, product_name, product_version):
        self.config = config
        self.product_name = product_name
        self.product_version = product_version

    #--------------------------------------------------------------------------
    def send_crash_report(self):
        raw_crash = DotDict()
        raw_crash.ProductName = self.product_name
        raw_crash.Version = self.product_version
        raw_crash.traceback = traceback.extract_tb(sys.exc_info()[2])
        datagen, headers = poster.encode.multipart_encode(raw_crash)
        request = urllib2.Request(
            self.config.url,
            datagen,
            headers
        )
        submission_response = urllib2.urlopen(request).read().strip()
