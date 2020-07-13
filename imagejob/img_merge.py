#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user
'''

import uuid
import os
import sys, signal
import warnings
import requests
import urllib.request
import urllib
from bs4 import BeautifulSoup
from PIL import Image as PILImage
import PIL
import httplib2
from app import config
import log as Log;  Log.Init()


if not sys.warnoptions:
    warnings.simplefilter("ignore")

'''
##########################################################
#
# 이미지 다운로드시 사용 되는 requests 의 header 내용
# 	- 이미지 서버가 HTTP-2 사용시 urllib.request.urlretrieve을 사용하여 이미지 다운로드 불가
# 	- Header 값에 Referer 값에 따라서 응답메시지가 달라짐.
#
##########################################################
'''	
def get_header(url):
	
	tmp_url_list = url.split('//')
	url_list = tmp_url_list[1].split('/')
	
	header = { 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' , \
		'Accept-Encoding': 'gzip, deflate' , \
		'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6' , \
		'Cache-Control': 'no-cache' , \
		'Connection': 'keep-alive' , \
		'Host': url_list[0] , \
		'Pragma': 'no-cache' , \
		'Upgrade-Insecure-Requests': '1' , \
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36' } 
		
	return header

'''
##########################################################
#
# 이미지 압축 함수
# 	- 이미지 Size에 따른 사이즈 조정
# 	- 이미지 컬리티를 85 로 조정
#
# image : 원본 PIL 이미지 데이터
# infile : 압축하여 저장하는 파일명
##########################################################
'''	
def compress_image(image, infile):
	'''
	size = 1920, 1080
	width = 1920
	height = 1080
	'''
	size = 1000, 5000
	width = 1000
	height = 5000


	if image.size[0] > width and image.size[1] > height:
		image.thumbnail(size, PILImage.ANTIALIAS)
		image.save(infile, quality=85)
		
	elif image.size[0] > width:
		wpercent = (width/float(image.size[0]))
		height = int((float(image.size[1])*float(wpercent)))
		image = image.resize((width,height), PILImage.ANTIALIAS)
		image.save(infile,quality=85)
		
	elif image.size[1] > height:
		wpercent = (height/float(image.size[1]))
		width = int((float(image.size[0])*float(wpercent)))
		image = image.resize((width,height), PILImage.ANTIALIAS)
		image.save(infile, quality=85)
		
	else:
		image.save(infile, quality=85)
		
'''
##########################################################
#
# 이미지 변환 함수
# 	- 다양한 이미지 종류를 JPG 형식으로 변환하여 이미지를 저장함.
# 	- 이미지 컬리티를 85 로 조정
#
# org_img_name : 원본 이미지 파일명
# rtn_img_name : 이미지 변환된 파일명
##########################################################
'''	
def change_img_format( org_img_name ) :
	rtn = False
	try :

		rtn_img_name = '%s%s.jpg' % ( config.IMAGE_PATH, uuid.uuid4() )
		
		with PILImage.open( org_img_name ) as im:
			try :
				#__LOG__.Trace( im.format )
				if im.format == "JPEG":
					image = im.convert('RGB')
					compress_image(image, rtn_img_name)

				elif im.format == "GIF":
					i = im.convert("RGBA")
					bg = PILImage.new("RGB", i.size)
					image = PILImage.composite(i, bg, i)
					compress_image(image, rtn_img_name)

				elif im.format == "PNG":
					try:
						image = PILImage.new("RGB", im.size, (255,255,255))
						image.paste(im,im)
						compress_image(image, rtn_img_name)
						
					except ValueError:
						image = im.convert('RGB')
						compress_image(image, rtn_img_name)

				elif im.format == "BMP":
					image = im.convert('RGB')
					compress_image(image, rtn_img_name)
				else :
					image = im.convert('RGB')
					compress_image(image, rtn_img_name)
				rtn = True
				
			except :
				pass
				
			im.close()

		
	except Exception as ex:
		__LOG__.Trace('에러 : change_img_format')
		__LOG__.Error( ex )
		pass

	return rtn , rtn_img_name
	
'''
##########################################################
#
# 이미지 파일 한개를 다운로드 하는 함수
#
# img_url : 이미지 URL
##########################################################
'''		
def get_single_img( img_url ) :
	rtn = False
	rtn_img_name = ''
	img_name = ''

	try :

		img_name = config.IMAGE_PATH + os.path.basename(img_url)
		filename, fileExtension = os.path.splitext(img_name)
		img_name = '%s%s%s' % ( config.IMAGE_PATH, uuid.uuid4(), fileExtension )

		if(img_name.count('http') == 0 ) and ( (0 == fileExtension.lower().find('.jpg')) or (0 == fileExtension.lower().find('.jpeg')) or (0 == fileExtension.lower().find('.png')) or (0 == fileExtension.lower().find('.gif')) ) :
			
			# 이미지 URL 변경 및 다운로드
			decode_url = urllib.parse.unquote(img_url)
			img_data = requests.get(decode_url, headers=get_header(decode_url)).content
			with open(img_name, 'wb') as f:
				f.write(img_data)
				
			# 이미지 사이즈 및 포맷 변경
			rtn , rtn_img_name = change_img_format( img_name )
				
			if(rtn) : __LOG__.Trace('성공 : 이미지 다운로드 : %s' % (img_url) )
			else : __LOG__.Trace('실패 : 이미지 다운로드 : %s' % (img_url) )
			
			# 변환 전 이미지 삭제 
			remove_img(img_name)
			
	except Exception as ex:
		if(config.__DEBUG__) : __LOG__.Trace('실패 : 이미지 다운로드 : %s' % (img_url) )
		__LOG__.Error( ex )
		if(rtn_img_name != '') : remove_img(rtn_img_name)
		if(img_name != '') : remove_img(img_name)
		
		pass
	
	
	return rtn , rtn_img_name



'''
##########################################################
#
# 여러개의 이미지 URL에서 이미지를 다운로드 받아서,
# 하나의 통합 이미지 생성 함수 
#
# image_url_list : 이미지 URL 리스트
# save_img_path : 통합이미지 파일명
#
#
# 제한 사항 : 
#	- 통합 이미지 생성시, 65500 픽셀 이상은 생성할수 없음.
# 	- 65500 픽셀이상일때 해당 이미지는 제외하고 통합이미지 생성시
#
##########################################################
'''	

def get_merge_img( image_url_list) :
	rtn = False
	
	save_img_path = '%s%s.jpg' % ( config.IMAGE_PATH, uuid.uuid4() )
	image_list = []
	full_width, full_height = 0, 0
	try :
		for img_url in image_url_list :
			try :
				__LOG__.Trace( img_url )
				rtn , rtn_img_name = get_single_img( img_url )
				if(rtn) :
					im = PILImage.open(rtn_img_name)
					width, height = im.size
					if( ( full_height + height ) < 65500 ) : 
						image_list.append(im)
						full_width = max(full_width, width)
						full_height += height
						
					remove_img(rtn_img_name)

			except Exception as ex :
				__LOG__.Error( "실패 - get_single_img")
				__LOG__.Error( ex )
				pass
		
		#__LOG__.Trace(' full_width, full_height - %d : %d' % (full_width, full_height) )
		
		if(full_width != 0 ) :
			canvas = None
			canvas = PILImage.new('RGB', (full_width, full_height), 'white')
			output_height = 0

			for im in image_list:
				try :
					width, height = im.size
					canvas.paste(im, (0, output_height))
					output_height += height
					#__LOG__.Trace(' output_height , height- %d : %d' % (output_height , height ) )
				except :
					pass
			 
			canvas.save(save_img_path)
			
			if(config.__DEBUG__) : __LOG__.Trace('통합 이미지 생성 : %s' % (save_img_path) )
			rtn = True
		
	except Exception as exb:
		__LOG__.Error( "실패 - 통합 이미지 생성 : %s" % (save_img_path) )
		__LOG__.Error( exb )
		pass
	
	
	return rtn , save_img_path



'''
##########################################################
#
# 이미지 파일 삭제 함수
#
##########################################################
'''
def remove_img(img_path):
	try :
	
		if os.path.isfile(img_path): 
			os.remove(img_path)

	except Exception as ex :  
		__LOG__.Error(ex)            
		pass

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))

	#img_url_list = 'http://cocochien.img9.kr/ALLINONE/leopard%2001.jpg'
	
	img_url_list = ['https://shop-phinf.pstatic.net/20200319_166/1584585904602o7Mp0_JPEG/%25B4%25BA%25C6%25AE%25B8%25AE_%25BB%25F3%25BC%25BC_1.jpg', \
					'https://shop-phinf.pstatic.net/20200319_258/1584585930647aVAzw_JPEG/%25B4%25BA%25C6%25AE2.jpg', \
					'https://shop-phinf.pstatic.net/20200319_131/1584585739095DUrmF_JPEG/%25B4%25BA%25C6%25AE3.jpg', \
					'https://shop-phinf.pstatic.net/20200311_58/1583908903271ocO8j_JPEG/DOG-%25BD%25BA%25B8%25F4%25BA%25EA%25B8%25AE%25B5%25E5.jpg', \
					'https://shop-phinf.pstatic.net/20200311_122/1583908903241MqQMc_JPEG/DOG-%25BF%25C0%25BC%25C7%25C7%25C7%25BD%25AC.jpg', \
					'https://shop-phinf.pstatic.net/20200311_188/1583908903241qF5iA_JPEG/DOG-%25C4%25A1%25C5%25B2%25C4%25A5%25B8%25E9%25C1%25B6.jpg', \
					'https://shop-phinf.pstatic.net/20170323_67/heedong00_1490256350357dGI0L_JPEG/1.jpg', \
					'https://shop-phinf.pstatic.net/20170323_56/heedong00_1490256350776H6XGY_JPEG/KakaoTalk_20170323_145747922.jpg', \
					'https://shop-phinf.pstatic.net/20170323_299/heedong00_1490256350993fkL9w_JPEG/2.jpg', \
					'https://shop-phinf.pstatic.net/20170323_178/heedong00_1490256351277qqrCO_JPEG/18.jpg', \
					'https://shop-phinf.pstatic.net/20170323_163/heedong00_1490256351533pMRAp_JPEG/15.jpg', \
					'https://shop-phinf.pstatic.net/20170323_89/heedong00_1490256352038x5kWv_JPEG/12.jpg', \
					'https://shop-phinf.pstatic.net/20170323_96/heedong00_14902563522784By3R_JPEG/16.jpg', \
					'https://shop-phinf.pstatic.net/20170323_84/heedong00_1490256352502o8Bh0_JPEG/3.jpg', \
					'https://shop-phinf.pstatic.net/20170323_216/heedong00_149025635276821RIK_JPEG/KakaoTalk_20170323_145747521.jpg', \
					'https://shop-phinf.pstatic.net/20170323_102/heedong00_1490256353038b8C8x_JPEG/14.jpg', \
					'https://shop-phinf.pstatic.net/20170323_2/heedong00_14902563533149c1wO_JPEG/13.jpg', \
					'https://shop-phinf.pstatic.net/20170323_26/heedong00_14902563535770amr0_JPEG/17.jpg', \
					'https://shop-phinf.pstatic.net/20170323_155/heedong00_1490256353819oTtAf_JPEG/10.jpg', \
					'https://shop-phinf.pstatic.net/20170323_251/heedong00_1490256354224PTQMk_JPEG/7.jpg', \
					'https://shop-phinf.pstatic.net/20170323_70/heedong00_1490256354535ng5dL_JPEG/11.jpg', \
					'https://shop-phinf.pstatic.net/20170323_197/heedong00_1490256354823XOvXR_JPEG/8.jpg', \
					'https://shop-phinf.pstatic.net/20170323_94/heedong00_1490256355111iaLQ0_JPEG/5.jpg', \
					'https://shop-phinf.pstatic.net/20170323_72/heedong00_1490256355408RgtWE_JPEG/6.jpg', \
					'https://shop-phinf.pstatic.net/20170323_89/heedong00_1490256355716KL2wQ_JPEG/4.jpg', \
					'https://shop-phinf.pstatic.net/20170323_60/heedong00_1490257504112mW19K_PNG/%25B4%25EB%25B1%25B8.png', \
					'https://shop-phinf.pstatic.net/20170323_270/heedong00_1490257504571nGe92_PNG/%25C6%25DB%25BD%25C3%25C7%25C8.png', \
					'https://shop-phinf.pstatic.net/20180228_188/500114562_1519788750343wKc9w_JPEG/%25C7%25C1%25B7%25B9%25C0%25CC%25C1%25AE%25B9%25EB%25B8%25AE_%25BE%25EE%25B4%25FA%25C6%25AE.jpg', \
					'https://shop-phinf.pstatic.net/20180928_157/500114562_1538118683770AjAh4_JPEG/%25C6%25DB%25BD%25C3%25C7%25C8_%25BB%25F3%25BC%25BC.jpg', \
					'http://bshop.phinf.naver.net/20200319_166/1584585904602o7Mp0_JPEG/%25B4%25BA%25C6%25AE%25B8%25AE_%25BB%25F3%25BC%25BC_1.jpg', \
					'http://bshop.phinf.naver.net/20200319_258/1584585930647aVAzw_JPEG/%25B4%25BA%25C6%25AE2.jpg', \
					'http://bshop.phinf.naver.net/20200319_131/1584585739095DUrmF_JPEG/%25B4%25BA%25C6%25AE3.jpg', \
					'http://bshop.phinf.naver.net/20200311_58/1583908903271ocO8j_JPEG/DOG-%25BD%25BA%25B8%25F4%25BA%25EA%25B8%25AE%25B5%25E5.jpg', \
					'http://bshop.phinf.naver.net/20200311_122/1583908903241MqQMc_JPEG/DOG-%25BF%25C0%25BC%25C7%25C7%25C7%25BD%25AC.jpg', \
					'http://bshop.phinf.naver.net/20200311_188/1583908903241qF5iA_JPEG/DOG-%25C4%25A1%25C5%25B2%25C4%25A5%25B8%25E9%25C1%25B6.jpg', \
					'https://shop-phinf.pstatic.net/20170323_67/heedong00_1490256350357dGI0L_JPEG/1.jpg', \
					'https://shop-phinf.pstatic.net/20170323_56/heedong00_1490256350776H6XGY_JPEG/KakaoTalk_20170323_145747922.jpg', \
					'https://shop-phinf.pstatic.net/20170323_299/heedong00_1490256350993fkL9w_JPEG/2.jpg', \
					'https://shop-phinf.pstatic.net/20170323_178/heedong00_1490256351277qqrCO_JPEG/18.jpg', \
					'https://shop-phinf.pstatic.net/20170323_163/heedong00_1490256351533pMRAp_JPEG/15.jpg', \
					'https://shop-phinf.pstatic.net/20170323_89/heedong00_1490256352038x5kWv_JPEG/12.jpg', \
					'https://shop-phinf.pstatic.net/20170323_96/heedong00_14902563522784By3R_JPEG/16.jpg', \
					'https://shop-phinf.pstatic.net/20170323_84/heedong00_1490256352502o8Bh0_JPEG/3.jpg', \
					'https://shop-phinf.pstatic.net/20170323_216/heedong00_149025635276821RIK_JPEG/KakaoTalk_20170323_145747521.jpg', \
					'https://shop-phinf.pstatic.net/20170323_102/heedong00_1490256353038b8C8x_JPEG/14.jpg', \
					'https://shop-phinf.pstatic.net/20170323_2/heedong00_14902563533149c1wO_JPEG/13.jpg', \
					'https://shop-phinf.pstatic.net/20170323_26/heedong00_14902563535770amr0_JPEG/17.jpg', \
					'https://shop-phinf.pstatic.net/20170323_155/heedong00_1490256353819oTtAf_JPEG/10.jpg', \
					'https://shop-phinf.pstatic.net/20170323_251/heedong00_1490256354224PTQMk_JPEG/7.jpg', \
					'https://shop-phinf.pstatic.net/20170323_70/heedong00_1490256354535ng5dL_JPEG/11.jpg', \
					'https://shop-phinf.pstatic.net/20170323_197/heedong00_1490256354823XOvXR_JPEG/8.jpg', \
					'https://shop-phinf.pstatic.net/20170323_94/heedong00_1490256355111iaLQ0_JPEG/5.jpg', \
					'https://shop-phinf.pstatic.net/20170323_72/heedong00_1490256355408RgtWE_JPEG/6.jpg', \
					'https://shop-phinf.pstatic.net/20170323_89/heedong00_1490256355716KL2wQ_JPEG/4.jpg', \
					'https://shop-phinf.pstatic.net/20170323_60/heedong00_1490257504112mW19K_PNG/%25B4%25EB%25B1%25B8.png', \
					'https://shop-phinf.pstatic.net/20170323_270/heedong00_1490257504571nGe92_PNG/%25C6%25DB%25BD%25C3%25C7%25C8.png', \
					'http://bshop.phinf.naver.net/20180228_188/500114562_1519788750343wKc9w_JPEG/%25C7%25C1%25B7%25B9%25C0%25CC%25C1%25AE%25B9%25EB%25B8%25AE_%25BE%25EE%25B4%25FA%25C6%25AE.jpg', \
					'http://bshop.phinf.naver.net/20180928_157/500114562_1538118683770AjAh4_JPEG/%25C6%25DB%25BD%25C3%25C7%25C8_%25BB%25F3%25BC%25BC.jpg']
	
	#img_url_list = ['http://www.biteme.co.kr/data/editor/goods/191227/7805ca8e141a54f6153887ee6df3b76a_193117.jpg', 
	#				'https://shop-phinf.pstatic.net/20170323_60/heedong00_1490257504112mW19K_PNG/%25B4%25EB%25B1%25B8.png', \
	#				'https://shop-phinf.pstatic.net/20170323_270/heedong00_1490257504571nGe92_PNG/%25C6%25DB%25BD%25C3%25C7%25C8.png', \
	#				'http://bshop.phinf.naver.net/20180228_188/500114562_1519788750343wKc9w_JPEG/%25C7%25C1%25B7%25B9%25C0%25CC%25C1%25AE%25B9%25EB%25B8%25AE_%25BE%25EE%25B4%25FA%25C6%25AE.jpg', \
	#				'http://bshop.phinf.naver.net/20180928_157/500114562_1538118683770AjAh4_JPEG/%25C6%25DB%25BD%25C3%25C7%25C8_%25BB%25F3%25BC%25BC.jpg']
	
	#img_url_list = ['http://www.biteme.co.kr/data/editor/goods/191227/7805ca8e141a54f6153887ee6df3b76a_193117.jpg', \
	#				'http://www.biteme.co.kr/data/editor/goods/191227/ee0020d241d634c96b29304451414fdd_193125.jpg', \
	#				'http://www.biteme.co.kr/data/editor/goods/191227/9de850f91f0f92252fb21b777619ad67_193133.jpg', \
	#				'http://www.biteme.co.kr/data/editor/goods/191227/07b5922c90a15ba239d505c66f37f248_191733.jpg']
					
					
	rtn , rtn_img = get_merge_img( img_url_list )


	



	
	
	