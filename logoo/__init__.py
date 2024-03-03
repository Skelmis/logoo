import logging
from collections import namedtuple

from .logger import Logger
from .primary_logger import PrimaryLogger

__version__ = "1.0.0"
VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")
version_info = VersionInfo(major=1, minor=0, micro=0, releaselevel="final", serial=0)
logging.getLogger(__name__).addHandler(logging.NullHandler())
