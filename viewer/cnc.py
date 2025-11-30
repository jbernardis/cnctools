import re
import math

MT_NORMAL = 0
MT_RAPID = 1

gcRegex = re.compile(r'[-]?\d+[.]?\d*')


def get_float(which, pstr):
	try:
		return float(gcRegex.findall(pstr.split(which)[1])[0])
	except ValueError:
		return 0.0
	except IndexError:
		return 0.0


def drawArc(cx, cy, cz, rad, angstart, angend, cw, numsegments):
	pts = []
	if cw:
		sign = -1
		angdist = angstart - angend
		while angdist <= 0:
			angdist += 2*math.pi
	else:
		sign = 1
		angdist = angend - angstart
		while angdist <= 0:
			angdist += 2*math.pi
			
	segs = int(math.degrees(angdist)/4)
	if segs < numsegments:
		segs = numsegments
		
	for i in range(segs+1): 
		theta = angstart + sign * (angdist * (float(i) / float(segs)))
		while theta < 0:
			theta += 2*math.pi

		dx = rad * math.cos(theta)
		dy = rad * math.sin(theta) 

		pts.append([cx + dx, cy + dy, cz]) 
		
	return pts


def setQuadrant(sa, dx, dy):
	a = math.degrees(sa)
	if dy >= 0:
		while a < 0.0:
			a += 180
		while a > 180:
			a -= 180
	else:
		while a < 180:
			a += 180
		while a > 360:
			a -= 180
		
	if dx <= 0:
		while a > 270:
			a -= 180
		while a < 90:
			a += 180
	else:
		while a > 450:
			a -= 180
		while a < 270:
			a += 180
		if a >= 360:
			a -= 360
	
	return math.radians(a)


class GParseErrorSyntax(Exception):
	pass


class GParseErrorNoCommand(Exception):
	pass


class GParseErrorNumberFormat(Exception):
	pass


class gShifter:
	reXparam = re.compile(r'(.*X *)(-{0,1}\d*\.\d+)(.*)')
	reYparam = re.compile(r'(.*Y *)(-{0,1}\d*\.\d+)(.*)')

	def __init__(self, dx, dy):
		self.dx = dx
		self.dy = dy
		
	def shift(self, gline):
		if self.dx != 0:
			gline = self.shiftX(gline)
		if self.dy != 0:
			gline = self.shiftY(gline)
		return gline
	
	def getFormat(self, sval):
		c = sval.split(".")
		if len(c) != 2:
			print("length not 2 (%s)" % sval)
			return "%-.2f"
		
		l = len(c[1])
		fmt = "%" + ("-0.%df" % l)
		return fmt
	
	def shiftX(self, gline):
		r = gShifter.reXparam.match(gline)
		if r is None:
			return gline
		
		try:
			sval = r.group(2)
			val = float(sval)
		except:
			print("unable to parse X value out of (%s) - leaving unchanged" % gline)
			return gline
		
		newsval = self.getFormat(sval) % (val + self.dx)
		
		newg = r.group(1) + newsval + r.group(3)
		return newg
	
	def shiftY(self, gline):
		r = gShifter.reYparam.match(gline)
		if r is None:
			return gline
		
		try:
			sval = r.group(2)
			val = float(sval)
		except:
			print("unable to parse y value out of (%s) - leaving unchanged" % gline)
			return gline
		
		newsval = self.getFormat(sval) % (val + self.dy)
		
		newg = r.group(1) + newsval + r.group(3)
		return newg
		

class gMirror:
	reXparam = re.compile(r'(.*X *)(-{0,1}\d*\.\d+)(.*)')
	reYparam = re.compile(r'(.*Y *)(-{0,1}\d*\.\d+)(.*)')

	def __init__(self):
		pass
		
	def getFormat(self, sval):
		c = sval.split(".")
		if len(c) != 2:
			print("length not 2 (%s)" % sval)
			return "%-.2f"
		
		l = len(c[1])
		fmt = "%" + ("-0.%df" % l)
		return fmt
	
	def mirrorY(self, gline):
		r = gMirror.reXparam.match(gline)
		if r is None:
			return gline
		
		try:
			sval = r.group(2)
			val = float(sval)
		except:
			print("unable to parse X value out of (%s) - leaving unchanged" % gline)
			return gline
		
		newsval = self.getFormat(sval) % -val
		
		newg = r.group(1) + newsval + r.group(3)
		return newg
	
	def mirrorX(self, gline):
		r = gMirror.reYparam.match(gline)
		if r is None:
			return gline
		
		try:
			sval = r.group(2)
			val = float(sval)
		except:
			print("unable to parse y value out of (%s) - leaving unchanged" % gline)
			return gline
		
		newsval = self.getFormat(sval) % -val	
			
		newg = r.group(1) + newsval + r.group(3)
		return newg
		

class gParser:
	gcmd = re.compile(r'^([GMT]\d+)(.*)')
	gparm = re.compile(r'^([XYZFIJKS] *-{0,1}\d*\.{0,1}\d+)(.*)')

	def __init__(self):
		self.lastCmd = None

	def parseGLine(self, gline):
		gl = gline.strip().upper()
		if '(' in gl:
			gl = gl.split('(', 1)[0]

		if ';' in gl:
			gl = gl.split(';', 1)[0]

		if '%' in gl:
			gl = gl.split('%', 1)[0]

		if len(gl) == 0:
			return None, None

		r = gParser.gcmd.match(gl)
		if r is None:
			if self.lastCmd is None:
				raise GParseErrorNoCommand
			else:
				cmd = self.lastCmd
				remaining = gl
		else:
			cmd = r.group(1)
			try:
				remaining = r.group(2).strip()
			except IndexError:
				remaining = ""

			if cmd in ["G1", "G01", "G0", "G00"]:
				self.lastCmd = cmd

		parms = {}
		while remaining != "":
			r = gParser.gparm.match(remaining)
			if r is None:
				raise GParseErrorSyntax
			else:
				prm = r.group(1)
				tag = prm[0]
				prm = prm[1:]
				try:
					parms[tag] = float(prm)
				except ValueError:
					raise GParseErrorNumberFormat

				try:
					remaining = r.group(2).strip()
				except IndexError:
					remaining = ""

		return cmd, parms	
	
	
class CNC:
	def __init__(self):
		self.curX = 0
		self.curY = 0
		self.curZ = 0
		self.curI = 0
		self.curJ = 0
		self.curK = 0

		self.points = [(0, 0, 0, MT_NORMAL)]
		
		self.relative = False
		self.metric = True	
		
		self.lastCmd = "G1"
		
		self.gp = gParser()

		self.dispatch = {
			"G0": self.moveFast,
			"G1": self.moveSlow,
			"G2": self.arcCW,
			"G3": self.arcCCW,
			"G20": self.setInches,
			"G21": self.setMillimeters,
			"G28": self.home,
			"G90": self.setAbsolute,
			"G91": self.setRelative,
			"G92": self.axisReset,
			}
		
	def execute(self, gline):
		cmd, params = self.gp.parseGLine(gline)
		if cmd is None:
			return
		if cmd not in self.dispatch:
			return
	
		self.dispatch[cmd](params)
		
	def moveFast(self, parms):
		self.lastCmd = "G0"
		self.move(parms, MT_RAPID)
		
	def moveSlow(self, parms):
		self.lastCmd = "G1"
		self.move(parms, MT_NORMAL)
		
	def move(self, parms, moveType):
		self.checkCoords(parms)		
		self.recordPoint(self.curX, self.curY, self.curZ, moveType)
		
	def arcCW(self, params):
		self.arc(params, True)
		
	def arcCCW(self, params):
		self.arc(params, False)
		
	def arc(self, params, cw):
		x = self.curX
		y = self.curY
		z = self.curZ
		self.checkCoords(params)
		
		cx = x + self.curI
		cy = y + self.curJ
		cz = z + self.curK

		# calculate radius, start and end angles
		dx = x - cx
		dy = y - cy
		if dy == 0:
			startang = math.radians(0)
		elif dx == 0:
			startang = math.radians(90)
		else:
			startang = math.atan(dy/dx)
			
		startang = setQuadrant(startang, dx, dy)
		rad = math.sqrt(dx*dx+dy*dy)
		
		dx = self.curX - cx
		dy = self.curY - cy
		if dy == 0:
			endang = math.radians(0)
		elif dx == 0:
			endang = math.radians(90)
		else:
			endang = math.atan(dy/dx)
		endang = setQuadrant(endang, dx, dy)

		pts = drawArc(cx, cy, cz, rad, startang, endang, cw, 20)
		for p in pts:
			self.recordPoint(p[0], p[1], p[2], MT_NORMAL)
	
	def recordPoint(self, px, py, pz, mtype):
		self.points.append((px, py, pz, mtype))
		
	def getPoints(self):
		return self.points
		
	def setInches(self, _):
		self.metric = False

	def setMillimeters(self, _):
		self.metric = True

	def home(self, parms):
		naxes = 0
		if 'X' in parms.keys():
			self.curX = 0
			naxes += 1
		if 'Y' in parms.keys():
			self.curY = 0
			naxes += 1
		if 'Z' in parms.keys():
			self.curZ = 0
			naxes += 1
			
		if naxes == 0:
			self.curX = 0
			self.curY = 0
			self.curZ = 0
			
		self.recordPoint(self.curX, self.curY, self.curZ, MT_NORMAL)

	def setAbsolute(self, *_):
		self.relative = False

	def setRelative(self, *_):
		self.relative = True
		
	def axisReset(self, parms, _):
		if 'X' in parms.keys():
			self.curX = float(parms['X'])
		if 'Y' in parms.keys():
			self.curY = float(parms['Y'])
		if 'Z' in parms.keys():
			self.curZ = float(parms['Z'])
	
	def checkCoords(self, parms):
		if self.relative:
			if 'X' in parms.keys():
				self.curX += float(parms["X"])
			if 'Y' in parms.keys():
				self.curY += float(parms["Y"])
			if 'Z' in parms.keys():
				self.curZ += float(parms["Z"])
		else:
			if 'X' in parms.keys():
				self.curX = float(parms["X"])
			if 'Y' in parms.keys():
				self.curY = float(parms["Y"])
			if 'Z' in parms.keys():
				self.curZ = float(parms["Z"])

		self.curI = 0.0
		self.curJ = 0.0
		self.curK = 0.0
		if 'I' in parms.keys():
			self.curI = float(parms["I"])
		if 'J' in parms.keys():
			self.curJ = float(parms["J"])
		if 'K' in parms.keys():
			self.curK = float(parms["K"])


