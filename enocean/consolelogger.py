# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import logging


def init_logging(level=logging.DEBUG,logsize=1024,logcount=5):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger = logging.getLogger('enocean')
    logger.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = RotatingFileHandler('encoean.log', 'a',  logsize*1000 , logcount)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
