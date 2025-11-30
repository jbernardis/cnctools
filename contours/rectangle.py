import wx
import math
from gcodelist import GCodeList
from cncobject import CNCObject
from validators import ValidateToolSize, ValidateRange, ValidateNoEntryErrors
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
			
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "angle")
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=0, min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(0)
		sc.SetDigits(digits)
		self.scAngle = sc
		self.addWidget(self.scAngle, "angle")
		sizer.Add(self.scAngle, pos=(ln, 1), flag=wx.LEFT, border=10)

		t = wx.StaticText(self, wx.ID_ANY, "Corner Radius")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)	
			
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "cornerrad")
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=0, min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(0)
		sc.SetDigits(digits)
		self.scCornerRad = sc
		self.addWidget(self.scCornerRad, "cornerrad")
		sizer.Add(self.scCornerRad, pos=(ln, 3), flag=wx.LEFT, border=10)
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
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		td = self.resolveToolDiameter(toolInfo)
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "tooldiam")
		self.databaseToolDiam = round(td, digits)
		self.effectiveToolDiameter = round(td, digits)
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

		t = wx.StaticText(self, wx.ID_ANY, "Tool Movement")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sizer.Add(self.getToolMovement(), pos=(ln, 3), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Cutting Direction")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sizer.Add(self.getCuttingDirection(), pos=(ln, 1), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	

		self.cbPocket = wx.CheckBox(self, wx.ID_ANY, "Pocket")
		self.addWidget(self.cbPocket, "pocket")
		sizer.Add(self.cbPocket, pos=(ln, 2), span=(1,2),
				flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_HORIZONTAL, border=5)
		self.Bind(wx.EVT_CHECKBOX, self.onChange, self.cbPocket)
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
		vmin, vmax, vinc, digits = self.getSpinValues(self.settings.metric, "feedxyg1")
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
			
		self.addspeed = self.cbAddSpeed.IsChecked()
		self.feedzG0 = self.scFeedZG0.GetValue()
		self.feedzG1 = self.scFeedZG1.GetValue()
		self.feedxyG0 = self.scFeedXYG0.GetValue()
		self.feedxyG1 = self.scFeedXYG1.GetValue()

		stepover = self.scStepover.GetValue()
		passdepth = self.scPassDepth.GetValue()
		depth = self.scTotalDepth.GetValue()
		tdiam = self.scToolDiam.GetValue()
		angle = self.scAngle.GetValue()
		cornerrad = self.scCornerRad.GetValue()

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
			
		rot = Rotator(angle)
			
		if not ValidateToolSize(self, tdiam, height, "Height"):
			return
		if not ValidateToolSize(self, tdiam, width, "Width"):
			return
		
		if not ValidateRange(self, stepover, 0.001, 1.0, "Stepover", "0 < x <= 1.0"):
			return

		if self.databaseToolDiam == tdiam:
			toolname = self.toolInfo["name"]
		else:
			toolname = None
			
		self.gcode = self.preamble(self.settings, self.viewTitle, tdiam, toolname, self.settings.metric)					
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG0)) % safez)

		if cornerrad == 0:						
			self.tDiam = tdiam
				
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
				
			pkt = self.cbPocket.IsChecked()

			if self.settings.annotate:
				sx = points[0][0]
				sy = points[0][1]
				
				if angle == 0:
					self.gcode.append("(Rectangle (%6.2f,%6.2f) to (%6.2f,%6.2f))" % (sx, sy, sx+width, sy+height))
					self.gcode.append("(Depth from %6.2f to %6.2f)" % (sz, depth))
				else:
					rx1, ry1 = rot.rotate(sx, sy)
					rx2, ry2 = rot.rotate(width+sx, height+sy)
					self.gcode.append("(Rectangle (%6.2f,%6.2f) to (%6.2f,%6.2f))" % (rx1, ry1, rx2, ry2))
					self.gcode.append("(Depth from %6.2f to %6.2f rotated %6.2f)" % (sz, depth, angle))
		
				self.gcode.append("(Start point: %s)" % sp)
				self.gcode.append("(Cutting direction: %s)" % cd)
				self.gcode.append("(Tool movement: %s)" % tm)
				self.gcode.append("(Pocket: %s)" % pkt)
	
			if not pkt:
				self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG0)) % (safez))
				self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG0)) % rot.rotate(points[0][0], points[0][1]))
	
			
			xmin = min(points[0][0], points[2][0]) + tdiam/2
			xmax = max(points[0][0], points[2][0]) - tdiam/2
			ymin = min(points[0][1], points[2][1]) + tdiam/2
			ymax = max(points[0][1], points[2][1]) - tdiam/2
			
			passes = int(math.ceil(depth/passdepth))
			
			
			cz = sz
			for i in range(passes):
				cz -= passdepth
				if cz < -depth:
					cz = -depth
				if self.settings.annotate:
					self.gcode.append("(Pass number %d at depth %f)" % (i, cz))
	
				if pkt:
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
						
					self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG0)) % (safez))
					self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG0)) % rot.rotate(xb, yb))
					self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG1)) % (cz))
					self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xa, ya))
					
					d = stepover * tdiam
					while (xa-d) >= xmin:
						if cd == "Clockwise":
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xa-d, ya-d))
							if vertical:
								self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xa-d, yb+d))
							else:
								self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xa-d, ya+d))
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xb+d, yb+d))
							if vertical:
								self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xb+d, ya-d))
							else:
								self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xb+d, yb-d))
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xa-d, ya-d))
						else:
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xa-d, ya-d))
							if vertical:
								self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xb+d, ya-d))
							else:
								self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xb+d, yb-d))
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xb+d, yb+d))
							if vertical:
								self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xa-d, yb+d))
							else:
								self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xa-d, ya+d))
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(xa-d, ya-d))
						d += stepover * tdiam
					
					self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG0)) % (safez))
					self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG0)) % rot.rotate(points[0][0], points[0][1]))
				
				self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG1)) % (cz))
				for p in points[1:]:
					self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % rot.rotate(p[0], p[1]))
				
			self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG0)) % (safez))
			if self.settings.annotate:
				self.gcode.append("(End object %s)" % self.viewTitle)
				
		else:
			# cornerrad != 0
			self.tDiam = tdiam
				
			self.gcode.append("(Corner Radius = %.2f)" % cornerrad)
			
			points = [[sx, sy+cornerrad], [sx, sy+height-cornerrad],
					[sx+cornerrad, sy+height], [sx+width-cornerrad, sy+height], 
					[sx+width, sy+height-cornerrad], [sx+width, sy+cornerrad],
					[sx+width-cornerrad, sy], [sx+cornerrad, sy]]
			
				
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
			cRadAdj = 0
			if tm == "Inside Rectangle":
				cRadAdj = -rad
				points[0][0] += rad
				points[1][0] += rad
				points[2][1] -= rad
				points[3][1] -= rad
				points[4][0] -= rad
				points[5][0] -= rad
				points[6][1] += rad
				points[7][1] += rad
			
			elif tm == "Outside Rectangle":
				cRadAdj = rad
				points[0][0] -= rad
				points[1][0] -= rad
				points[2][1] += rad
				points[3][1] += rad
				points[4][0] += rad
				points[5][0] += rad
				points[6][1] -= rad
				points[7][1] -= rad

			baseOffset = cornerrad + cRadAdj
			centerOffsets = [ [baseOffset, 0], [0, -baseOffset], [-baseOffset, 0], [0, baseOffset] ]
				
			self.arcCmd = "G2"
			cd = self.getChosen(self.rbCutDir)
			cw = True
			if cd != "Clockwise":
				np = points[::-1]
				points = np
				co = centerOffsets[::-1]
				centerOffsets = co
				self.arcCmd = "G3"
				cw = False
				
			pkt = self.cbPocket.IsChecked()
		
			if self.settings.annotate:
				sx = points[0][0]
				sy = points[0][1]
				if angle == 0:
					self.gcode.append("(Rectangle (%6.2f,%6.2f) to (%6.2f,%6.2f))" % (sx, sy, sx+width, sy+height))
					self.gcode.append("(Depth from %6.2f to %6.2f)" % (sz, depth))
				else:
					rx1, ry1 = rot.rotate(sx, sy)
					rx2, ry2 = rot.rotate(width+sx, height+sy)
					self.gcode.append("(Rectangle (%6.2f,%6.2f) to (%6.2f,%6.2f))" % (rx1, ry1, rx2, ry2))
					self.gcode.append("(Depth from %6.2f to %6.2f rotated %6.2f)" % (sz, depth, angle))

				self.gcode.append("(Start point: %s)" % sp)
				self.gcode.append("(Cutting direction: %s)" % cd)
				self.gcode.append("(Tool movement: %s)" % tm)
				self.gcode.append("(Pocket: %s)" % pkt)
				
			self.gcode.append("(%s)" % str(points))
			self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG0)) % (safez))
			self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG0)) % rot.rotate(points[0][0], points[0][1]))
			
			passes = int(math.ceil(depth/passdepth))
			
			points.append([points[0][0], points[0][1]])
			
			cz = sz
			
			for i in range(passes):
				cz -= passdepth
				if cz < -depth:
					cz = -depth
				if self.settings.annotate:
					self.gcode.append("(Pass number %d at depth %f)" % (i, cz))
					
				self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG1)) % (cz))
				if pkt:
					delta = stepover * tdiam
					offset = baseOffset - delta
					pts = [[x[0], x[1]] for x in points]
					while offset > 0:
						if cw:
							co = [ [offset, 0], [0, -offset], [-offset, 0], [0, offset] ]
							pts[0][0] += delta
							pts[1][0] += delta
							pts[8][0] += delta
							
							pts[2][1] -= delta
							pts[3][1] -= delta
							
							pts[4][0] -= delta
							pts[5][0] -= delta
							
							pts[6][1] += delta
							pts[7][1] += delta
						else:
							co = [ [0, offset], [-offset, 0], [0, -offset], [offset, 0] ]
							pts[0][1] += delta
							pts[1][1] += delta
							pts[8][1] += delta
							
							pts[2][0] -= delta
							pts[3][0] -= delta
							
							pts[4][1] -= delta
							pts[5][1] -= delta
							
							pts[6][0] += delta
							pts[7][0] += delta

						self.drawLoop(pts, co, rot)
						offset -= delta
						
					if cw:
						xlo, xhi, ylo, yhi = pts[7][0], pts[6][0], pts[0][1], pts[1][1]
					else:
						xlo, xhi, ylo, yhi = pts[0][0], pts[1][0], pts[7][1], pts[6][1]
						
					while (xlo <= xhi and ylo <= yhi):
						if cw:
							rpts = [[xlo, yhi], [xhi, yhi], [xhi, ylo], [xlo, ylo]]
						else:
							rpts = [[xhi, ylo], [xhi, yhi], [xlo, yhi], [xlo, ylo]]
						self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % (xlo, ylo))
						for p in rpts:
							self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % (p[0], p[1]))
						xlo += delta
						ylo += delta
						xhi -= delta
						yhi -= delta
				
				self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG1)) % (cz))
				self.drawLoop(points, centerOffsets, rot)
				
			self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(self.addspeed, self.feedzG0)) % (safez))
			if self.settings.annotate:
				self.gcode.append("(End object %s)" % self.viewTitle)

				
		self.gcl.updateList(self.gcode)
		self.bSave.Enable()
		self.bVisualize.Enable()
		self.setState(False, True)

	def drawLoop(self, points, centerOffsets, rot):
		p0 = points[0]
		rp0 = rot.rotate(p0[0], p0[1])
		self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % (rp0[0], rp0[1]))
		for i in range(4):
			p1 = points[i*2+1]
			rp1 = rot.rotate(p1[0], p1[1])
			p2 = points[i*2+2]
			rp2 = rot.rotate(p2[0], p2[1])
			self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1)) % (rp1[0], rp1[1]))
			cp = rot.rotate(p1[0] + centerOffsets[i][0], p1[1] + centerOffsets[i][1])
			xoff = cp[0] - rp1[0]
			yoff = cp[1] - rp1[1]
			self.gcode.append((self.arcCmd+self.IJTerm("I", xoff)+self.IJTerm("J", yoff)+" X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.addspeed, self.feedxyG1))
						% (rp2[0], rp2[1]))

