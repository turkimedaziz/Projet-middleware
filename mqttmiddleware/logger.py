import logging
import os
from datetime import datetime
from django.conf import settings

LOG_FILE = os.path.join(settings.LOG_DIR, 'middleware.log')

def setup_logger():
    logger = logging.getLogger('mqttmiddleware')
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = logging.FileHandler(LOG_FILE)
        fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger
