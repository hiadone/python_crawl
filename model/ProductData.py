# -*- coding: utf-8 -*-


from app import define_mall as __DEFINE__

class CategoryData:

	def __init__(self):
		
		self.category_depth = 0	
		self.parent_category_no = 0
		self.category_name  = ''
		self.category_depth_name = []
		
		
class ProductData:

	def __init__(self):
		
		self.brd_id = 0
		self.crw_id = 0
		
		self.crw_action = __DEFINE__.__INSERT_CRW__
		
		self.crw_name  = ''   		#상세리스트 부분의 상품명 ,필수
		self.crw_price = 0  		#상세리스트 부분의 상품 가격 ,필수
				
		self.crw_is_soldout = 0    	# 상세리스트 부분의 1이면 솔드아웃 0 이면 판매중  ,필수
		self.crw_goods_code  = ''  	#상세리스트 부분의 상품 product_no ,필수
		self.crw_post_url  = ''  	#상세리스트 부분의 상품 아웃 링크 ,필수
		self.crw_price_sale = 0    	#상세리스트 부분의 상품 할인 가격 ,필수 (없으면 0 으로 넘겨주세요
		
		self.crw_file_1 = ''		# 상품리스트에서의 상품이미지 파일명
		
		self.crw_brand1  = '' 		#상세리스트 부분의 상품 브랜드 1순위 추정되는 String
		self.crw_brand2  = ''  		#상세리스트 부분의 상품 브랜드 2순위 추정되는 String
		self.crw_brand3  = ''  		#상세리스트 부분의 상품 브랜드 3순위 추정되는 String 
		self.crw_brand4  = '' 		#상세리스트 부분의 ...
		self.crw_brand5  = ''
		
		self.crw_category1  = ''  	#상품 카테고리 3순위 추정되는 String 
		self.crw_category2  = ''  	#상품 카테고리 3순위 추정되는 String (혹시 몰라 만듬 )
		self.crw_category3  = ''  	#상품 카테고리 3순위 추정되는 String (혹시 몰라 만듬 ) 
		
		
		#
		#
		self.cdt_content  = ''  	# 상세페이지 부분의 상품 상세 정보 text
		self.d_crw_file_1 = ''		# 상세페이지 부분의 통합이미지 파일명
		
		self.d_crw_brand1  = '' 		#상세페이지 부분의 상품 브랜드 1순위 추정되는 String
		self.d_crw_brand2  = ''  		#상세페이지 부분의 상품 브랜드 2순위 추정되는 String
		self.d_crw_brand3  = ''  		#상세페이지 부분의 상품 브랜드 3순위 추정되는 String 
		self.d_crw_brand4  = '' 		# 상세페이지 부분의 ...
		self.d_crw_brand5  = ''
		
		#
		self.product_img = ''	# 상세리스트 부분의 이미지 URL 리스트
		self.detail_page_img = []	# 상세페이지 부분의 이미지 URL 리스트
		
		
				
		self.product_id = ''
		self.product_no = ''
		

		
	def toJSON(self):
		return str(json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4))