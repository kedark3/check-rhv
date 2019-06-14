import logging

from logging.config import fileConfig

# setup logger
fileConfig("/var/lib/shinken/libexec/rhv_logconf/logging_config.ini")
logger = logging.getLogger()
