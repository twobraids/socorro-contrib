# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from configman import Namespace, RequiredConfig
from configman.converters import class_converter

from socorro.database.transaction_executor import TransactionExecutor


#==============================================================================
class PyNewCrashSource(RequiredConfig):
    """ """
    required_config = Namespace()
    required_config.add_option(
        'crashstorage_class',
        doc='the source storage class',
        default=None,
        from_string_converter=class_converter
    )

    #--------------------------------------------------------------------------
    def __init__(self, config, processor_name, quit_check_callback=None):
        self.config = config
        self.source = config.crashstorage_class(config, quit_check_callback)

    #--------------------------------------------------------------------------
    def close(self):
        self.source.close()

    #--------------------------------------------------------------------------
    def __iter__(self):
        """an adapter that allows this class can serve as an iterator in a
        fetch_transform_save app"""
        for crash_id in self.source.new_crashes():
            if crash_id:
                yield crash_id
            else:
                yield None

    #--------------------------------------------------------------------------
    def __call__(self):
        return self.__iter__()

