# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

class VersionIdentifier(object):
  main = 0
  beta = 0
  alpha = 0
  build = 0

class VersionInfo(object):
  app_version: VersionIdentifier = VersionIdentifier()
  api_version: VersionIdentifier = VersionIdentifier()
  chip_id: 0
  chip_version = 0
  app_description = ''