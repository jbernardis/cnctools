import wx
import math
from gcodelist import GCodeList
from cncobject import CNCObject
from validators import ValidateRange, ValidateNoEntryErrors, ValidateTrue
from pointlisteditdlg import PointListEditDialog
from contours.offset import offsetPath

class MainFrame(wx.Frame):
	def __init__(self, toolInfo, speedInfo, parent):
		self.parent = parent
		self.settings = parent.settings
		self.images = self.parent.images
		
		wx.Frame.__init__(self, None, size=(480, 800), title="")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = PolyPanel(toolInfo, speedInfo, self)
		sizer.Add(self.panel)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def okToClose(self):
		return self.panel.okToClose()
	
	def onClose(self, _):
		return self.panel.onClose(None)
		

class PolyPanel(wx.Panel, CNCObject):
	seqNo = 1
	def __init__(self, toolInfo, speedInfo, parent):
		CNCObject.__init__(self, parent, "contour:polyline")
		self.toolInfo = toolInfo
		
		self.modified = False
		self.unsaved = False
		self.viewTitle = "Polyline %d" % PolyPanel.seqNo
		self.titleText = "G Code Generator: %s" % self.viewTitle
		PolyPanel.seqNo += 1

		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		sizer = wx.GridBagSizer(wx.HORIZONTAL)
		sizer.Add(10, 10, wx.GBPosition(0, 4))
		ln = 1
		
		self.setTitleFlag()

		t = wx.StaticText(self, wx.ID_ANY, "Point List")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.tePoints = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_RIGHT + wx.TE_READONLY)
		self.addWidget(self.tePoints, "pointlist")
		sizer.Add(self.tePoints, pos=(ln, 1), span=(1,2), flag=wx.EXPAND, border=10)
		self.bEditPoints = wx.Button(self, wx.ID_ANY, "...", size=(30, 20))
		self.bEditPoints.SetToolTip("Edit Point List")
		
		bsz = wx.BoxSizer(wx.HORIZONTAL)
		bsz.AddSpacer(20)
		bsz.Add(self.bEditPoints)
		
		sizer.Add(bsz, pos=(ln, 3))
		self.Bind(wx.EVT_BUTTON, self.bEditPointsPressed, self.bEditPoints)
		ln += 1
		
		self.cbClosePath = wx.CheckBox(self, wx.ID_ANY, "Close Path")
		self.addWidget(self.cbClosePath, "closepath")
		sizer.Add(self.cbClosePath, pos=(ln, 0), span=(1,4),
				flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_HORIZONTAL, border=5)
		self.Bind(wx.EVT_CHECKBOX, self.onChange, self.cbClosePath)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Start Z")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teStartZ = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_RIGHT)
		self.addWidget(self.teStartZ, "startz")
		sizer.Add(self.teStartZ, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Safe Z above surface")
		sz = "%6.3f" % self.settings.safez
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teSafeZ = wx.TextCtrl(self, wx.ID_ANY, sz, style=wx.TE_RIGHT)
		self.addWidget(self.teSafeZ, "safez")
		sizer.Add(self.teSafeZ, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Tool Diameter")
		td = "%6.3f" % toolInfo["diameter"]
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teToolDiam = wx.TextCtrl(self, wx.ID_ANY, td, style=wx.TE_RIGHT)
		self.addWidget(self.teToolDiam, "tooldiameter")
		sizer.Add(self.teToolDiam, pos=(ln, 1), flag=wx.LEFT, border=10)

		t = wx.StaticText(self, wx.ID_ANY, "Stepover")
		so = "%6.3f" % speedInfo["stepover"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teStepOver = wx.TextCtrl(self, wx.ID_ANY, so, style=wx.TE_RIGHT)
		self.addWidget(self.teStepOver, "stepover")
		sizer.Add(self.teStepOver, pos=(ln, 3), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Total Depth")
		td = "%6.3f" % self.settings.totaldepth
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teTotalDepth = wx.TextCtrl(self, wx.ID_ANY, td, style=wx.TE_RIGHT)
		self.addWidget(self.teTotalDepth, "totaldepth")
		sizer.Add(self.teTotalDepth, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Depth/Pass")
		dpp = "%6.3f" % speedInfo["depthperpass"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.tePassDepth = wx.TextCtrl(self, wx.ID_ANY, dpp, style=wx.TE_RIGHT)
		self.addWidget(self.tePassDepth, "passdepth")
		sizer.Add(self.tePassDepth, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Tool Movement")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sizer.Add(self.getToolMovement(), pos=(ln, 1), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	

		t = wx.StaticText(self, wx.ID_ANY, "Tracks")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)	
		
		self.scTracks = wx.SpinCtrl(self, wx.ID_ANY, "", size=(50, -1), style=wx.ALIGN_RIGHT)
		self.addWidget(self.scTracks, "tracks")
		self.scTracks.SetRange(1,20)
		self.scTracks.SetValue(1)
		self.Bind(wx.EVT_SPINCTRL, self.onTracks, self.scTracks)
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(30)
		sz.Add(self.scTracks)
		sizer.Add(sz, pos=(ln, 3), border=5, flag=wx.LEFT+wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	
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
		
	def getToolMovement(self):
		labels = ["On Polyline", "Left of Forward", "Right of Forward"]
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
		
	def onCbAddSpeed(self, _):
		self.setState(True, False)
		flag = self.cbAddSpeed.IsChecked()
		self.teFeedXYG0.Enable(flag)
		self.teFeedXYG1.Enable(flag)
		self.teFeedZG0.Enable(flag)
		self.teFeedZG1.Enable(flag)
		
	def onTracks(self, _):
		self.setState(True, False)
		
	def bEditPointsPressed(self, _):
		try:
			data = eval(self.tePoints.GetValue())
		except:
			data = None
			
		minVal = 2
		if self.cbClosePath.IsChecked():
			minVal = 3
			
		dlg = PointListEditDialog(self, data, minVal)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			self.tePoints.SetValue(str(dlg.getValues()))
			self.setState(True, False)
			
		dlg.Destroy()
				
	def bGeneratePressed(self, _):
		self.bSave.Enable(False)
		self.bVisualize.Enable(False)
		self.gcl.clear()
		self.gcode = []
		
		self.fmt = "%%0.%df" % self.settings.decimals
		
		errs = []
		try:
			data = eval(self.tePoints.GetValue())
		except:
			errs.append("Point List")
		try:
			sz = float(self.teStartZ.GetValue())
		except:
			errs.append("Start Z")
		try:
			safez = float(self.teSafeZ.GetValue())
		except:
			errs.append("Safe Z")
			
		closePath = self.cbClosePath.IsChecked()
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
			
		if not ValidateNoEntryErrors(self, errs):
			return
		
		if closePath and len(data) < 3:
			ValidateTrue(self, False, "Need >2 points for a closed path")
			return
		
		if not ValidateRange(self, stepover, 0.001, 1.0, "Stepover", "0 < x <= 1.0"):
			return

		self.gcode = self.preamble(self.settings.metric, tdiam, self.toolInfo, safez)
			
		self.tDiam = tdiam
		if self.settings.annotate:
			self.gcode.append("(Polyline depth from %6.2f to %6.2f" % (sz, depth))	
		
		tracks = self.scTracks.GetValue()
		
		tm = self.getChosen(self.rbToolMove)

		passes = int(math.ceil(depth/passdepth))
			
		if tm == "Left of Forward":
			offset = tdiam/2.0
			offset2 = stepover
		elif tm == "Right of Forward":
			offset = -tdiam/2.0
			offset2 = -stepover
		else:
			offset = 0
			offset2 = 0
			if tracks != 1:
				dlg = wx.MessageDialog(self, "Cannot have more than 1 track when tool movement is \"On Polyline\".\nAssuming a value of 1.",
							'Only 1 Track permitted', wx.OK | wx.ICON_WARNING)
				dlg.ShowModal()
				dlg.Destroy()
				
			tracks = 1
			
		if offset != 0:
			data = offsetPath(data, offset, closePath)
			if data is None:
				ValidateTrue(self, False, "Unable to calculate offset path for track 0")
				return
			
		if self.settings.annotate:
			self.gcode.append("(Tool movement: %s)" % tm)
			self.gcode.append("(Tracks: %d)" % tracks)
			
		cz = sz - passdepth
		if cz < -depth:
			cz = -depth
		self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (data[0][0], data[0][1]))
		saveData = [x for x in data]
		
		for p in range(passes):
			if self.settings.annotate:
				self.gcode.append("(pass %d at depth %6.2f)" % (p, cz))
			self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (cz))
			for trk in range(tracks):
				for pt in data[1:]:
					self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (pt[0], pt[1]))
				
				if closePath:
					self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (data[0][0], data[0][1]))
				else:
					self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
					self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (data[0][0], data[0][1]))
					self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (cz))
					
				if trk+1 < tracks: # if not last track
					data = offsetPath(data, offset2, closePath)
					if data is None:
						ValidateTrue(self, False, "Unable to calculate offset path for track %d" % (trk+1))
						return
					self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (data[0][0], data[0][1]))
			
			data = [x for x in saveData]
			self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (data[0][0], data[0][1]))
			cz -= passdepth
			if cz < -depth:
				cz = -depth
		
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
		if self.settings.annotate:
			self.gcode.append("(End object %s)" % self.viewTitle)
			
		self.gcl.updateList(self.gcode)
		self.bSave.Enable()
		self.bVisualize.Enable()
		self.setState(False, True)
