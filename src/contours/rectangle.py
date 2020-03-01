import wx
import math
from gcodelist import GCodeList
from cncobject import CNCObject
from validators import ValidateToolSize, ValidateRange, ValidateNoEntryErrors
from rotator import Rotator

class MainFrame(wx.Frame):
	def __init__(self, toolInfo, speedInfo, parent):
		self.parent = parent
		self.settings = parent.settings
		self.images = self.parent.images
		
		wx.Frame.__init__(self, None, size=(480, 800), title="")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = RectanglePanel(toolInfo, speedInfo, self)
		sizer.Add(self.panel)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def okToClose(self):
		return self.panel.okToClose()
	
	def onClose(self, _):
		return self.panel.onClose(None)

class RectanglePanel(wx.Panel, CNCObject):
	seqNo = 1
	def __init__(self, toolInfo, speedInfo, parent):
		CNCObject.__init__(self, parent, "contour:rectangle")
		self.toolInfo = toolInfo
		
		self.modified = False
		self.unsaved = False
		self.viewTitle = "Rectangle %d" % RectanglePanel.seqNo
		self.titleText = "G Code Generator: %s" % self.viewTitle
		RectanglePanel.seqNo += 1
		
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		sizer = wx.GridBagSizer(wx.HORIZONTAL)
		sizer.Add(10, 10, wx.GBPosition(0, 4))
		ln = 1
		
		self.setTitleFlag()

		t = wx.StaticText(self, wx.ID_ANY, "Height")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teHeight = wx.TextCtrl(self, wx.ID_ANY, "10", style=wx.TE_RIGHT)
		self.addWidget(self.teHeight, "height")
		sizer.Add(self.teHeight, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Width")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teWidth = wx.TextCtrl(self, wx.ID_ANY, "10", style=wx.TE_RIGHT)
		self.addWidget(self.teWidth, "width")
		sizer.Add(self.teWidth, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Rotation Angle")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teAngle = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_RIGHT)
		self.addWidget(self.teAngle, "angle")
		sizer.Add(self.teAngle, pos=(ln, 1), flag=wx.LEFT, border=10)

		t = wx.StaticText(self, wx.ID_ANY, "Tool Diameter")
		td = "%6.3f" % toolInfo["diameter"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teToolDiam = wx.TextCtrl(self, wx.ID_ANY, td, style=wx.TE_RIGHT)
		self.addWidget(self.teToolDiam, "tooldiameter")
		sizer.Add(self.teToolDiam, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Total Depth")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teTotalDepth = wx.TextCtrl(self, wx.ID_ANY, "1", style=wx.TE_RIGHT)
		self.addWidget(self.teTotalDepth, "depth")
		sizer.Add(self.teTotalDepth, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Depth/Pass")
		dpp = "%6.3f" % speedInfo["depthperpass"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.tePassDepth = wx.TextCtrl(self, wx.ID_ANY, dpp, style=wx.TE_RIGHT)
		self.addWidget(self.tePassDepth, "passdepth")
		sizer.Add(self.tePassDepth, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Start X")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teStartX = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_RIGHT)
		self.addWidget(self.teStartX, "startx")
		sizer.Add(self.teStartX, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Start Y")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teStartY = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_RIGHT)
		self.addWidget(self.teStartY, "starty")
		sizer.Add(self.teStartY, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Start Z")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teStartZ = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_RIGHT)
		self.addWidget(self.teStartZ, "startz")
		sizer.Add(self.teStartZ, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Safe Z above surface")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teSafeZ = wx.TextCtrl(self, wx.ID_ANY, "0.5", style=wx.TE_RIGHT)
		self.addWidget(self.teSafeZ, "safez")
		sizer.Add(self.teSafeZ, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1
		
		self.cbAddSpeed = wx.CheckBox(self, wx.ID_ANY, "Add Speed Parameter")
		self.addWidget(self.cbAddSpeed, "addspeed")
		sizer.Add(self.cbAddSpeed, pos=(ln, 0), span=(1,4),
				flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_HORIZONTAL, border=5)
		self.Bind(wx.EVT_CHECKBOX, self.onCbAddSpeed, self.cbAddSpeed)
		self.cbAddSpeed.SetValue(self.settings.addspeed)
		ln += 1
		
		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate XY (G0)")
		g0xy = "%7.2f" % speedInfo["G0XY"]
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teFeedXYG0 = wx.TextCtrl(self, wx.ID_ANY, g0xy, style=wx.TE_RIGHT)
		self.addWidget(self.teFeedXYG0, "feedXYG0")
		sizer.Add(self.teFeedXYG0, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate XY (G1)")
		g1xy = "%7.2f" % speedInfo["G1XY"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teFeedXYG1 = wx.TextCtrl(self, wx.ID_ANY, g1xy, style=wx.TE_RIGHT)
		self.addWidget(self.teFeedXYG1, "feedXYG1")
		sizer.Add(self.teFeedXYG1, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate Z (G0)")
		g0z = "%7.2f" % speedInfo["G0Z"]
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teFeedZG0 = wx.TextCtrl(self, wx.ID_ANY, g0z, style=wx.TE_RIGHT)
		self.addWidget(self.teFeedZG0, "feedZG0")
		sizer.Add(self.teFeedZG0, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate Z (G1)")
		g1z = "%7.2f" % speedInfo["G1Z"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teFeedZG1 = wx.TextCtrl(self, wx.ID_ANY, g1z, style=wx.TE_RIGHT)
		self.addWidget(self.teFeedZG1, "feedZG1")
		sizer.Add(self.teFeedZG1, pos=(ln, 3), flag=wx.LEFT, border=10)

		self.teFeedXYG0.Enable(self.settings.addspeed)
		self.teFeedXYG1.Enable(self.settings.addspeed)
		self.teFeedZG0.Enable(self.settings.addspeed)
		self.teFeedZG1.Enable(self.settings.addspeed)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Starting Point")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)	
		sizer.Add(self.getStartingPoints(), pos=(ln, 1), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	

		t = wx.StaticText(self, wx.ID_ANY, "Tool Movement")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sizer.Add(self.getToolMovement(), pos=(ln, 3), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Cutting Direction")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sizer.Add(self.getCuttingDirection(), pos=(ln, 1), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	

		t = wx.StaticText(self, wx.ID_ANY, "Measurement System")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sizer.Add(self.getMeasurementSystem(), pos=(ln, 3), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Pocket")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sizer.Add(self.getPockets(), pos=(ln, 1), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	

		t = wx.StaticText(self, wx.ID_ANY, "Stepover")
		so = "%6.3f" % speedInfo["stepover"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teStepOver = wx.TextCtrl(self, wx.ID_ANY, so, style=wx.TE_RIGHT)
		self.addWidget(self.teStepOver, "stepover")
		sizer.Add(self.teStepOver, pos=(ln, 3), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=10)
		ln += 1
		
		t = wx.StaticText(self, wx.ID_ANY, "Decimal Places")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teDecimals = wx.TextCtrl(self, wx.ID_ANY, "4", style=wx.TE_RIGHT)
		self.addWidget(self.teDecimals, "decimals")
		sizer.Add(self.teDecimals, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		sizer.Add(20, 20, wx.GBPosition(ln, 0))
		ln += 1
		
		bsz = self.buttons()
		
		sizer.Add(bsz, pos=(ln, 0), span=(1,4),
				flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_HORIZONTAL, border=5)
		ln += 1
		
		sizer.Add(10, 10, wx.GBPosition(ln, 0))
		ln += 1
		
		self.gcl = GCodeList(self)
		sizer.Add(self.gcl, pos=(ln, 0), span=(1, 4), flag=wx.LEFT+wx.EXPAND, border=10)
		ln += 1
		
		sizer.Add(10, 10, wx.GBPosition(ln, 0))

		self.Bind(wx.EVT_TEXT, self.onChange)
		self.Bind(wx.EVT_RADIOBUTTON, self.onChange)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def getStartingPoints(self):
		labels = ["Lower Left", "Upper Left", "Lower Right", "Upper Right", "Center"]
		self.rbStartPoints = []
		sz = wx.BoxSizer(wx.VERTICAL)
		for i in range(len(labels)):
			if i == 0:
				style = wx.RB_GROUP
			else:
				style = 0
			r = wx.RadioButton(self, wx.ID_ANY, labels[i], style=style)
			self.addWidget(r, labels[i])
			sz.Add(r)
			self.rbStartPoints.append(r)
		return sz
		
	def getToolMovement(self):
		labels = ["On Rectangle", "Outside Rectangle", "Inside Rectangle"]
		self.rbToolMove = []
		sz = wx.BoxSizer(wx.VERTICAL)
		for i in range(len(labels)):
			if i == 0:
				style = wx.RB_GROUP
			else:
				style = 0
			r = wx.RadioButton(self, wx.ID_ANY, labels[i], style=style)
			self.addWidget(r, labels[i])
			sz.Add(r)
			self.rbToolMove.append(r)
		return sz
	
	def getCuttingDirection(self):
		labels = ["Clockwise", "Counter Clockwise"]
		self.rbCutDir = []
		sz = wx.BoxSizer(wx.VERTICAL)
		for i in range(len(labels)):
			if i == 0:
				style = wx.RB_GROUP
			else:
				style = 0
			r = wx.RadioButton(self, wx.ID_ANY, labels[i], style=style)
			self.addWidget(r, labels[i])
			sz.Add(r)
			self.rbCutDir.append(r)
		return sz
	
	def getMeasurementSystem(self):
		labels = ["Metric", "Imperial"]
		self.rbMeas = []
		sz = wx.BoxSizer(wx.VERTICAL)
		for i in range(len(labels)):
			if i == 0:
				style = wx.RB_GROUP
			else:
				style = 0
			r = wx.RadioButton(self, wx.ID_ANY, labels[i], style=style)
			self.addWidget(r, labels[i])
			sz.Add(r)
			self.rbMeas.append(r)
		if self.settings.metric:
			self.setChosen(self.rbMeas, "Metric")
		else:
			self.setChosen(self.rbMeas, "Imperial")
		return sz
	
	def getPockets(self):
		labels = ["None", "Horizontal", "Vertical", "Centered"]
		self.rbPkts = []
		sz = wx.BoxSizer(wx.VERTICAL)
		for i in range(len(labels)):
			if i == 0:
				style = wx.RB_GROUP
			else:
				style = 0
			r = wx.RadioButton(self, wx.ID_ANY, labels[i], style=style)
			self.addWidget(r, labels[i])
			sz.Add(r)
			self.rbPkts.append(r)
		return sz
		
	def onCbAddSpeed(self, _):
		self.setState(True, False)
		flag = self.cbAddSpeed.IsChecked()
		self.teFeedXYG0.Enable(flag)
		self.teFeedXYG1.Enable(flag)
		self.teFeedZG0.Enable(flag)
		self.teFeedZG1.Enable(flag)
		
	def bGeneratePressed(self, _):
		self.bSave.Enable(False)
		self.bVisualize.Enable(False)
		self.gcl.clear()
		self.gcode = []
		
		errs = []
		try:
			dec = int(self.teDecimals.GetValue())
			self.fmt = "%0." + str(dec) + "f"
		except:
			errs.append("Decimal Places")	
		try:
			sx = float(self.teStartX.GetValue())
		except:
			errs.append("Start X")	
		try:
			sy = float(self.teStartY.GetValue())
		except:
			errs.append("Start Y")	
		try:
			sz = float(self.teStartZ.GetValue())
		except:
			errs.append("Start Z")	
		try:
			safez = float(self.teSafeZ.GetValue())
		except:
			errs.append("Safe Z")	
			
		addspeed = self.cbAddSpeed.IsChecked()
		try:
			feedzG0 = float(self.teFeedZG0.GetValue())
		except:
			errs.append("Z G0 Speed")	
		try:
			feedzG1 = float(self.teFeedZG1.GetValue())
		except:
			errs.append("Z G1 Speed")	
		try:
			feedxyG0 = float(self.teFeedXYG0.GetValue())
		except:
			errs.append("XY G0 Speed")	
		try:
			feedxyG1 = float(self.teFeedXYG1.GetValue())
		except:
			errs.append("XY G1 Speed")	
		try:
			height = float(self.teHeight.GetValue())
		except:
			errs.append("Height")	
		try:
			width = float(self.teWidth.GetValue())
		except:
			errs.append("Width")	
		try:
			depth = float(self.teTotalDepth.GetValue())
		except:
			errs.append("Depth")	
		try:
			passdepth = float(self.tePassDepth.GetValue())
		except:
			errs.append("Depth per Pass")	
		try:
			tdiam = float(self.teToolDiam.GetValue())
		except:
			errs.append("Tool Diameter")	
		try:
			stepover = float(self.teStepOver.GetValue())
		except:
			errs.append("Stepover")	
		try:
			angle = float(self.teAngle.GetValue())
		except:
			errs.append("Angle")	

		if not ValidateNoEntryErrors(self, errs):
			return
			
		rot = Rotator(angle)
			
		if not ValidateToolSize(self, tdiam, height, "Height"):
			return
		if not ValidateToolSize(self, tdiam, width, "Width"):
			return
		
		if not ValidateRange(self, stepover, 0.001, 1.0, "Stepover", "0 < x <= 1.0"):
			return

		self.gcode = self.preamble(self.getChosen(self.rbMeas), tdiam, self.toolInfo, safez)
		
		self.tDiam = tdiam
		if self.settings.annotate:
			if angle == 0:
				self.gcode.append("(Rectangle (%6.2f,%6.2f) to (%6.2f,%6.2f) depth from %6.2f to %6.2f)" % (sx, sy, width, height, sz, depth))
			else:
				rx1, ry1 = rot.rotate(sx, sy)
				rx2, ry2 = rot.rotate(width+sx, height+sy)
				self.gcode.append("(Rectangle (%6.2f,%6.2f) to (%6.2f,%6.2f) depth from %6.2f to %6.2f rotated %6.2f)" % (rx1, ry1, rx2, ry2, sz, depth, angle))
			
		points = [[sx, sy], [sx, sy+height], [sx+width, sy+height], [sx+width, sy], [sx, sy]]
			
		sp = self.getChosen(self.rbStartPoints)
		adjx = 0
		adjy = 0
		if sp == "Upper Left":
			adjy = -height
		elif sp == "Upper Right":
			adjy = -height
			adjx = -width
		elif sp == "Lower Right":
			adjx = -width
		elif sp == "Center":
			adjx = -width/2
			adjy = -height/2
			
		for p in points:
			p[0] += adjx
			p[1] += adjy
			
		tm = self.getChosen(self.rbToolMove)
		rad = float(tdiam)/2.0
		if tm == "Inside Rectangle":
			points[0][0] += rad
			points[0][1] += rad
			points[1][0] += rad
			points[1][1] -= rad
			points[2][0] -= rad
			points[2][1] -= rad
			points[3][0] -= rad
			points[3][1] += rad
			points[4][0] += rad
			points[4][1] += rad

		elif tm == "Outside Rectangle":
			points[0][0] -= rad
			points[0][1] -= rad
			points[1][0] -= rad
			points[1][1] += rad
			points[2][0] += rad
			points[2][1] += rad
			points[3][0] += rad
			points[3][1] -= rad
			points[4][0] -= rad
			points[4][1] -= rad
			
		cd = self.getChosen(self.rbCutDir)
		if cd != "Clockwise":
			np = points[::-1]
			points = np
			
		pkt = self.getChosen(self.rbPkts)
	
		if self.settings.annotate:
			self.gcode.append("(Start point: %s)" % sp)
			self.gcode.append("(Cutting direction: %s)" % cd)
			self.gcode.append("(Tool movement: %s)" % tm)
			self.gcode.append("(Pocket: %s)" % pkt)

		if pkt == "None":
			self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
			self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % rot.rotate(points[0][0], points[0][1]))

		
		xmin = min(points[0][0], points[2][0]) + tdiam/2
		xmax = max(points[0][0], points[2][0]) - tdiam/2
		ymin = min(points[0][1], points[2][1]) + tdiam/2
		ymax = max(points[0][1], points[2][1]) - tdiam/2
		
		passes = int(math.ceil(depth/passdepth))
		
		cz = sz
		xlast = 0
		ylast = 0
		for i in range(passes):
			cz -= passdepth
			if cz < -depth:
				cz = -depth
			if self.settings.annotate:
				self.gcode.append("(Pass number %d at depth %f)" % (i, cz))
				
			if pkt == "Horizontal":
				first = True
				alt = True
				y = ymin
				self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
				self.gcode.append(("G0 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % rot.rotate(xmin, ymin))
				
				self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (cz))
				while y <= ymax:
					if not first:
						self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xlast, y))
						
					if alt:
						self.gcode.append(("G1 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xmax, y))
						xlast = xmax
					else:
						self.gcode.append(("G1 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xmin, y))
						xlast = xmin
					y += tdiam * stepover
					first = False
					alt = not alt
				
				self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
				self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % rot.rotate(points[0][0], points[0][1]))
			
			elif pkt == "Vertical":
				first = True
				alt = True
				x = xmin
				self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
				self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % rot.rotate(xmin, ymin))
				
				self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (cz))
				while x <= xmax:
					if not first:
						self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(x, ylast))
						
					if alt:
						self.gcode.append(("G1 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(x, ymax))
						ylast = ymax
					else:
						self.gcode.append(("G1 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(x, ymin))
						ylast = ymin
					x += tdiam * stepover
					first = False
					alt = not alt
				
				self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
				self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % rot.rotate(points[0][0], points[0][1]))
			
			elif pkt == "Centered":
				vertical = False
				if (xmax-xmin) > (ymax-ymin):
					ya = (ymax+ymin)/2.0
					yb = ya
					d = ymax - ya
					xa = xmin + d
					xb = xmax - d
				elif (xmax-xmin) < (ymax-ymin):
					vertical = True
					xa = (xmax+xmin)/2.0
					xb = xa
					d = xmax - xa
					ya = ymin + d
					yb = ymax - d
				else:
					xa = (xmax+xmin)/2.0
					xb = xa
					ya = (ymax+ymin)/2.0
					yb = ya
					
				self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
				self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % rot.rotate(xb, yb))
				self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (cz))
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xa, ya))
				
				d = stepover * tdiam
				while (xa-d) >= xmin:
					if cd == "Clockwise":
						self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xa-d, ya-d))
						if vertical:
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xa-d, yb+d))
						else:
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xa-d, ya+d))
						self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xb+d, yb+d))
						if vertical:
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xb+d, ya-d))
						else:
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xb+d, yb-d))
						self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xa-d, ya-d))
					else:
						self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xa-d, ya-d))
						if vertical:
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xb+d, ya-d))
						else:
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xb+d, yb-d))
						self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xb+d, yb+d))
						if vertical:
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xa-d, yb+d))
						else:
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xa-d, ya+d))
						self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(xa-d, ya-d))
					d += stepover * tdiam
				
				self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
				self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % rot.rotate(points[0][0], points[0][1]))
			
				
			self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (cz))
			for p in points[1:]:
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % rot.rotate(p[0], p[1]))
			
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
		if self.settings.annotate:
			self.gcode.append("(End object %s)" % self.viewTitle)
				
		self.gcl.updateList(self.gcode)
		self.bSave.Enable()
		self.bVisualize.Enable()
		self.setState(False, True)


