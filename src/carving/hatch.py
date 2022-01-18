import math
import wx
from cncobject import CNCObject
from gcodelist import GCodeList
from validators import ValidateNoEntryErrors
from settings import SPINSIZE

def hatch(angle, minx, miny, maxx, maxy, gap, offsety):
	run = gap/math.sin(math.radians(angle))
	rise = math.tan(math.radians(angle)) * run 
	slope = float(rise)/float(run)

	intercepts = [ miny - slope*minx, miny - slope*maxx, maxy - slope*minx, maxy - slope*maxx ]
	mini = min(intercepts)
	maxi = max(intercepts)
	
	if offsety < 0:
		maxi = maxi + math.fabs(rise) + offsety
		mini += offsety
	elif offsety > 0:
		mini = mini - math.fabs(rise) + offsety
		maxi += offsety
	
	intercept = mini
	plist = []
	while intercept < maxi:
		p = []
		
		y = slope * minx + intercept
		if y >= miny and y <= maxy:
			p.append([minx, y])
			
		x = (miny - intercept) / slope
		if x >= minx and x <= maxx:
			p.append([x, miny])
		
		x = (maxy - intercept) / slope
		if x >= minx and x <= maxx:
			p.append([x, maxy])
		
		y = slope * maxx + intercept
		if y >= miny and y <= maxy:
			p.append([maxx, y])
			
		if len(p) == 2:
			if p[0][0] != p[1][0] or p[0][1] != p[1][1]:
				if p[1][0] < p[0][0]:
					p = [p[1], p[0]]
				plist.append(p)
		
		intercept += math.fabs(rise)
		
	return plist

class MainFrame(wx.Frame):
	def __init__(self, toolInfo, speedInfo, parent):
		self.parent = parent
		self.settings = parent.settings
		self.images = self.parent.images
		
		wx.Frame.__init__(self, None, size=(480, 800), title="")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = GridPanel(toolInfo, speedInfo, self)
		sizer.Add(self.panel)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def okToClose(self):
		return self.panel.okToClose()
	
	def onClose(self, _):
		return self.panel.onClose(None)
		

class GridPanel(wx.Panel, CNCObject):
	seqNo = 1
	def __init__(self, toolInfo, speedInfo, parent):
		CNCObject.__init__(self, parent, "carve:hatch")
		self.toolInfo = toolInfo
		
		self.modified = False
		self.unsaved = False
		self.viewTitle = "Cross Hatch Pattern %d" % GridPanel.seqNo
		self.titleText = "G Code Generator: %s" % self.viewTitle
		GridPanel.seqNo += 1
		
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		sizer = wx.GridBagSizer(wx.HORIZONTAL)
		sizer.Add(10, 10, wx.GBPosition(0, 4))
		ln = 1
		
		self.setTitleFlag()

		t = wx.StaticText(self, wx.ID_ANY, "Total X Size")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teSizeX = wx.TextCtrl(self, wx.ID_ANY, "100", style=wx.TE_RIGHT)
		self.addWidget(self.teSizeX, "sizex")
		sizer.Add(self.teSizeX, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Total Y Size")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teSizeY = wx.TextCtrl(self, wx.ID_ANY, "100", style=wx.TE_RIGHT)
		self.addWidget(self.teSizeY, "sizey")
		sizer.Add(self.teSizeY, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1
		
		t = wx.StaticText(self, wx.ID_ANY, "Angle")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teAngle = wx.TextCtrl(self, wx.ID_ANY, "45", style=wx.TE_RIGHT)
		self.addWidget(self.teAngle, "angle")
		sizer.Add(self.teAngle, pos=(ln, 1), flag=wx.LEFT, border=10)

		t = wx.StaticText(self, wx.ID_ANY, "Y Offset")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teYOffset= wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_RIGHT)
		self.addWidget(self.teYOffset, "yoffset")
		sizer.Add(self.teYOffset, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Perpendicular Gap")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teGap = wx.TextCtrl(self, wx.ID_ANY, "10", style=wx.TE_RIGHT)
		self.addWidget(self.teGap, "gap")
		sizer.Add(self.teGap, pos=(ln, 1), flag=wx.LEFT, border=10)
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
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "safez")
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=self.settings.safez, min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(self.settings.safez)
		sc.SetDigits(digits)
		self.scSafeZ = sc
		self.addWidget(self.scSafeZ, "safez")
		sizer.Add(self.scSafeZ, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1
		
		t = wx.StaticText(self, wx.ID_ANY, "Tool Diameter")
		td = self.resolveToolDiameter(toolInfo)
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "tooldiam")
		self.databaseToolDiam = round(td, digits)
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=td, min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(td)
		sc.SetDigits(digits)
		self.scToolDiam = sc
		self.addWidget(self.scToolDiam, "tooldiameter")
		sizer.Add(self.scToolDiam, pos=(ln, 1), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Total Depth")
		td = self.settings.totaldepth
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "totaldepth")
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=td, min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(td)
		sc.SetDigits(digits)
		self.scTotalDepth = sc
		self.addWidget(self.scTotalDepth, "depth")
		sizer.Add(self.scTotalDepth, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Depth/Pass")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "passdepth")
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=speedInfo["depthperpass"], min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(speedInfo["depthperpass"])
		sc.SetDigits(digits)
		self.scPassDepth = sc
		self.addWidget(self.scPassDepth, "passdepth")
		sizer.Add(self.scPassDepth, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1
		
		t = wx.StaticText(self, wx.ID_ANY, "Starting Point")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)	
		sizer.Add(self.getStartingPoints(), pos=(ln, 1), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	

		t = wx.StaticText(self, wx.ID_ANY, "Add Border")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.cbBorder = wx.CheckBox(self, wx.ID_ANY)
		self.addWidget(self.cbBorder, "border")
		self.Bind(wx.EVT_CHECKBOX, self.onChange, self.cbBorder)
		sizer.Add(self.cbBorder, pos=(ln, 3), flag=wx.LEFT+wx.RIGHT+wx.ALIGN_CENTER_VERTICAL, border=10)
		ln += 1
		
		sizer.Add(20, 20, wx.GBPosition(ln, 0))
		ln += 1

		self.cbAddSpeed = wx.CheckBox(self, wx.ID_ANY, "Add Speed Parameter")
		self.addWidget(self.cbAddSpeed, "addspeed")
		sizer.Add(self.cbAddSpeed, pos=(ln, 0), span=(1,4),
				flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_HORIZONTAL, border=5)
		self.Bind(wx.EVT_CHECKBOX, self.onCbAddSpeed, self.cbAddSpeed)
		self.cbAddSpeed.SetValue(self.settings.addspeed)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate XY (G0)")
		g0xy = speedInfo["G0XY"]
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=g0xy, size=SPINSIZE)
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "feedxyg0")
		sc.SetRange(vmin, vmax)
		sc.SetValue(g0xy)
		self.scFeedXYG0 = sc
		self.addWidget(self.scFeedXYG0, "feedXYG0")
		sizer.Add(self.scFeedXYG0, pos=(ln, 1), flag=wx.LEFT, border=10)		
		
		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate XY (G1)")
		g1xy = speedInfo["G1XY"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=g1xy, size=SPINSIZE)
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "feedxyg1")
		sc.SetRange(vmin, vmax)
		sc.SetValue(g1xy)
		self.scFeedXYG1 = sc
		self.addWidget(self.scFeedXYG1, "feedXYG1")
		sizer.Add(self.scFeedXYG1, pos=(ln, 3), flag=wx.LEFT, border=10)		
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate Z (G0)")
		g0z = speedInfo["G0Z"]
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=g0z, size=SPINSIZE)
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "feedzg0")
		sc.SetRange(vmin, vmax)
		sc.SetValue(g0z)
		self.scFeedZG0 = sc
		self.addWidget(self.scFeedZG0, "feedZG0")
		sizer.Add(self.scFeedZG0, pos=(ln, 1), flag=wx.LEFT, border=10)		
		
		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate Z (G1)")
		g1z = speedInfo["G1Z"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=g1z, size=SPINSIZE)
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "feedzg1")
		sc.SetRange(vmin, vmax)
		sc.SetValue(g1z)
		self.scFeedZG1 = sc
		self.addWidget(self.scFeedZG1, "feedZG1")
		sizer.Add(self.scFeedZG1, pos=(ln, 3), flag=wx.LEFT, border=10)		

		self.scFeedXYG0.Enable(self.settings.addspeed)
		self.scFeedXYG1.Enable(self.settings.addspeed)
		self.scFeedZG0.Enable(self.settings.addspeed)
		self.scFeedZG1.Enable(self.settings.addspeed)
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
		self.Bind(wx.EVT_SPINCTRL, self.onChange)
		
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

	def onCbAddSpeed(self, _):
		self.setState(True, None)
		flag = self.cbAddSpeed.IsChecked()
		self.scFeedXYG0.Enable(flag)
		self.scFeedXYG1.Enable(flag)
		self.scFeedZG0.Enable(flag)
		self.scFeedZG1.Enable(flag)
		
	def bGeneratePressed(self, _):
		self.bSave.Enable(False)
		self.bVisualize.Enable(False)
		self.gcl.clear()
		self.gcode = []
		
		self.fmt = "%%0.%df" % self.settings.decimals

		errs = []		
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
			
		safez = self.scSafeZ.GetValue()

		feedzG0 = self.scFeedZG0.GetValue()
		feedzG1 = self.scFeedZG1.GetValue()
		feedxyG0 = self.scFeedXYG0.GetValue()
		feedxyG1 = self.scFeedXYG1.GetValue()

		passdepth = self.scPassDepth.GetValue()
		self.tDiam = self.scToolDiam.GetValue()
		totaldepth = self.scTotalDepth.GetValue()

		try:
			totalx = float(self.teSizeX.GetValue())
		except:
			errs.append("Size X")
		try:
			totaly = float(self.teSizeY.GetValue())
		except:
			errs.append("Size Y")
		try:
			angle = float(self.teAngle.GetValue())
		except:
			errs.append("Angle")
		try:
			gap = float(self.teGap.GetValue())
		except:
			errs.append("Perpendicular Gap")
		try:
			yoffset = float(self.teYOffset.GetValue())
		except:
			errs.append("Y Offset")

		if not ValidateNoEntryErrors(self, errs):
			return			
			
		border = self.cbBorder.IsChecked()
		addspeed = self.cbAddSpeed.IsChecked()
		
		if self.databaseToolDiam == self.tDiam:
			toolname = self.toolInfo["name"]
		else:
			toolname = None
			
		self.gcode = self.preamble(self.settings, self.viewTitle, self.tDiam, toolname, self.settings.metric)					
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % safez)
		
		plist = hatch(angle, sx, sy, sx+totalx, sy+totaly, gap, yoffset)		
			
		sp = self.getChosen(self.rbStartPoints)
		adjx = 0
		adjy = 0
		if sp == "Upper Left":
			adjy = -totaly
		elif sp == "Upper Right":
			adjy = -totaly
			adjx = -totalx
		elif sp == "Lower Right":
			adjx = -totalx
		elif sp == "Center":
			adjx = -totalx/2
			adjy = -totaly/2
			
		points = [[[p[0][0]+adjx, p[0][1]+adjy], [p[1][0]+adjx, p[1][1]+adjy]] for p in plist]
		
		corners = [[sx+adjx, sy+adjy], [sx+adjx, sy+totaly+adjy], [sx+totalx+adjx, sy+totaly+adjy], [sx+totalx+adjx, sy+adjy]]

		passes = int(math.ceil(float(totaldepth)/float(passdepth)))
		if self.settings.annotate:
			self.gcode.append("(Cross Hatch pattern start (%6.2f,%6.2f) width %6.2f height %6.2f depth from %6.2f to %6.2f)" % (sx, sy, totalx, totaly, sz, totaldepth))
			self.gcode.append("(Start point: %s)" % sp)
			self.gcode.append("(Y offset: %6.2f)" % yoffset)
			self.gcode.append("(Cut border: %s)" % str(border))
			self.gcode.append("(Gap: %6.2f)" % gap)
			self.gcode.append("(Angle: %6.2f)" % angle)
		
		depth = 0
		flag = True
		for i in range(passes):
			depth += passdepth
			if depth > totaldepth: depth=totaldepth
			if self.settings.annotate:
				self.gcode.append("(Pass number %d at depth %f)" % (i, depth))
			
			self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % safez)
			for p in points:
				if flag:
					xa = p[0][0]
					ya = p[0][1]
					xb = p[1][0]
					yb = p[1][1]
				else:
					xa = p[1][0]
					ya = p[1][1]
					xb = p[0][0]
					yb = p[0][1]
				flag = not flag
					
				self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (xa, ya))
				self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (sz-depth))
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (xb, yb))
				self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
			
			if border:
				self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (corners[0][0], corners[0][1]))
				self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (sz-depth))
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (corners[1][0], corners[1][1]))
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (corners[2][0], corners[2][1]))
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (corners[3][0], corners[3][1]))
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (corners[0][0], corners[0][1]))
				self.gcode.append(("G0 Z"+self.fmt+""+self.speedTerm(addspeed, feedzG0)+"\n") % (safez))

		self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (sx, sy))
		if self.settings.annotate:
			self.gcode.append("(End object %s)" % self.viewTitle)
		self.gcl.updateList(self.gcode)
		self.bSave.Enable()
		self.bVisualize.Enable()
		self.setState(False, True)

	