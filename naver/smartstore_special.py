#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2020. 5. 20.

@author: user
'''
import json
import time
import random
import os, datetime,re, signal
from datetime import date, timedelta

import bs4
import queue
import sys
import warnings
import requests
import datetime
from urllib import parse

import log as Log;  Log.Init()
from app import config
from app import define_mall as __DEFINE__


from util import Util as __UTIL__

from api import hiadone_api as __API__

from model.ProductData import ProductData
from mall.Mall import Mall
from naver.smartstore import smartstore

if not sys.warnoptions:
    warnings.simplefilter("ignore")

           

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))
		

	#BRD_ID_LIST = ['140','141','161','126','190', '281','288','294','297','302','225','229','257','258','266','269','247','314','331']

	#BRD_ID_LIST = ['331'] -- item 1
	BRD_ID_LIST = [ '281']


	
	app = smartstore()

	for brd_id in BRD_ID_LIST :
		if(app.SHUTDOWN) : break
		app_url = __API__.get_storelist_by_brd_id(brd_id)
		__LOG__.Trace('%s : %s' % (app_url, str(brd_id ) ) )
		app.main(app_url, int(brd_id))

