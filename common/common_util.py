# coding: utf-8

import yaml
import json
import inspect
import os
import sys
import uuid
from importlib import import_module
from robot.running.builder import TestSuiteBuilder, ResourceFileBuilder
from robot.running.context import EXECUTION_CONTEXTS


def get_global_vars(filepath):
    '''
    :param filepath: absolute path to the current file
    :return: var dict
    '''
    if not os.path.isfile(filepath):
        raise TypeError('filepath must be a file!')
    dirname, filename = os.path.split(filepath)
    sys.path.append(dirname)
    name = filename.split('.')[0]
    m = import_module(name)
    var = {}
    for key in dir(m):
        value = getattr(m, key)
        if key.startswith('_'):
            continue
        elif (
            inspect.ismodule(value) or inspect.isclass(value)
            or inspect.isgenerator(value) or inspect.isgenerator(value)
            or inspect.isfunction(value) or inspect.isbuiltin(value)
            or inspect.ismethod(value) or inspect.isfunction(value)
        ):
            continue
        else:
            var[key] = value
    del m
    sys.path.remove(dirname)
    return var


def get_mac():
    return uuid.UUID(int=uuid.getnode()).hex[-12:]


def gen_uuid():
    mac = get_mac()
    pid = os.getpid()
    name = '%s:%s' % (mac, pid)
    return uuid.uuid3(uuid.NAMESPACE_OID, name).hex


def get_user_keywords(resource):
    assert os.path.isfile(resource), '{} not a file!'.format(resource)
    rs = ResourceFileBuilder().build(resource)
    return rs.keywords
