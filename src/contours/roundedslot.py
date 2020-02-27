import wx
import math
from gcodelist import GCodeList
from cncobject import CNCObject
from validators import ValidateToolSize, ValidateRange, ValidateMinLength, ValidateNoEntryErrors
from settings import BTNDIM

class MainFrame(wx.Frame):
	def __init__(self, toolInfo, speedInfo, parent):
		self.parent = parent
		self.settings = parent.settings
		self.images = self.parent.images
		
		wx.Frame.__init__(self, None, size=(480, 800), title="")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = SlotPanel(toolInfo, speedInfo, self)
		sizer.Add(self.panel)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def okToClose(self):
		return self.panel.okToClose()
	
	def onClose(self, _):
		return self.panel.onClose(None)
		

class SlotPanel(wx.Panel, CNCObject):
	seqNo = 1
	def __init__(self, toolInfo, speedInfo, parent):
		self.parent = parent
		self.settings = parent.settings
		self.images = self.parent.images
		self.toolInfo = toolInfo
		
		self.modified = False
		self.unsaved = False
		self.viewTitle = "Rounded Slot %d" % SlotPanel.seqNo
		self.titleText = "G Code Generator: %s" % self.viewTitle
		SlotPanel.seqNo += 1
		
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		sizer = wx.GridBagSizer(wx.HORIZONTAL)
		sizer.Add(10, 10, wx.GBPosition(0, 4))
		ln = 1
		
		self.setTitleFlag()

		t = wx.StaticText(self, wx.ID_ANY, "Length")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teLength = wx.TextCtrl(self, wx.ID_ANY, "10", style=wx.TE_RIGHT)
		sizer.Add(self.teLength, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Width")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teWidth = wx.TextCtrl(self, wx.ID_ANY, "10", style=wx.TE_RIGHT)
		sizer.Add(self.teWidth, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Rotation Angle")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teAngle = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_RIGHT)
		sizer.Add(self.teAngle, pos=(ln, 1), flag=wx.LEFT, border=10)

		t = wx.StaticText(self, wx.ID_ANY, "Tool Diameter")
		td = "%6.3f" % toolInfo["diameter"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teToolDiam = wx.TextCtrl(self, wx.ID_ANY, td, style=wx.TE_RIGHT)
		sizer.Add(self.teToolDiam, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Total Depth")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teTotalDepth = wx.TextCtrl(self, wx.ID_ANY, "1", style=wx.TE_RIGHT)
		sizer.Add(self.teTotalDepth, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Depth/Pass")
		dpp = "%6.3f" % speedInfo["depthperpass"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.tePassDepth = wx.TextCtrl(self, wx.ID_ANY, dpp, style=wx.TE_RIGHT)
		sizer.Add(self.tePassDepth, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Start X")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teStartX = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_RIGHT)
		sizer.Add(self.teStartX, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Start Y")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teStartY = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_RIGHT)
		sizer.Add(self.teStartY, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Start Z")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teStartZ = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_RIGHT)
		sizer.Add(self.teStartZ, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Safe Z above surface")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teSafeZ = wx.TextCtrl(self, wx.ID_ANY, "0.5", style=wx.TE_RIGHT)
		sizer.Add(self.teSafeZ, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1
		
		self.cbAddSpeed = wx.CheckBox(self, wx.ID_ANY, "Add Speed Parameter")
		sizer.Add(self.cbAddSpeed, pos=(ln, 0), span=(1,4),
				flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_HORIZONTAL, border=5)
		self.Bind(wx.EVT_CHECKBOX, self.onCbAddSpeed, self.cbAddSpeed)
		self.cbAddSpeed.SetValue(self.settings.addspeed)
		ln += 1
		
		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate XY (G0)")
		g0xy = "%7.2f" % speedInfo["G0XY"]
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teFeedXYG0 = wx.TextCtrl(self, wx.ID_ANY, g0xy, style=wx.TE_RIGHT)
		sizer.Add(self.teFeedXYG0, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate XY (G1)")
		g1xy = "%7.2f" % speedInfo["G1XY"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teFeedXYG1 = wx.TextCtrl(self, wx.ID_ANY, g1xy, style=wx.TE_RIGHT)
		sizer.Add(self.teFeedXYG1, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate Z (G0)")
		g0z = "%7.2f" % speedInfo["G0Z"]
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teFeedZG0 = wx.TextCtrl(self, wx.ID_ANY, g0z, style=wx.TE_RIGHT)
		sizer.Add(self.teFeedZG0, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate Z (G1)")
		g1z = "%7.2f" % speedInfo["G1Z"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teFeedZG1 = wx.TextCtrl(self, wx.ID_ANY, g1z, style=wx.TE_RIGHT)
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

		self.cbPocket = wx.CheckBox(self, wx.ID_ANY, "Pocket")
		sizer.Add(self.cbPocket, pos=(ln, 0), span=(1,2),
				flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_HORIZONTAL, border=5)
		self.Bind(wx.EVT_CHECKBOX, self.onChange, self.cbPocket)

		t = wx.StaticText(self, wx.ID_ANY, "Stepover")
		so = "%6.3f" % speedInfo["stepover"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teStepOver = wx.TextCtrl(self, wx.ID_ANY, so, style=wx.TE_RIGHT)
		sizer.Add(self.teStepOver, pos=(ln, 3), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=10)
		ln += 1
		
		t = wx.StaticText(self, wx.ID_ANY, "Decimal Places")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teDecimals = wx.TextCtrl(self, wx.ID_ANY, "4", style=wx.TE_RIGHT)
		sizer.Add(self.teDecimals, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		sizer.Add(20, 20, wx.GBPosition(ln, 0))
		ln += 1
		
		bsz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bGenerate = wx.BitmapButton(self, wx.ID_ANY, self.images.pngGcode, size=BTNDIM)
		self.bGenerate.SetToolTip("Generate G Code")
		bsz.Add(self.bGenerate)
		self.Bind(wx.EVT_BUTTON, self.bGeneratePressed, self.bGenerate)
		
		bsz.AddSpacer(20)
		
		self.bSave = wx.BitmapButton(self, wx.ID_ANY, self.images.pngFilesaveas, size=BTNDIM)
		self.bSave.SetToolTip("Save G Code")
		bsz.Add(self.bSave)
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
		self.bSave.Disable()
		
		bsz.AddSpacer(20)
		
		self.bVisualize = wx.BitmapButton(self, wx.ID_ANY, self.images.pngView, size=BTNDIM)
		self.bVisualize.SetToolTip("Visualize G Code")
		bsz.Add(self.bVisualize)
		self.Bind(wx.EVT_BUTTON, self.bVisualizePressed, self.bVisualize)
		self.bVisualize.Disable()
		
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
			sz.Add(r)
			self.rbStartPoints.append(r)
		return sz
		
	def getToolMovement(self):
		labels = ["On Perimeter", "Outside", "Inside"]
		self.rbToolMove = []
		sz = wx.BoxSizer(wx.VERTICAL)
		for i in range(len(labels)):
			if i == 0:
				style = wx.RB_GROUP
			else:
				style = 0
			r = wx.RadioButton(self, wx.ID_ANY, labels[i], style=style)
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
			sz.Add(r)
			self.rbMeas.append(r)
		if self.settings.metric:
			self.setChosen(self.rbMeas, "Metric")
		else:
			self.setChosen(self.rbMeas, "Imperial")
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
			self.safez = float(self.teSafeZ.GetValue())
		except:
			errs.append("Safe Z")
			
		self.addspeed = self.cbAddSpeed.IsChecked()
		try:
			self.feedzG0 = float(self.teFeedZG0.GetValue())
		except:
			errs.append("Z G0 Speed")
		try:
			self.feedzG1 = float(self.teFeedZG1.GetValue())
		except:
			errs.append("Z G1 Speed")
		try:
			self.feedxyG0 = float(self.teFeedXYG0.GetValue())
		except:
			errs.append("XY G0 Speed")
		try:
			self.feedxyG1 = float(self.teFeedXYG1.GetValue())
		except:
			errs.append("XY G1 Speed")
		try:
			length = float(self.teLength.GetValue())
		except:
			errs.append("Length")
		try:
			width = float(self.teWidth.GetValue())
		except:
			errs.append("Width")
		try:
			self.depth = float(self.teTotalDepth.GetValue())
		except:
			errs.append("Depth")
		try:
			self.passdepth = float(self.tePassDepth.GetValue())
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
			
		if not ValidateToolSize(self, tdiam, length, "Length"):
			return
		if not ValidateToolSize(self, tdiam, width, "Width"):
			return
		
		if not ValidateRange(self, stepover, 0.001, 1.0, "Stepover", "0 < x <= 1.0"):
			return
		
		if not ValidateMinLength(self, length, width, "Length", "Width"):
			return

		self.gcode = self.preamble(self.getChosen(self.rbMeas), tdiam, self.toolInfo, self.safez)
		
		self.tDiam = tdiam
		if self.settings.annotate:
			self.gcode.append("(Rounded slot start (%6.2f,%6.2f) length %6.2f width %6.2f depth from %6.2f to %6.2f)" % (sx, sy, width, length, sz, self.depth))
		
		length -= width
			
		points = [[sx, sy], [sx, sy+width], [sx+length, sy+width], [sx+length, sy]]
		centers = [[sx, sy+width/2], [sx+length, sy+width/2]]
			
		sp = self.getChosen(self.rbStartPoints)
		adjx = 0
		adjy = 0
		if sp == "Upper Left":
			adjy = -width
		elif sp == "Upper Right":
			adjy = -width
			adjx = -length
		elif sp == "Lower Right":
			adjx = -length
		elif sp == "Center":
			adjx = -length/2
			adjy = -width/2
			
		for p in points:
			p[0] += adjx
			p[1] += adjy
		for c in centers:
			c[0] += adjx
			c[1] += adjy
			
		tm = self.getChosen(self.rbToolMove)
		rad = float(tdiam)/2.0
		if tm == "Inside":
			points[0][1] += rad
			points[1][1] -= rad
			points[2][1] -= rad
			points[3][1] += rad

		elif tm == "Outside":
			points[0][1] -= rad
			points[1][1] += rad
			points[2][1] += rad
			points[3][1] -= rad

		np = []	
		nc = []
		cosv = math.cos(math.radians(angle))
		sinv = math.sin(math.radians(angle))		
		for p in points:
			np.append([p[0]*cosv-p[1]*sinv, p[0]*sinv+p[1]*cosv])
		for c in centers:
			nc.append([c[0]*cosv-c[1]*sinv, c[0]*sinv+c[1]*cosv])
			
		cd = self.getChosen(self.rbCutDir)
		clockwise = True
		if cd != "Clockwise":
			clockwise = False
			
		pkt = self.cbPocket.IsChecked()
	
		if self.settings.annotate:
			self.gcode.append("(Start point: %s)" % sp)
			self.gcode.append("(Cutting direction: %s)" % cd)
			self.gcode.append("(Tool movement: %s)" % tm)
			self.gcode.append("(Pocket: %s)" % pkt)
			
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG0)) % (self.safez))
		
		passes = int(math.ceil(self.depth/self.passdepth))
		
		cz = sz
		for i in range(passes):
			cz -= self.passdepth
			if cz < -self.depth:
				cz = -self.depth
			if self.settings.annotate:
				self.gcode.append("(Pass number %d at depth %f)" % (i, cz))
			
			if pkt:
				self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG0)) % (nc[1][0], nc[1][1]))
				self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG1)) % (cz))
				self.gcode.append(("G1 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) %
					(nc[0][0],nc[0][1]))
				
				d = centers[0][1] - points[0][1]
				cd = stepover*tdiam
				while cd < d:
					pc = [p for p in centers]
					pp = [[pc[0][0], pc[0][1]-cd], [pc[0][0], pc[0][1]+cd], [pc[1][0], pc[1][1]+cd], [pc[1][0], pc[1][1]-cd]]
					npp = []
					npc = []
					for p in pp:
						npp.append([p[0]*cosv-p[1]*sinv, p[0]*sinv+p[1]*cosv])
					for c in pc:
						npc.append([c[0]*cosv-c[1]*sinv, c[0]*sinv+c[1]*cosv])
					self.gcode.append(("G1 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) %
						(npp[0][0],npp[0][1]))
					self.loop(npp, npc, clockwise)
					cd += stepover*tdiam
				
				
				self.gcode.append(("G1 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) %
					(np[0][0],np[0][1]))
			else:
				self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG0)) % (np[0][0], np[0][1]))
				self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG1)) % (cz))
			
			self.loop(np, nc, clockwise)
		
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG0)) % (self.safez))
		if self.settings.annotate:
			self.gcode.append("(End object %s)" % self.viewTitle)
				
		self.gcl.updateList(self.gcode)
		self.bSave.Enable()
		self.bVisualize.Enable()
		self.setState(False, True)
		
	def loop(self, points, centers, clockwise):
		cmd = "G3"
		if clockwise:
			cmd = "G2"

		if clockwise:
			self.gcode.append((cmd+" I"+self.fmt+" J"+self.fmt+" X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) %
					(centers[0][0]-points[0][0],centers[0][1]-points[0][1],points[1][0],points[1][1]))
			self.gcode.append(("G1 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) %
					(points[2][0],points[2][1]))
			self.gcode.append((cmd+" I"+self.fmt+" J"+self.fmt+" X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) %
					(centers[1][0]-points[2][0],centers[1][1]-points[2][1],points[3][0],points[3][1]))
			self.gcode.append(("G1 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) %
					(points[0][0],points[0][1]))
		else:
			self.gcode.append(("G1 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) %
					(points[3][0],points[3][1]))
			self.gcode.append((cmd+" I"+self.fmt+" J"+self.fmt+" X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) %
					(centers[1][0]-points[3][0],centers[1][1]-points[3][1],points[2][0],points[2][1]))
			self.gcode.append(("G1 X"+self.fmt+ " Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) %
					(points[1][0],points[1][1]))
			self.gcode.append((cmd+" I"+self.fmt+" J"+self.fmt+" X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) %
					(centers[0][0]-points[1][0],centers[0][1]-points[1][1],points[0][0],points[0][1]))

