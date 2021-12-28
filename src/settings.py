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
		self.lastjsondir = "."
		self.annotate = False
		self.addspeed = False
		self.metric = True
		self.tool = "110"
		self.material = "MDF"
		self.speedG0XY = 600
		self.speedG1XY = 330
		self.speedG0Z = 300
		self.speedG1Z = 55
		self.safez = 0.5
		self.totaldepth = 1.6
		self.depthperpass = 0.33
		self.stepover = 0.75
		self.decimals = 4
		self.boxdirectory = os.getcwd()
		self.boxgcodedirectory = os.getcwd()
		
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
				elif opt == 'lastjsondir':
					self.lastjsondir = value
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
				elif opt == 'speedG0XY':
					self.speedG0XY = int(float(value))
				elif opt == 'speedG1XY':
					self.speedG1XY = int(float(value))
				elif opt == 'speedG0Z':
					self.speedG0Z = int(float(value))
				elif opt == 'speedG1Z':
					self.speedG1Z = int(float(value))
				elif opt == 'decimals':
					self.decimals = int(float(value))
				elif opt == 'depthperpass':
					self.depthperpass = float(value)
				elif opt == 'stepover':
					self.stepover = float(value)
				elif opt == 'totaldepth':
					self.totaldepth = float(value)
				elif opt == 'safez':
					self.safez = float(value)
				elif opt == "boxdirectory":
					self.boxdirectory = value
				elif opt == "boxgcodedirectory":
					self.boxgcodedirectory = value
				else:
					print("Unknown %s option: %s - ignoring" % (self.section, opt))
		else:
			print("Missing %s section - assuming defaults" % self.section)
				

	def setModified(self):
		self.modified = True
		
	def checkModified(self):
		return self.modified
		
	def save(self):
		try:
			self.cfg.add_section(self.section)
		except configparser.DuplicateSectionError:
			pass
		
		self.cfg.set(self.section, "lastsavedir", str(self.lastsavedir))
		self.cfg.set(self.section, "lastloaddir", str(self.lastloaddir))
		self.cfg.set(self.section, "lastjsondir", str(self.lastjsondir))
		self.cfg.set(self.section, "tool", str(self.tool))
		self.cfg.set(self.section, "material", str(self.material))
		self.cfg.set(self.section, "annotate", str(self.annotate))
		self.cfg.set(self.section, "addspeed", str(self.addspeed))
		self.cfg.set(self.section, "metric", str(self.metric))
		self.cfg.set(self.section, "speedG0XY", "%d" % self.speedG0XY)
		self.cfg.set(self.section, "speedG1XY", "%d" % self.speedG1XY)
		self.cfg.set(self.section, "speedG0Z", "%d" % self.speedG0Z)
		self.cfg.set(self.section, "speedG1Z", "%d" % self.speedG1Z)
		self.cfg.set(self.section, "depthperpass", "%.2f" % self.depthperpass)
		self.cfg.set(self.section, "stepover", "%.2f" % self.stepover)
		self.cfg.set(self.section, "totaldepth", "%.2f" % self.totaldepth)
		self.cfg.set(self.section, "safez", "%.2f" % self.safez)
		self.cfg.set(self.section, "boxdirectory", str(self.boxdirectory))
		self.cfg.set(self.section, "boxgcodedirectory", str(self.boxgcodedirectory))
		self.cfg.set(self.section, "decimals", "%d" % self.decimals)

		try:		
			cfp = open(self.inifile, 'w')
		except:
			print("Unable to open settings file %s for writing" % self.inifile)
			return
		self.cfg.write(cfp)
		cfp.close()
		
		self.modified = False

