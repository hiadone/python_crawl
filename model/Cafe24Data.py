# -*- coding: utf-8 -*-


class Cafe24Data:

	def __init__(self):
		self.product_no = ''	# 상품번호
		self.product_name = ''

		self.price = '0'
		self.retail_price = '0'
		self.description = ''
		self.sold_out = False

		
	def toJSON(self):
		return str(json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4))