import json

class Tools:
	def __init__(self, fn):
		with open(fn, "r") as fp:
			self.json = json.load(fp)
			
	def getTools(self):
		return sorted(self.json.keys())
			
	def getTool(self, tname):
		if tname not in self.json.keys():
			return None
		
		return self.json[tname]
			
	def getToolSpeeds(self, tname, mname):
		if tname not in self.json.keys():
			return None
		
		if mname not in self.json[tname]["speeds"].keys():
			return None
		
		return self.json[tname]["speeds"][mname]
			


