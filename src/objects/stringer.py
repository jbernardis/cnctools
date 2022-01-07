import wx
import math
from gcodelist import GCodeList
from cncobject import CNCObject
from rotator import Rotator
from settings import SPINSIZE
from validators import ValidateNoEntryErrors


class MainFrame(wx.Frame):
	def __init__(self, toolInfo, speedInfo, parent):
		self.parent = parent
		self.settings = parent.settings
		self.images = self.parent.images
		
		wx.Frame.__init__(self, None, size=(480, 800), title="")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = StringerPanel(toolInfo, speedInfo, self)
		sizer.Add(self.panel)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def okToClose(self):
		return self.panel.okToClose()
	
	def onClose(self, _):
		return self.panel.onClose(None)

class StringerPanel(wx.Panel, CNCObject):
	seqNo = 1
	def __init__(self, toolInfo, speedInfo, parent):
		CNCObject.__init__(self, parent, "object:stringer")
		self.toolInfo = toolInfo
		
		self.modified = False
		self.unsaved = False
		self.viewTitle = "Stair Stringer %d" % StringerPanel.seqNo
		self.titleText = "G Code Generator: %s" % self.viewTitle
		StringerPanel.seqNo += 1
		
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		sizer = wx.GridBagSizer(wx.HORIZONTAL)
		sizer.Add(10, 10, wx.GBPosition(0, 4))
		ln = 1
		
		self.setTitleFlag()

		t = wx.StaticText(self, wx.ID_ANY, "Rise")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.rise = 2.5
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "rise")
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=self.rise, min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(self.rise)
		sc.SetDigits(digits)
		self.scRise = sc
		self.addWidget(self.scRise, "rise")
		sizer.Add(self.scRise, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Run")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)	
		self.run = 3.0	
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "run")
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=self.run, min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(self.run)
		sc.SetDigits(digits)
		self.scRun = sc
		self.addWidget(self.scRun, "run")
		sizer.Add(self.scRun, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Angle")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.stAngle = wx.StaticText(self, wx.ID_ANY, "")
		sizer.Add(self.stAngle, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		self.cbRotate = wx.CheckBox(self, wx.ID_ANY, "Rotate to horizontal")
		self.addWidget(self.cbRotate, "rotate")
		sizer.Add(self.cbRotate, pos=(ln, 2), span=(1,2),
				flag=wx.LEFT, border=10)
		self.Bind(wx.EVT_CHECKBOX, self.onCbRotate, self.cbRotate)
		self.cbRotate.SetValue(False)
		ln += 1
		
		sizer.Add(20, 20, wx.GBPosition(ln, 0))
		ln += 1
		
		t = wx.StaticText(self, wx.ID_ANY, "Number of steps")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)	
		self.count = 5	
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=self.count, size=SPINSIZE)
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "steps")
		sc.SetRange(vmin, vmax)
		sc.SetValue(self.count)
		self.scCount = sc
		self.addWidget(self.scCount, "count")
		sizer.Add(self.scCount, pos=(ln, 1), flag=wx.LEFT, border=10)
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
		self.Bind(wx.EVT_SPINCTRL, self.onChange)
		self.Bind(wx.EVT_RADIOBUTTON, self.onChange)

		self.Bind(wx.EVT_SPINCTRL, self.onRiseRunSpin, self.scRise)
		self.Bind(wx.EVT_TEXT, self.onRiseRunText, self.scRise)
		self.Bind(wx.EVT_SPINCTRL, self.onRiseRunSpin, self.scRun)
		self.Bind(wx.EVT_TEXT, self.onRiseRunText, self.scRun)
		
		self.setAngle()
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def onRiseRunSpin(self, _):
		self.setState(True, False)
		self.run = self.scRun.GetValue()
		self.rise = self.scRise.GetValue() 
		
		self.setAngle()
		
	def onRiseRunText(self, _):
		self.setState(True, False)
		self.run = self.scRun.GetValue()
		self.rise = self.scRise.GetValue() 
		
		self.setAngle()
		
	def setAngle(self):
		self.angle = math.degrees(math.atan(self.rise/self.run))
		sangle = "%6.2f degrees" % (self.angle)
		self.stAngle.SetLabel(sangle)
		
		
	def onCbRotate(self, _):
		self.setState(True, False)
		
	def onCbAddSpeed(self, _):
		self.setState(True, False)
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
		

		safez = self.scSafeZ.GetValue()
			
		addspeed = self.cbAddSpeed.IsChecked()
		feedzG0 = self.scFeedZG0.GetValue()
		feedzG1 = self.scFeedZG1.GetValue()
		feedxyG0 = self.scFeedXYG0.GetValue()
		feedxyG1 = self.scFeedXYG1.GetValue()
		
		passdepth = self.scPassDepth.GetValue()
		depth = self.scTotalDepth.GetValue()
		tdiam = self.scToolDiam.GetValue()

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
		try:
			self.rise = float(self.scRise.GetValue())
		except:
			errs.append("Rise")	
		try:
			self.run = float(self.scRun.GetValue())
		except:
			errs.append("Run")	
		try:
			count = int(self.scCount.GetValue())
		except:
			errs.append("Count")	
			
		if not ValidateNoEntryErrors(self, errs):
			return
		
		self.setAngle()
		rotate = self.cbRotate.GetValue()
		if rotate:
				rot = Rotator(-self.angle)

		self.tDiam = tdiam
		if self.toolInfo["diameter"] == tdiam:
			toolname = self.toolInfo["name"]
		else:
			toolname = None

		self.gcode = self.preamble(self.settings, self.viewTitle, tdiam, toolname, self.settings.metric)					
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % safez)
		
		if self.settings.annotate:
			self.gcode.append("(Stair Stringer step count %d, rise %6.2f/run %6.2f%s)" % (count, self.rise, self.run, " rotated to horizontal" if rotate else ""))
		
		passes = int(math.ceil(depth/passdepth))

		offsetx = sx
		offsety = sy
		sx = 0
		sy = 0
				
		ptsa = [
			[sx, sy + self.rise ],
			[sx + self.run * count, sy + self.rise * (count+1)],
			[sx + self.run * (count+1), sy + self.rise * (count+1)]
		]
		if rotate:
			ptsa = [rot.rotate(x, y) for x, y in ptsa]
			
		ptsa = [[x+offsetx, y+offsety] for x, y in ptsa]
			
		cz = sz
		if self.settings.annotate:
			self.gcode.append("(Upper Edge)")
			
		for i in range(passes):
			cz -= passdepth
			if cz < -depth:
				cz = -depth
			if self.settings.annotate:
				self.gcode.append("(Pass number %d at depth %f)" % (i, cz))
				
			ax = ptsa[0][0]
			ay = ptsa[0][1]
			self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
			self.gcode.append(("G0 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (ax, ay))
			self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % cz)
			for p in ptsa[1:]:
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (p[0], p[1]))

		points = [[sx, sy], [sx+self.run, sy]]
		x = sx+self.run
		y = sy			
		for _ in range(count):
			points.append([x, y+self.rise])
			points.append([x+self.run, y+self.rise])
			y += self.rise
			x += self.run
		if rotate:
			points = [rot.rotate(x, y) for x, y in points]
			
		points = [[x+offsetx, y+offsety] for x, y in points]
		
		cz = sz
		if self.settings.annotate:
			self.gcode.append("(Stringer)")
		for i in range(passes):
			cz -= passdepth
			if cz < -depth:
				cz = -depth
			if self.settings.annotate:
				self.gcode.append("(Pass number %d at depth %f)" % (i, cz))
				
			ax = points[0][0]
			ay = points[0][1]
			self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
			self.gcode.append(("G0 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (ax, ay))
			self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % cz)
			for p in points[1:]:
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (p[0], p[1]))
				
		ptsb = [
			[sx, sy - self.rise],
			[sx + self.run, sy - self.rise],
			[sx + self.run * (count+1), sy + self.rise * (count-1)]
		]
		if rotate:
			ptsb = [rot.rotate(x, y) for x, y in ptsb]
			
		ptsb = [[x+offsetx, y+offsety] for x, y in ptsb]

		cz = sz
		if self.settings.annotate:
			self.gcode.append("(Lower Edge)")
		for i in range(passes):
			cz -= passdepth
			if cz < -depth:
				cz = -depth
			if self.settings.annotate:
				self.gcode.append("(Pass number %d at depth %f)" % (i, cz))
				
			ax = ptsb[0][0]
			ay = ptsb[0][1]
			self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
			self.gcode.append(("G0 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (ax, ay))
			self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % cz)
			for p in ptsb[1:]:
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (p[0], p[1]))

		
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
		if self.settings.annotate:
			self.gcode.append("(End object %s)" % self.viewTitle)
				
		self.gcl.updateList(self.gcode)
		self.bSave.Enable()
		self.bVisualize.Enable()
		self.setState(False, True)


