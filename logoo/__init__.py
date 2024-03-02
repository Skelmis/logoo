import logging

from .logger import Logger
from .primary_logger import PrimaryLogger

logging.getLogger(__name__).addHandler(logging.NullHandler())
