import logging
import os

from logging.config import fileConfig


# setup logger
def get_logger(local):
    if local:
        fileConfig(os.getcwd() + "/rhv_logconf/local_config.ini")
    else:
        fileConfig("/var/lib/shinken/libexec/check-rhv/rhv_logconf/logging_config.ini")
    return logging.getLogger()
