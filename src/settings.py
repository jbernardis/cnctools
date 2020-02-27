import configparser
import os

INIFILE = "cnctools.ini"

BTNDIM = (48,48)

def parseBoolean(val, defaultVal):
	lval = val.lower();
	
	if lval == 'true' or lval == 't' or lval == 'yes' or lval == 'y':
		return True
	
	if lval == 'false' or lval == 'f' or lval == 'no' or lval == 'n':
		return False
	
	return defaultVal

class Settings:
	def __init__(self, app, folder):
		self.app = app
		self.cmdfolder = folder
		self.inifile = os.path.join(folder, INIFILE)
		self.section = "cnctools"	
		
		self.lastsavedir = "."
		self.lastloaddir = "."
		self.annotate = False
		self.addspeed = False
		self.metric = True
		self.tool = "110"
		self.material = "MDF"
		
		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			print("Settings file %s does not exist.  Using default values" % INIFILE)
			
			self.modified = True
			return

		self.modified = False	
		if self.cfg.has_section(self.section):
			for opt, value in self.cfg.items(self.section):
				if opt == 'lastsavedir':
					self.lastsavedir = value
				elif opt == 'lastloaddir':
					self.lastloaddir = value
				elif opt == "tool":
					self.tool = value;
				elif opt == "material":
					self.material = value
				elif opt == 'annotate':
					self.annotate = parseBoolean(value, False)
				elif opt == 'addspeed':
					self.addspeed = parseBoolean(value, False)
				elif opt == 'metric':
					self.metric = parseBoolean(value, False)
				else:
					print("Unknown %s option: %s - ignoring" % (self.section, opt))
		else:
			print("Missing %s section - assuming defaults" % self.section)
				

	def setModified(self):
		self.modified = True
		
	def checkModified(self):
		return self.modified
		
	def cleanUp(self):
		if self.checkModified():
			try:
				self.cfg.add_section(self.section)
			except configparser.DuplicateSectionError:
				pass
			
			self.cfg.set(self.section, "lastsavedir", str(self.lastsavedir))
			self.cfg.set(self.section, "lastloaddir", str(self.lastloaddir))
			self.cfg.set(self.section, "tool", str(self.tool))
			self.cfg.set(self.section, "material", str(self.material))
			self.cfg.set(self.section, "annotate", str(self.annotate))
			self.cfg.set(self.section, "addspeed", str(self.addspeed))
			self.cfg.set(self.section, "metric", str(self.metric))

			try:		
				cfp = open(self.inifile, 'w')
			except:
				print("Unable to open settings file %s for writing" % self.inifile)
				return
			self.cfg.write(cfp)
			cfp.close()

