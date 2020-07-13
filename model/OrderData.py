# -*- coding: utf-8 -*-


from app import define_mall as __DEFINE__

class OrderData:

	def __init__(self):
		
		self.brd_id = 0				#하이드애원에서 전달해준 스토어 id, 필수 
		self.mem_id = 0				#하이드애원에서 전달해준 맴버 id , 필수
		self.cor_key  = ''  		#하이애드원에서 전달해준 key ,필수 
		
		self.cor_pay_type  = ''  		#하이애드원에서 전달해준 구매 페이 타입 ,필수
		
		
		self.cor_order_no  = ''   	#크롤링한 주문번호 ,필수 

		self.total_price_sum  = 0    	#주문한 상품 총 가격
		
		
		self.cor_goods_code  = []	# 상품 product_no  
		
		self.cod_count   = []		# 상품 구매 개수(위 cor_goods_code 와 짝을 이루어서)
		
		self.cor_content   = ''  	# 컨텐츠 (ex 청바지 외 3개 상품) 

		self.cor_file_1 = ''		# 구매정보 html가 들어 있는 파일 path 정보
		
		self.brd_url = ''			# 쇼핑몰 URL
		
		self.search_web_str = ''			# function을 찾기 위한 URL
		
		self.action_value = 0			# cor_id 또는 cos_id
		
	def toJSON(self):
		return str(json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4))
		
		

class OrderStatusData:

	def __init__(self):
		
		self.brd_id = 0				#하이드애원에서 전달해준 스토어 id, 필수 
		self.mem_id = 0				#하이드애원에서 전달해준 맴버 id , 필수

		self.cor_pay_type  = ''  		#하이애드원에서 전달해준 구매 페이 타입 ,필수
		
		self.cos_order_no  = ''   	#크롤링한 주문번호 ,필수 

		self.cor_carrier   = ''  	#택배사
		
		self.cor_track   = ''  	 #택배 운송장 번호
		
		self.cor_goods_code   = []  	 #상품 product_no  
		self.cod_count   = []  	 #상품 구매 개수(위 cor_goods_code 와 짝을 이루어서)
		
		self.cor_memo   = ''  	 #주문 상태 현황(배송중,준비중,취소 등등 )

		self.cos_file_1 = ''		# 주문 현황 정보 html가 들어 있는 파일 path 정보
		
		self.brd_url = ''			# 쇼핑몰 URL
		
		self.search_web_str = ''			# function을 찾기 위한 URL
		
		self.action_value = 0			# cor_id 또는 cos_id
		
	def toJSON(self):
		return str(json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4))