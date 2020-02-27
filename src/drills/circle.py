import wx
import math
from gcodelist import GCodeList
from cncobject import CNCObject
from validators import ValidateToolSize, ValidateMinLength, ValidateNonZero, ValidateNoEntryErrors
from settings import BTNDIM

def triangulate(p1, p2):
	dx = p2[0] - p1[0]
	dy = p2[1] - p1[1]
	d = math.sqrt(dx*dx + dy*dy)
	return d

class MainFrame(wx.Frame):
	def __init__(self, toolInfo, speedInfo, parent):
		self.parent = parent
		self.settings = parent.settings
		self.images = self.parent.images
		
		wx.Frame.__init__(self, None, size=(480, 800), title="")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = CirDrillPanel(toolInfo, speedInfo, self)
		sizer.Add(self.panel)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def okToClose(self):
		return self.panel.okToClose()
	
	def onClose(self, _):
		return self.panel.onClose(None)
		

class CirDrillPanel(wx.Panel, CNCObject):
	seqNo = 1
	def __init__(self, toolInfo, speedInfo, parent):
		self.parent = parent
		self.settings = parent.settings
		self.images = self.parent.images
		self.toolInfo = toolInfo
		
		self.modified = False
		self.unsaved = False
		self.viewTitle = "Circular Drill Pattern %d" % CirDrillPanel.seqNo
		self.titleText = "G Code Generator: %s" % self.viewTitle
		CirDrillPanel.seqNo += 1
		
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		sizer = wx.GridBagSizer(wx.HORIZONTAL)
		sizer.Add(10, 10, wx.GBPosition(0, 4))
		ln = 1
		
		self.setTitleFlag()

		t = wx.StaticText(self, wx.ID_ANY, "Diameter")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teDiameter = wx.TextCtrl(self, wx.ID_ANY, "10", style=wx.TE_RIGHT)
		sizer.Add(self.teDiameter, pos=(ln, 1), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Tool Diameter")
		td = "%6.3f" % toolInfo["diameter"]
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teToolDiam = wx.TextCtrl(self, wx.ID_ANY, td, style=wx.TE_RIGHT)
		sizer.Add(self.teToolDiam, pos=(ln, 1), flag=wx.LEFT, border=10)

		t = wx.StaticText(self, wx.ID_ANY, "Hole Diameter")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teHoleDiam = wx.TextCtrl(self, wx.ID_ANY, "3", style=wx.TE_RIGHT)
		sizer.Add(self.teHoleDiam, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Stepover")
		so = "%6.3f" % speedInfo["stepover"]
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teStepover = wx.TextCtrl(self, wx.ID_ANY, so, style=wx.TE_RIGHT)
		sizer.Add(self.teStepover, pos=(ln, 1), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=10)

		t = wx.StaticText(self, wx.ID_ANY, "Minimum space between")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teSpacing = wx.TextCtrl(self, wx.ID_ANY, "2", style=wx.TE_RIGHT)
		sizer.Add(self.teSpacing, pos=(ln, 3), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=10)
		ln += 1
		
		szOpts = wx.BoxSizer(wx.VERTICAL)
		self.cbInside = wx.CheckBox(self, wx.ID_ANY, "Inside Circle")
		self.Bind(wx.EVT_CHECKBOX, self.onChange, self.cbInside)
		szOpts.Add(self.cbInside)
		
		szOpts.AddSpacer(10)
		
		self.cbStagger = wx.CheckBox(self, wx.ID_ANY, "Staggered rows")
		self.Bind(wx.EVT_CHECKBOX, self.onChange, self.cbStagger)
		szOpts.Add(self.cbStagger)
		
		szOpts2 = wx.BoxSizer(wx.HORIZONTAL)
		szOpts2.AddSpacer(80)
		szOpts2.Add(szOpts)
		
		sizer.Add(szOpts2, pos=(ln, 0), span=(1, 2), border=5, flag=wx.TOP+wx.BOTTOM+wx.LEFT+wx.ALIGN_CENTER_VERTICAL)

		t = wx.StaticText(self, wx.ID_ANY, "Cutting Direction")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sizer.Add(self.getCuttingDirection(), pos=(ln, 3), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Depth of Cut")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teDepth = wx.TextCtrl(self, wx.ID_ANY, "1", style=wx.TE_RIGHT)
		sizer.Add(self.teDepth, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Depth/Pass")
		dpp = "%6.3f" % speedInfo["depthperpass"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.tePassDepth = wx.TextCtrl(self, wx.ID_ANY, dpp, style=wx.TE_RIGHT)
		sizer.Add(self.tePassDepth, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1
		
		self.cbRetract = wx.CheckBox(self, wx.ID_ANY, "Retract each pass")
		sizer.Add(self.cbRetract, pos=(ln, 2), span=(1,2),
				flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_HORIZONTAL, border=5)
		self.Bind(wx.EVT_CHECKBOX, self.onChange, self.cbRetract)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Center X")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teStartX = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_RIGHT)
		sizer.Add(self.teStartX, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Center Y")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teStartY = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_RIGHT)
		sizer.Add(self.teStartY, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Center Z")
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

		t = wx.StaticText(self, wx.ID_ANY, "Decimal Places")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teDecimals = wx.TextCtrl(self, wx.ID_ANY, "4", style=wx.TE_RIGHT)
		sizer.Add(self.teDecimals, pos=(ln, 1), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=10)

		t = wx.StaticText(self, wx.ID_ANY, "Measurement System")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sizer.Add(self.getMeasurementSystem(), pos=(ln, 3), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	
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
			errs.append("Center X")
		try:
			sy = float(self.teStartY.GetValue())
		except:
			errs.append("Center Y")
		try:
			sz = float(self.teStartZ.GetValue())
		except:
			errs.append("Center Z")
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
			feedxyG23 = float(self.teFeedXYG1.GetValue())
		except:
			errs.append("XY G1 Speed")
		try:
			cdiam = float(self.teDiameter.GetValue())
		except:
			errs.append("Overall Diameter")
		try:
			depth = float(self.teDepth.GetValue())
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
			hdiam = float(self.teHoleDiam.GetValue())
		except:
			errs.append("Hole Diameter")
		try:
			spacing = float(self.teSpacing.GetValue())
		except:
			errs.append("Spacing")
		try:
			stepover = float(self.teStepover.GetValue())
		except:
			errs.append("Stepover")

		if not ValidateNoEntryErrors(self, errs):
			return
		
		inside = self.cbInside.IsChecked()
		stagger = self.cbStagger.IsChecked()
		retract = self.cbRetract.IsChecked()
		
		if not ValidateToolSize(self, tdiam, hdiam, "Hole Diameter"):
			return
		
		if not ValidateMinLength(self, cdiam, hdiam + spacing, "Overall diameter", "Hole diameter + spacing"):
			return

		self.gcode = self.preamble(self.getChosen(self.rbMeas), tdiam, self.toolInfo, safez)
		
		if inside:
			radlimit = cdiam/2 - hdiam/2
		else:
			radlimit = cdiam/2
			
		minx = sx - cdiam/2
		maxx = sx + cdiam/2
		miny = sy - cdiam/2
		maxy = sy + cdiam/2
			
		cd = self.getChosen(self.rbCutDir)
		if cd == "Clockwise":
			cmd = "G2"
		else:
			cmd = "G3"
		
		nrows = int((maxy - miny)/(hdiam+spacing))
		ncols = int((maxx - minx)/(hdiam+spacing))

		if not ValidateNonZero(self, ncols, "Number of calculated columns"):
			return		
		if not ValidateNonZero(self, nrows, "Number of calculated rows"):
			return		
		
		xstep = (maxx - minx) / float(ncols)
		ystep = (maxy - miny) / float(nrows)
		
		if stagger:
			ystep *= 0.866
			nrows = int((nrows/0.866)+0.5)
		
		if self.settings.annotate:
			self.gcode.append("(Circular drill pattern center (%6.2f,%6.2f) diameter %6.2f depth from %6.2f to %6.2f)" % (sx, sy, cdiam, sz, depth))
			self.gcode.append("(Cut Direction: %s)" % cd)
			self.gcode.append("(Inside Circle: %s)" % str(inside))
			self.gcode.append("(Retract each pass: %s)" % str(retract))
			self.gcode.append("(Hole diameter: %6.2f)" % hdiam)
			self.gcode.append("(Stagger rows: %s)" % str(stagger))
			self.gcode.append("(Calculated step x/y: %6.2f/%6.2f)" % (xstep, ystep))

		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
		
		points = [(sx, sy)]
		ix = 1
		while sx + ix*xstep <= maxx:
			if ix*xstep <= radlimit:
				points = [(sx - ix*xstep, sy)] + points + [(sx + ix*xstep, sy)]
			ix += 1
			
		iy = 1
		while sy + iy*ystep <= maxy:
			rowu = []
			rowd = []
			ix = 0
			if stagger and iy%2 != 0:
				bx = xstep/2
			else:
				bx = 0
				
			while sx + ix*xstep + bx <= maxx:
				r = triangulate((0,0), (ix*xstep+bx, iy*ystep))
				if r <= radlimit:
					if bx == 0 and ix == 0:
						rowu.append((sx + ix*xstep + bx, sy + iy*ystep))
						rowd.append((sx + ix*xstep + bx, sy - iy*ystep))
					else:
						rowu = [(sx - ix*xstep - bx, sy + iy*ystep)] + rowu + [(sx + ix*xstep + bx, sy + iy*ystep)]
						rowd = [(sx - ix*xstep - bx, sy - iy*ystep)] + rowd + [(sx + ix*xstep + bx, sy - iy*ystep)]
				ix += 1

			points = rowu + points + rowd
			iy += 1
			
		passes = int(math.ceil(depth/passdepth))
		for p in points:
			self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (p[0], p[1]))
			cz = sz
			for i in range(passes):
				cz -= passdepth
				if cz < -depth:
					cz = -depth
				self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (cz))
				if self.settings.annotate:
					self.gcode.append("(Pass number %d at depth %f)" % (i, cz))
				if hdiam > tdiam:
					maxyoff = (hdiam-tdiam)/2.0
					yoff = stepover
					while True:
						if yoff > maxyoff:
							yoff = maxyoff
						self.gcode.append(("G1 Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (p[1]-yoff))
						self.gcode.append((cmd+" J"+self.fmt+" X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG23)) % (yoff, p[0], p[1]-yoff))
						if yoff >= maxyoff:
							break
						yoff += stepover
						
					self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG23)) % (p[0], p[1]))

				if retract:
					self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
					
			if not retract:
				self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
		
		if self.settings.annotate:
			self.gcode.append("(End object %s)" % self.viewTitle)
		self.gcl.updateList(self.gcode)
		self.bSave.Enable()
		self.bVisualize.Enable()
		self.setState(False, True)

