# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json

from configman import Namespace, RequiredConfig
from configman.converters import class_converter

from socorro.lib.util import DotDict
from socorro.lib.datetimeutil import utc_now


#==============================================================================
class PyCrashProcessor(RequiredConfig):
    def __init__(self, config, quit_check_callback=None):
        super(PyCrashProcessor, self).__init__()
        self.config = config
        if quit_check_callback:
            self.quit_check = quit_check_callback
        else:
            self.quit_check = lambda: False

    @staticmethod
    def method_parts(traceback):
        for file_name, line_number, method, text in traceback:
            yield method

    def _create_minimal_processed_crash(self):
        processed_crash = DotDict()
        processed_crash.addons = None
        processed_crash.addons_checked = None
        processed_crash.additional_minidumps = []
        processed_crash.address = None
        processed_crash.app_notes = None
        processed_crash.build = None
        processed_crash.client_crash_date = None
        processed_crash.completeddatetime = None
        processed_crash.cpu_info = None
        processed_crash.cpu_name = None
        processed_crash.crashedThread = None
        processed_crash.date_processed = None
        processed_crash.distributor = None
        processed_crash.distributor_version = None
        processed_crash.email = None
        processed_crash.exploitability = None
        processed_crash.flash_version = None
        #processed_crash.flash_process_dump = None  # anticiptation of future
        processed_crash.hangid = None
        processed_crash.install_age = None
        processed_crash.last_crash = None
        processed_crash.os_name = None
        processed_crash.os_version = None
        processed_crash.pluginFilename = None
        processed_crash.pluginName = None
        processed_crash.pluginVersion = None
        processed_crash.processor_notes = ''
        processed_crash.process_type = None
        processed_crash.product = None
        processed_crash.reason = None
        processed_crash.release_channel = None
        processed_crash.signature = 'EMPTY: crash failed to process'
        processed_crash.startedDateTime = None
        processed_crash.success = False
        processed_crash.topmost_filenames = ''
        processed_crash.truncated = None
        processed_crash.uptime = None
        processed_crash.user_comments = None
        processed_crash.user_id = None
        processed_crash.url = None
        processed_crash.uuid = None
        processed_crash.version = None
        processed_crash.Winsock_LSP = None
        return processed_crash

    #--------------------------------------------------------------------------
    def convert_raw_crash_to_processed_crash(self, raw_crash, raw_dumps):
        started_datetime = self._log_job_start(raw_crash.uuid)
        processed_crash = self._create_minimal_processed_crash()
        processed_crash.uuid = raw_crash.uuid
        processed_crash.startedDateTime = started_datetime
        processor_notes = ['pyprocessor 2013']
        try:
            raw_dump = json.loads(raw_crash.raw_dump)
            environment = json.loads(raw_crash.environment)
            processed_crash.signature = \
                ' | '.join(self.method_parts(raw_dump['stack']))

            processed_crash.date_processed = raw_crash.submitted_timestamp
            processed_crash.client_crash_date = raw_crash.client_crash_date
            processed_crash.cpu_info = environment.machine
            processed_crash.cpu_name = environment.processor
            processed_crash.crashedThread = raw_dump.crashedThread
            processed_crash.os_name = environment.system
            processed_crash.os_version = environment.release
            processed_crash.product = raw_crash.ProductName
            processed_crash.reason = raw_dump.exception_str
            processed_crash.version = raw_crash.Version

            processed_crash.success = True
        except Exception, x:
            processor_notes.append(str(x))
            self.config.logger.debug('error in processing', exc_info=True)
        processed_crash.processor_notes = '; '.join(processor_notes)
        processed_crash.completeddatetime = utc_now()
        self._log_job_end(processed_crash.success, raw_crash.uuid)
        return processed_crash

    #--------------------------------------------------------------------------
    def reject_raw_crash(self, crash_id, reason):
        self._log_job_start(crash_id)
        self.config.logger.warning('%s rejected: %s', crash_id, reason)
        self._log_job_end(False, crash_id)

    #--------------------------------------------------------------------------
    def _log_job_start(self, crash_id):
        self.config.logger.info("starting job: %s", crash_id)
        started_datetime = utc_now()
        return started_datetime

    #--------------------------------------------------------------------------
    def _log_job_end(self, success, crash_id):
        self.config.logger.info(
            "finishing %s job: %s",
            'successful' if success else 'failed',
            crash_id
        )

