# -*- coding: utf-8 -*-


class BrdData:

	def __init__(self):
	
		self.brd_id = 0
		self.brd_name = ''
		
		self.brd_url = ''
		self.brd_comment = ''	
		
		
	def toJSON(self):
		return str(json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4))