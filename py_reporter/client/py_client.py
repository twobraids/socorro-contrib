import traceback
import os
import sys
import threading
import platform
import datetime

import json
import urllib2
import poster

from configman import Namespace, RequiredConfig
from configman.converters import py_obj_to_str

from socorro.lib.util import DotDict
from socorro.lib.datetimeutil import utc_now

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

    @staticmethod
    def _preprocess_traceback():
        raw_dump = DotDict()
        exc_info = sys.exc_info()
        raw_dump.exception_class = py_obj_to_str(exc_info[0])
        raw_dump.exception_str = str(exc_info[1])
        raw_dump.stack = traceback.extract_tb(exc_info[2])
        raw_dump_str = json.dumps(raw_dump)
        return raw_dump_str

    #--------------------------------------------------------------------------
    def send_crash_report(self):
        raw_crash = DotDict()
        raw_crash.ProductName = self.product_name
        raw_crash.Version = self.product_version
        raw_crash.raw_dump = self._preprocess_traceback()
        raw_crash.crashedThread = threading.currentThread().name
        raw_crash.client_crash_date = utc_now()
        raw_crash.python_version = platform.python_version()
        raw_crash.platform = platform.platform()
        raw_crash.architecture = platform.architecture()
        for key, value in os.environ.iteritems():
            raw_crash[key] = value
        datagen, headers = poster.encode.multipart_encode(raw_crash)
        request = urllib2.Request(
            self.config.crash_submission_url,
            datagen,
            headers
        )
        submission_response = urllib2.urlopen(request).read().strip()
