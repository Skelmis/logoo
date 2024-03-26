import logging
from collections import namedtuple

from .logger import Logger
from .primary_logger import PrimaryLogger

__version__ = "1.2.1"
VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")
version_info = VersionInfo(major=1, minor=2, micro=1, releaselevel="final", serial=0)
logging.getLogger(__name__).addHandler(logging.NullHandler())
