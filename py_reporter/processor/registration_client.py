# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import socket
from datetime import datetime
from collections import defaultdict

from configman import Namespace, RequiredConfig
from configman.converters import class_converter, timedelta_converter


#==============================================================================
class RegistrationError(Exception):
    """the exception used when there is a problem within registration"""
    pass


#==============================================================================
class ProcessorAppRegistrationClient(RequiredConfig):
    def __init__(self, config, quit_check_callback=None):
        self.config = config
        self.processor_name = "%s:%d" % (socket.gethostname(), os.getpid())

    #--------------------------------------------------------------------------
    def checkin(self):
        pass

    #--------------------------------------------------------------------------
    def unregister(self):
        pass
