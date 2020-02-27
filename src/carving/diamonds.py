import wx
import math
from cncobject import CNCObject
from gcodelist import GCodeList
from validators import ValidateNoEntryErrors
from settings import BTNDIM

class MainFrame(wx.Frame):
	def __init__(self, toolInfo, speedInfo, parent):
		self.parent = parent
		self.settings = parent.settings
		self.images = self.parent.images
		
		wx.Frame.__init__(self, None, size=(480, 800), title="")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = DiaPattPanel(toolInfo, speedInfo, self)
		sizer.Add(self.panel)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def okToClose(self):
		return self.panel.okToClose()
	
	def onClose(self, _):
		return self.panel.onClose(None)
		
class DiaPattPanel(wx.Panel, CNCObject):
	seqNo = 1
	def __init__(self, toolInfo, speedInfo, parent):
		self.parent = parent
		self.settings = parent.settings
		self.images = self.parent.images
		self.toolInfo = toolInfo
		
		self.modified = False
		self.unsaved = False
		self.viewTitle = "Diamond Pattern %d" % DiaPattPanel.seqNo
		self.titleText = "G Code Generator: %s" % self.viewTitle
		DiaPattPanel.seqNo += 1
		
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		sizer = wx.GridBagSizer(wx.HORIZONTAL)
		sizer.Add(10, 10, wx.GBPosition(0, 4))
		ln = 1
		
		self.setTitleFlag()

		t = wx.StaticText(self, wx.ID_ANY, "Total X Size")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teSizeX = wx.TextCtrl(self, wx.ID_ANY, "10", style=wx.TE_RIGHT)
		sizer.Add(self.teSizeX, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Total Y Size")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teSizeY = wx.TextCtrl(self, wx.ID_ANY, "10", style=wx.TE_RIGHT)
		sizer.Add(self.teSizeY, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Segments")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teSegments = wx.TextCtrl(self, wx.ID_ANY, "10", style=wx.TE_RIGHT)
		sizer.Add(self.teSegments, pos=(ln, 1), flag=wx.LEFT, border=10)
		
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

		t = wx.StaticText(self, wx.ID_ANY, "Measurement System")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sizer.Add(self.getMeasurementSystem(), pos=(ln, 3), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Add Border")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.cbBorder = wx.CheckBox(self, wx.ID_ANY)
		sizer.Add(self.cbBorder, pos=(ln, 1), flag=wx.LEFT+wx.RIGHT+wx.ALIGN_CENTER_VERTICAL, border=10)
		self.Bind(wx.EVT_CHECKBOX, self.onChange, self.cbBorder)

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

	def onCbAddSpeed(self, evt):
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
			errs.append("Decimal places")
		
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
			totalx = float(self.teSizeX.GetValue())
		except:
			errs.append("Size X")
		try:
			totaly = float(self.teSizeY.GetValue())
		except:
			errs.append("Size Y")
		try:
			totaldepth = float(self.teTotalDepth.GetValue())
		except:
			errs.append("Depth")
		try:
			passdepth = float(self.tePassDepth.GetValue())
		except:
			errs.append("Depth per Pass")
		try:
			segments = int(self.teSegments.GetValue())
		except:
			errs.append("Segments")
		try:
			self.tDiam = float(self.teToolDiam.GetValue())
		except:
			errs.append("Tool Diameter")
			
		if not ValidateNoEntryErrors(self, errs):
			return

		self.gcode = self.preamble(self.getChosen(self.rbMeas), self.tDiam, self.toolInfo, safez)
					
		border = self.cbBorder.IsChecked()
		addspeed = self.cbAddSpeed.IsChecked()
		
		sizex = totalx / segments
		sizey = totaly / segments
			
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
			
		xvals = [sx + i*sizex + adjx for i in range(segments+1)]
		yvals = [sy + i*sizey + adjy for i in range(segments+1)]
		
		points = []
		
		for i in range(1, segments):
			points.append([xvals[0], yvals[segments-i], xvals[i], yvals[segments]])
			
		points.append([xvals[0], yvals[0], xvals[segments], yvals[segments]])
			
		for i in range(1, segments):
			points.append([xvals[i], yvals[0], xvals[segments], yvals[segments-i]])
		
		for i in range(1, segments):
			points.append([xvals[segments-i], yvals[segments], xvals[segments], yvals[segments-i]])
			
		points.append([xvals[0], yvals[segments], xvals[segments], yvals[0]])
			
		for i in range(1, segments):
			points.append([xvals[0], yvals[segments-i], xvals[segments-i], yvals[0]])
			
			
		passes = int(math.ceil(float(totaldepth)/float(passdepth)))
		if self.settings.annotate:
			self.gcode.append("(Diamond pattern start (%6.2f,%6.2f) width %6.2f height %6.2f segments %d depth from %6.2f to %6.2f)" % (sx, sy, totalx, totaly, segments, sz, totaldepth))
			self.gcode.append("(Start point: %s)" % sp)
			self.gcode.append("(Cut border: %s)" % str(border))
		
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
					xa = p[0]
					ya = p[1]
					xb = p[2]
					yb = p[3]
				else:
					xa = p[2]
					ya = p[3]
					xb = p[0]
					yb = p[1]
				flag = not flag
					
				self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (xa, ya))
				self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (sz-depth))
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (xb, yb))
				self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
			
			if border:
				self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (xvals[0], yvals[0]))
				self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (sz-depth))
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (xvals[segments], yvals[0]))
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (xvals[segments], yvals[segments]))
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (xvals[0], yvals[segments]))
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (xvals[0], yvals[0]))
				self.gcode.append(("G0 Z"+self.fmt+""+self.speedTerm(addspeed, feedzG0)+"\n") % (safez))

		self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (sx, sy))
		if self.settings.annotate:
			self.gcode.append("(End object %s)" % self.viewTitle)
		self.gcl.updateList(self.gcode)
		self.bSave.Enable()
		self.bVisualize.Enable()
		self.setState(False, True)
	
