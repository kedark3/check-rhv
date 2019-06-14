import logging

from logging.config import fileConfig

# setup logger
fileConfig("rhv_logconf/logging_config.ini")
logger = logging.getLogger()