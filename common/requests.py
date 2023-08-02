import requests
import logging

from common import logger

log = logger.getLogger()
default_retries = 3


def post(retries=default_retries, *args, **kwargs):
    try:
        res = requests.post(*args, **kwargs)
        return res
    except Exception as e:
        log.error(e)


def get(retries=default_retries, *args, **kwargs):
    try:
        res = requests.get(*args, **kwargs)
        return res
    except Exception as e:
        log.error(e)


def delete(retries=default_retries, *args, **kwargs):
    try:
        res = requests.delete(*args, **kwargs)
        return res
    except Exception as e:
        log.error(e)
