import os
import json

class Options:
	def __init__(self):
		try:
			with open("options.json", "r") as fp:
				self.opts = json.load(fp)
		except (IOError, FileNotFoundError):
			self.opts = {
				"autoLabel": True,
				"lastDir" : os.getcwd(),
				"autogrowright": True
			}
			self.save()

	def AutoLabel(self):
		return self.opts["autoLabel"]
	
	def AutoGrowRight(self):
		try:
			return self.opts["autogrowright"]
		except KeyError:
			self.opts["autogrowright"] = True
			self.save()
			return self.opts["autogrowright"]
		
	def setAutoGrowRight(self, flag):
		self.opts["autogrowright"] = flag
		self.save()
	
	def LastDir(self):
		return self.opts["lastDir"]
		
	def setLastDir(self, dn):
		self.opts["lastDir"] = dn
		self.save()
		
	def save(self):
		with open("options.json", 'w') as f:
			json.dump(self.opts, f, sort_keys=True, indent=4)

