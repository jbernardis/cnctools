import wx
import math
from gcodelist import GCodeList
from cncobject import CNCObject
from validators import ValidateToolSize, ValidateMinValue, ValidateNoEntryErrors
from rotator import Rotator 
from settings import SPINSIZE

class MainFrame(wx.Frame):
	def __init__(self, toolInfo, speedInfo, parent):
		self.parent = parent
		self.settings = parent.settings
		self.images = self.parent.images
		
		wx.Frame.__init__(self, None, size=(480, 800), title="")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = RecDrillPanel(toolInfo, speedInfo, self)
		sizer.Add(self.panel)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def okToClose(self):
		return self.panel.okToClose()
	
	def onClose(self, _):
		return self.panel.onClose(None)
		

class RecDrillPanel(wx.Panel, CNCObject):
	seqNo = 1
	def __init__(self, toolInfo, speedInfo, parent):
		CNCObject.__init__(self, parent, "drill:rectangle")
		self.toolInfo = toolInfo
		
		self.modified = False
		self.unsaved = False
		self.viewTitle = "Rectangular Drill Pattern %d" % RecDrillPanel.seqNo
		self.titleText = "G Code Generator: %s" % self.viewTitle
		RecDrillPanel.seqNo += 1

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
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "angle")
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=0, min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(0)
		sc.SetDigits(digits)
		self.scAngle = sc
		self.addWidget(self.scAngle, "angle")
		sizer.Add(self.scAngle, pos=(ln, 1), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Hole Diameter")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "holediam")
		vinit = 1 if self.settings.metric else 0.25
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=vinit, min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(vinit)
		sc.SetDigits(digits)
		self.scHoleDiam = sc
		self.addWidget(self.scHoleDiam, "holediameter")
		sizer.Add(self.scHoleDiam, pos=(ln, 1), flag=wx.LEFT, border=10)

		t = wx.StaticText(self, wx.ID_ANY, "Minimum space between")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "spacing")
		vinit = 1 if self.settings.metric else 0.25
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=vinit, min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(vinit)
		sc.SetDigits(digits)
		self.scSpacing = sc
		self.addWidget(self.scSpacing, "spacing")
		sizer.Add(self.scSpacing, pos=(ln, 3), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=10)
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

		t = wx.StaticText(self, wx.ID_ANY, "Stepover")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=speedInfo["stepover"], min=0.1, max=1.0, inc=0.01, size=SPINSIZE)
		sc.SetValue(speedInfo["stepover"])
		sc.SetDigits(2)
		self.scStepover = sc
		self.addWidget(self.scStepover, "stepover")
		sizer.Add(self.scStepover, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Depth of Cut")
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

		sizer.Add(10, 10, wx.GBPosition(ln, 0))
		ln += 1

		szOpts = wx.BoxSizer(wx.VERTICAL)
		self.cbInside = wx.CheckBox(self, wx.ID_ANY, "Inside Rectangle")
		self.addWidget(self.cbInside, "inside")
		szOpts.AddSpacer(20)
		szOpts.Add(self.cbInside)
		self.Bind(wx.EVT_CHECKBOX, self.onChange, self.cbInside)
		
		self.cbPerimeter = wx.CheckBox(self, wx.ID_ANY, "Perimeter Only")
		self.addWidget(self.cbPerimeter, "perimeter")
		szOpts.AddSpacer(10)
		szOpts.Add(self.cbPerimeter)
		self.Bind(wx.EVT_CHECKBOX, self.onCbPerimeter, self.cbPerimeter)
		
		self.cbStagger = wx.CheckBox(self, wx.ID_ANY, "Staggered rows")
		self.addWidget(self.cbStagger, "stagger")
		szOpts.AddSpacer(10)
		szOpts.Add(self.cbStagger)
		self.Bind(wx.EVT_CHECKBOX, self.onChange, self.cbStagger)

		self.cbRetract = wx.CheckBox(self, wx.ID_ANY, "Retract after each pass")
		self.addWidget(self.cbRetract, "retract")
		szOpts.AddSpacer(10)
		szOpts.Add(self.cbRetract)
		self.Bind(wx.EVT_CHECKBOX, self.onChange, self.cbRetract)
		
		sizer.Add(szOpts, pos=(ln, 0), span=(2,2),
				flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_HORIZONTAL, border=5)
		
		t = wx.StaticText(self, wx.ID_ANY, "Cutting Direction")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sizer.Add(self.getCuttingDirection(), pos=(ln, 3), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	
		ln += 1
		
		t = wx.StaticText(self, wx.ID_ANY, "Starting Point")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)	
		sizer.Add(self.getStartingPoints(), pos=(ln, 3), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	
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
			sz.Add(r)
			self.addWidget(r, labels[i])
			self.rbStartPoints.append(r)
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

	def onCbPerimeter(self, _):
		self.setState(True, None)
		flag = self.cbPerimeter.IsChecked()
		self.cbStagger.Enable(not flag)
		
	def onCbAddSpeed(self, _):
		self.setState(True, None)
		flag = self.cbAddSpeed.IsChecked()
		self.scFeedXYG0.Enable(flag)
		self.scFeedXYG1.Enable(flag)
		self.scFeedZG0.Enable(flag)
		self.scFeedZG1.Enable(flag)
				
	def bGeneratePressed(self, _):
		self.bVisualize.Enable(False)
		self.bSave.Enable(False)
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
			
		addspeed = self.cbAddSpeed.IsChecked()
		feedzG0 = self.scFeedZG0.GetValue()
		feedzG1 = self.scFeedZG1.GetValue()
		feedxyG0 = self.scFeedXYG0.GetValue()
		feedxyG23 = self.scFeedXYG1.GetValue()

		stepover = self.scStepover.GetValue()
		passdepth = self.scPassDepth.GetValue()
		depth = self.scTotalDepth.GetValue()
		tdiam = self.scToolDiam.GetValue()
		hdiam = self.scHoleDiam.GetValue()
		spacing = self.scSpacing.GetValue()
		angle = self.scAngle.GetValue()

		try:
			height = float(self.teHeight.GetValue())
		except:
			errs.append("Height")		
		try:
			width = float(self.teWidth.GetValue())
		except:
			errs.append("Width")		
					
		if not ValidateNoEntryErrors(self, errs):
			return
			
		if not ValidateToolSize(self, tdiam, hdiam, "Hole Diameter"):
			return

		if not ValidateMinValue(self, height, hdiam+spacing, "Height", "Hole Diameter + Spacing"):
			return

		if not ValidateMinValue(self, width, hdiam+spacing, "Width", "Hole Diameter + Spacing"):
			return
			
		if self.databaseToolDiam == tdiam:
			toolname = self.toolInfo["name"]
		else:
			toolname = None
			
		self.gcode = self.preamble(self.settings, self.viewTitle, tdiam, toolname, self.settings.metric)					
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % safez)

		sp = self.getChosen(self.rbStartPoints)
		if sp == "Upper Left":
			sy -= height
		elif sp == "Upper Right":
			sy -= height
			sx -= width
		elif sp == "Lower Right":
			sx -= width
		elif sp == "Center":
			sx -= width/2
			sy -= height/2


		perimeteronly = self.cbPerimeter.IsChecked()
		inside = self.cbInside.IsChecked()
		if perimeteronly:
			stagger = False
		else:
			stagger = self.cbStagger.IsChecked()
		retract = self.cbRetract.IsChecked()
		
		if inside:
			minx = sx + hdiam/2
			maxx = sx + width - hdiam/2
			miny = sy + hdiam/2
			maxy = sy + height - hdiam/2
		else:
			minx = sx
			maxx = sx + width
			miny = sy
			maxy = sy + height
			
		cd = self.getChosen(self.rbCutDir)
		if cd == "Clockwise":
			cmd = "G2"
		else:
			cmd = "G3"
		
		nrows = int((maxy - miny)/(hdiam+spacing))
		ncols = int((maxx - minx)/(hdiam+spacing))
		
		xstep = (maxx - minx) / float(ncols)
		ystep = (maxy - miny) / float(nrows)
		
		if stagger:
			ystep *= 0.866
			nrows = int((nrows/0.866)+0.5)
		
		cx = minx
		cy = miny

		rot = None		
		if angle != 0:
			rot = Rotator(angle)
		
		if self.settings.annotate:
			self.gcode.append("(Rectangular drill pattern start (%6.2f,%6.2f) height %6.2f width %6.2f depth from %6.2f to %6.2f)" % (sx, sy, height, width, sz, depth))
			self.gcode.append("(Starting point: %s)" % sp)
			self.gcode.append("(Cut Direction: %s)" % cd)
			self.gcode.append("(Inside Circle: %s)" % str(inside))
			self.gcode.append("(Perimeter Only: %s)" % str(perimeteronly))
			self.gcode.append("(Retract each pass: %s)" % str(retract))
			self.gcode.append("(Hole diameter: %6.2f)" % hdiam)
			self.gcode.append("(Stagger rows: %s)" % str(stagger))
			self.gcode.append("(Calculated step x/y: %6.2f/%6.2f)" % (xstep, ystep))
		
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
		
		passes = int(math.ceil(depth/passdepth))
		maxyoff = hdiam/2-tdiam/2
		for iy in range(nrows+1):
			for ix in range(ncols+1):
				includeHole = False
				if not perimeteronly:
					if cx <= maxx and cy <= maxy:
						includeHole = True
				else:
					if ix == 0 or ix == ncols or iy == 0 or iy == nrows:
						includeHole = True
						
				if includeHole:
					if rot is None:
						nx = cx
						ny = cy
					else:
						nx, ny = rot.rotate(cx, cy)
						
					self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (nx, ny))
					cz = sz
					for i in range(passes):
						cz -= passdepth
						if cz < -depth:
							cz = -depth
						if self.settings.annotate:
							self.gcode.append("(Pass number %d at depth %f)" % (i, cz))
						self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (cz))
						if hdiam > tdiam:
							maxyoff = (hdiam-tdiam)/2.0
							yoff = stepover
							while True:
								if yoff > maxyoff:
									yoff = maxyoff
								self.gcode.append(("G1 Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (ny-yoff))
								self.gcode.append((cmd+" J"+self.fmt+" X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG23)) % (yoff, nx, ny-yoff))
								if yoff >= maxyoff:
									break
								yoff += stepover
								
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG23)) % (nx, ny))
							
						if retract:
							self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
					
					if not retract:
						self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))

				cx += xstep
			cy += ystep
			if stagger and iy%2 == 0:
				cx = minx + xstep/2
			else:
				cx = minx
				
		if self.settings.annotate:
			self.gcode.append("(End object %s)" % self.viewTitle)
		self.gcl.updateList(self.gcode)
		self.setState(False, True)
		self.bVisualize.Enable()
		self.bSave.Enable()

