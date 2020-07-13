# -*- coding: utf-8 -*-

import configparser


__REAL__ = True

__DEBUG__ = True

# 설정
APP_NAME = "HIADONE"
APP_BASIC_PATH = '/root/%s' % (APP_NAME)

APP_BIN_PATH = '%s/bin' % (APP_NAME)
IMAGE_PATH = '%s/images/' % (APP_BASIC_PATH)
DOWNLOAD_PATH = '%s/download' % (APP_BASIC_PATH)
LOG_PATH = '%s/LOG' % (APP_BASIC_PATH)
DATA_PATH = '%s/DATA' % (APP_BASIC_PATH)

# 크롬드라이브 path
CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'
	
