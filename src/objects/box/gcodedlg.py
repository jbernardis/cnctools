import wx
import objects.box.cncbox as cncbox
from gcodelist import GCodeList
from settings import BTNDIM, SPINSIZE
from validators import verifyStaleGCodeSave, verifyStaleGCodeView

DEPTHFORMAT = "%8.2f"
RATEFORMAT = "%8.2f"
INTFORMAT = "%3d"

BTNSPACING = 10

VISIBLEQUEUESIZE = 21

class GCodeDlg(wx.Dialog):
	def __init__(self, parent, bx, toolinfo, images, speedinfo, settings):
		self.parent = parent
		self.speedinfo = speedinfo
		self.bx = bx
		self.toolinfo = toolinfo
		self.settings = settings
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.SetBackgroundColour("white")

		self.tooldiam = self.parent.tooldiam
		self.depthPerCut = speedinfo["depthperpass"]
		self.feedG1XY = speedinfo["G1XY"]
		self.feedG1Z = speedinfo["G1Z"]
		self.feedG0XY = speedinfo["G0XY"]
		self.feedG0Z = speedinfo["G0Z"]
		self.safez = self.settings.safez
		self.extraDepth = 0.5
		self.offsetX = 0
		self.offsetY = 0
		
		self.images = images
		
		dsizer = wx.BoxSizer(wx.VERTICAL)
		dsizer.AddSpacer(10)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		
		sbox = wx.StaticBox(self, -1, "Choose face")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

		staticboxsizer.AddSpacer(10)
		self.rbTop = wx.RadioButton(self, wx.ID_ANY, " Top ", style = wx.RB_GROUP )
		self.rbBottom = wx.RadioButton(self, wx.ID_ANY, " Bottom " )
		self.rbLeft = wx.RadioButton(self, wx.ID_ANY, " Left " )
		self.rbRight = wx.RadioButton(self, wx.ID_ANY, " Right " )
		self.rbFront = wx.RadioButton(self, wx.ID_ANY, " Front " )
		self.rbBack = wx.RadioButton(self, wx.ID_ANY, " Back " )
		staticboxsizer.Add(self.rbTop, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbBottom, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbLeft, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbRight, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbFront, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbBack, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		self.rbTop.SetValue(True)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer(20)
		
		t = wx.StaticText(self, wx.ID_ANY, "Depth/Pass: ", size=(80, -1))
		vmin, vmax, vinc, digits = self.parent.getSpinValues(self.settings.metric, "passdepth")
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=self.depthPerCut, min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(self.depthPerCut)
		sc.SetDigits(digits)
		self.scDPP = sc

		sc.Bind(wx.EVT_TEXT, self.onTextDPP)
		sc.Bind(wx.EVT_SPINCTRL, self.onSpinDPP)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP, 5)
		hb.Add(sc)
		vsizer.Add(hb)
		vsizer.AddSpacer(5)
		
		t = wx.StaticText(self, wx.ID_ANY, "Extra Depth: ", size=(80, -1))
		vmin, vmax, vinc, digits = self.parent.getSpinValues(self.settings.metric, "extradepth")
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=self.extraDepth, min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(self.settings.safez)
		sc.SetDigits(digits)
		self.scExtraDepth = sc

		sc.Bind(wx.EVT_TEXT, self.onTextExtraDepth)
		sc.Bind(wx.EVT_SPINCTRL, self.onSpinExtraDepth)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP, 5)
		hb.Add(sc)
		vsizer.Add(hb)
		vsizer.AddSpacer(5)
		
		t = wx.StaticText(self, wx.ID_ANY, "Stepover: ", size=(80, -1))
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=speedinfo["stepover"], min=0.1, max=1.0, inc=0.01, size=SPINSIZE)
		sc.SetValue(speedinfo["stepover"])
		sc.SetDigits(2)
		self.scStepover = sc

		sc.Bind(wx.EVT_TEXT, self.onTextStepover)
		sc.Bind(wx.EVT_SPINCTRL, self.onSpinStepover)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP, 5)
		hb.Add(sc)
		vsizer.Add(hb)
		vsizer.AddSpacer(5)
		
		t = wx.StaticText(self, wx.ID_ANY, "Safe Z Height: ", size=(80, -1))
		vmin, vmax, vinc, digits = self.parent.getSpinValues(self.settings.metric, "safez")
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=self.safez, min=vmin, max=vmax, inc=vinc, size=SPINSIZE)
		sc.SetValue(self.settings.safez)
		sc.SetDigits(digits)
		self.scSafeZ = sc

		sc.Bind(wx.EVT_SPINCTRL, self.onSpinSafeZ)
		sc.Bind(wx.EVT_TEXT, self.onTextSafeZ)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP, 5)
		hb.Add(sc)
		vsizer.Add(hb)
		vsizer.AddSpacer(5)

		hsizer.Add(vsizer)
		hsizer.AddSpacer(20)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		
		sbox = wx.StaticBox(self, -1, "Cut direction - inside cuts")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

		staticboxsizer.AddSpacer(10)
		self.rbICW = wx.RadioButton(self, wx.ID_ANY, " Clockwise ", style = wx.RB_GROUP )
		self.rbICCW = wx.RadioButton(self, wx.ID_ANY, " Counter Clockwise " )
		staticboxsizer.Add(self.rbICW, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbICCW, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		self.rbICW.SetValue(True)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer(20)
		
		sbox = wx.StaticBox(self, -1, "Cut direction - outside cuts")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

		staticboxsizer.AddSpacer(10)
		self.rbOCW = wx.RadioButton(self, wx.ID_ANY, " Clockwise ", style = wx.RB_GROUP )
		self.rbOCCW = wx.RadioButton(self, wx.ID_ANY, " Counter Clockwise " )
		staticboxsizer.Add(self.rbOCW, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbOCCW, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		self.rbOCCW.SetValue(True)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer(20)

		sbox = wx.StaticBox(self, -1, "Origin")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

		staticboxsizer.AddSpacer(10)
		self.rbUL = wx.RadioButton(self, wx.ID_ANY, " Upper Left ", style = wx.RB_GROUP )
		self.rbUR = wx.RadioButton(self, wx.ID_ANY, " Upper Right " )
		self.rbCTR = wx.RadioButton(self, wx.ID_ANY, " Center " )
		self.rbLL = wx.RadioButton(self, wx.ID_ANY, " Lower Left " )
		self.rbLR = wx.RadioButton(self, wx.ID_ANY, " Lower Right " )
		staticboxsizer.Add(self.rbUL, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbUR, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbCTR, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbLL, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbLR, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer(10)
		self.rbCTR.SetValue(True)
		
		
		
		for rb in [ self.rbTop, self.rbBottom, self.rbLeft, self.rbRight, self.rbFront, self.rbBack,
				self.rbUL, self.rbUR, self.rbCTR, self.rbLL, self.rbLR,
				self.rbOCW, self.rbOCCW,
				self.rbICW, self.rbICCW ]:
			self.Bind(wx.EVT_RADIOBUTTON, self.onRb, rb)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer(20)

		hsizer.Add(vsizer)
		hsizer.AddSpacer(20)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		
		sbox = wx.StaticBox(self, -1, "Feed Rates")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
		
		t = wx.StaticText(self, wx.ID_ANY, "XY (G0): ", size=(80, -1))
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=self.feedG0XY, size=SPINSIZE)
		vmin, vmax, vinc, digits = self.parent.getSpinValues(self.settings.metric, "feedxyg0")
		sc.SetRange(vmin, vmax)
		sc.SetValue(self.feedG0XY)
		sc.Bind(wx.EVT_SPINCTRL, self.onSpinG0XY)
		sc.Bind(wx.EVT_SPINCTRL, self.onTextG0XY)
		self.scG0XY = sc
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP+wx.LEFT, 5)
		hb.Add(sc)
		staticboxsizer.Add(hb)
		staticboxsizer.AddSpacer(5)
		
		t = wx.StaticText(self, wx.ID_ANY, "Z (G0): ", size=(80, -1))
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=self.feedG0XY, size=SPINSIZE)
		vmin, vmax, vinc, digits = self.parent.getSpinValues(self.settings.metric, "feedxyg1")
		sc.SetRange(vmin, vmax)
		sc.SetValue(self.feedG0Z)
		sc.Bind(wx.EVT_SPINCTRL, self.onSpinG0Z)
		sc.Bind(wx.EVT_SPINCTRL, self.onTextG0Z)
		self.scG0Z = sc
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP+wx.LEFT, 5)
		hb.Add(sc)
		staticboxsizer.Add(hb)
		staticboxsizer.AddSpacer(5)

		t = wx.StaticText(self, wx.ID_ANY, "XY (G1): ", size=(80, -1))
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=self.feedG0XY, size=SPINSIZE)
		vmin, vmax, vinc, digits = self.parent.getSpinValues(self.settings.metric, "feedzg0")
		sc.SetRange(vmin, vmax)
		sc.SetValue(self.feedG1XY)
		sc.Bind(wx.EVT_SPINCTRL, self.onSpinG1XY)
		sc.Bind(wx.EVT_SPINCTRL, self.onTextG1XY)
		self.scG1XY = sc
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP+wx.LEFT, 5)
		hb.Add(sc)
		staticboxsizer.Add(hb)
		staticboxsizer.AddSpacer(5)
		
		t = wx.StaticText(self, wx.ID_ANY, "Z (G1): ", size=(80, -1))
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=self.feedG0XY, size=SPINSIZE)
		vmin, vmax, vinc, digits = self.parent.getSpinValues(self.settings.metric, "feedzg1")
		sc.SetRange(vmin, vmax)
		sc.SetValue(self.feedG1Z)
		sc.Bind(wx.EVT_SPINCTRL, self.onSpinG1Z)
		sc.Bind(wx.EVT_SPINCTRL, self.onTextG1Z)
		self.scG1Z = sc
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP+wx.LEFT, 5)
		hb.Add(sc)
		staticboxsizer.Add(hb)
		staticboxsizer.AddSpacer(15)
		
		self.cbFeed = wx.CheckBox(self, wx.ID_ANY, "Add Rates to GCode")
		self.Bind(wx.EVT_CHECKBOX, self.onCbFeed, self.cbFeed)
		self.cbFeed.SetValue(self.settings.addspeed)
		
		staticboxsizer.Add(self.cbFeed, 1, wx.LEFT, 20)
		staticboxsizer.AddSpacer(5)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer(20)
		
		hsizer.Add(vsizer)
		hsizer.AddSpacer(20)
		
		dsizer.Add(hsizer)
		dsizer.AddSpacer(20)
		
		self.enableSpeeds(self.settings.addspeed)

		btnsizer = wx.BoxSizer(wx.HORIZONTAL)		

		self.bGCode = wx.BitmapButton(self, wx.ID_ANY, self.images.pngGcode, size=BTNDIM)
		self.bGCode.SetToolTip("Generate G Code")
		btnsizer.Add(self.bGCode, 1, wx.LEFT + wx.RIGHT, BTNSPACING)
		self.Bind(wx.EVT_BUTTON, self.doGCode, self.bGCode)
		
		self.bSave = wx.BitmapButton(self, wx.ID_ANY, self.images.pngFilesaveas, size=BTNDIM)
		self.bSave.SetToolTip("Save G Code")
		btnsizer.Add(self.bSave, 1, wx.LEFT + wx.RIGHT, BTNSPACING)
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
		self.bSave.Disable()		
				
		self.bVisualize = wx.BitmapButton(self, wx.ID_ANY, self.images.pngView, size=BTNDIM)
		self.bVisualize.SetToolTip("Visualize G Code")
		btnsizer.Add(self.bVisualize, 1, wx.LEFT + wx.RIGHT, BTNSPACING)
		self.Bind(wx.EVT_BUTTON, self.bVisualizePressed, self.bVisualize)
		self.bVisualize.Disable()

		self.bExit = wx.BitmapButton(self, wx.ID_ANY, self.images.pngExit, size=BTNDIM)
		self.bExit.SetToolTip("Dismiss dialog")
		btnsizer.Add(self.bExit, 1, wx.LEFT + wx.RIGHT, BTNSPACING)
		self.Bind(wx.EVT_BUTTON, self.doExit, self.bExit)

		dsizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
		
		dsizer.AddSpacer(10)
		
		self.gcl = GCodeList(self)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(10)
		hsizer.Add(self.gcl, 1, wx.EXPAND)
		hsizer.AddSpacer(10)
		
		dsizer.Add(hsizer, 1, wx.EXPAND)
				
		dsizer.AddSpacer(10)
		
		self.SetSizer(dsizer)  
		dsizer.Fit(self)
		
		self.modified = None
		self.unsaved = None		
		self.setState(modified=False, unsaved=False)
	
	def setState(self, modified=None, unsaved=None):
		updateTitle = False
		if modified is not None:
			self.modified = modified
			updateTitle = True
			
		if unsaved is not None:
			self.unsaved = unsaved
			updateTitle = True

		if updateTitle:			
			title = "Generate G Code"
			if self.modified:
				title += " (modified)"
				
			if self.unsaved and self.modified:
				title += " (stale)"
				
			elif self.unsaved:
				title += " (unsaved)"
			
			self.SetTitle(title)

		self.bSave.Enable(self.unsaved)
		
	def doExit(self, e):
		self.EndModal(wx.ID_OK)
		
	def onRb(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onTextG0XY(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onSpinG0XY(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onTextG1XY(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onSpinG1XY(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onTextG0Z(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onSpinG0Z(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onTextG1Z(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onSpinG1Z(self, e):
		self.setState(modified=True)
		e.Skip()
				
	def onTextDPP(self, e):
		self.setState(modified=True)
		e.Skip()
				
	def onSpinDPP(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onTextSafeZ(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onSpinSafeZ(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onTextExtraDepth(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onSpinExtraDepth(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onTextStepover(self, e):
		self.setState(modified=True)
		e.Skip()
		
	def onSpinStepover(self, e):
		self.setState(modified=True)
		e.Skip()
			
	def illegalTcValue(self, name):
		dlg = wx.MessageDialog(self,
			"Illegal value for %s.\nRetaining old value" % name,
			'Illegal value entered',
			wx.OK | wx.ICON_INFORMATION
			)
		dlg.ShowModal()
		dlg.Destroy()
			
	def onCbFeed(self, e):
		f = self.cbFeed.GetValue()
		self.setState(modified=True)
		self.enableSpeeds(f)
		
	def enableSpeeds(self, f=True):
		self.scG0XY.Enable(f)
		self.scG0Z.Enable(f)
		self.scG1XY.Enable(f)
		self.scG1Z.Enable(f)
		
	def doGCode(self, e):
		self.gcl.clear()
		ft = cncbox.FACE_TOP
		faceName = "Top Face"
		if self.rbTop.GetValue():
			ft = cncbox.FACE_TOP
			faceName = "Top Face"
		elif self.rbBottom.GetValue():
			ft = cncbox.FACE_BOTTOM
			faceName = "Bottom Face"
		elif self.rbLeft.GetValue():
			ft = cncbox.FACE_LEFT
			faceName = "Left Face"
		elif self.rbRight.GetValue():
			ft = cncbox.FACE_RIGHT
			faceName = "Right Face"
		elif self.rbFront.GetValue():
			ft = cncbox.FACE_FRONT
			faceName = "Front Face"
		elif self.rbBack.GetValue():
			ft = cncbox.FACE_BACK
			faceName = "Rear Face"
			
		safez = self.scSafeZ.GetValue()
			
		self.feedzG0 = self.scG0Z.GetValue()
		self.feedzG1 = self.scG1Z.GetValue()
		self.feedxyG0 = self.scG0XY.GetValue()
		self.feedxyG1 = self.scG1XY.GetValue()

		extradepth = self.scExtraDepth.GetValue()
		passdepth = self.scDPP.GetValue()
		stepover = self.scStepover.GetValue()
		
		hasBlindSlots = self.bx.hasBlindSlots(ft)
		
		self.fmt = "%%0.%df" % self.settings.decimals
		
		self.addspeed = self.cbFeed.IsChecked()
			
		tdiam = self.tooldiam
		trad = float(tdiam)/2.0
		gcomment = "%s - %s" % (self.parent.viewTitle, faceName)

		if self.parent.databaseToolDiam == tdiam:
			toolname = self.toolinfo["name"]
		else:
			toolname = None

		gcode = self.parent.preamble(self.settings, gcomment, tdiam, toolname, self.settings.metric)					
		gcode.append(("G0 Z"+self.fmt+self.addSpeedTerm("G0Z")) % safez)

		self.offsetX = 0
		self.offsetY = 0
		
		fw, fh = self.bx.getFaceDim(ft)
		dx = fw / 2.0
		dy = fh / 2.0
		
		if self.rbUL.GetValue():
			self.offsetX = dx
			self.offsetY = -dy
		
		elif self.rbUR.GetValue():
			self.offsetX = -dx
			self.offsetY = -dy
		
		elif self.rbLL.GetValue():
			self.offsetX = dx
			self.offsetY = dy
			
		elif self.rbLR.GetValue():
			self.offsetX = -dx
			self.offsetY = dy
			
		icw = True
		if self.rbICCW.GetValue():
			icw = False
			
		ocw = True
		if self.rbOCCW.GetValue():
			ocw = False

		pts, crc, rct = self.bx.render(ft, tdiam, stepover)
		totalDepth = self.bx.Wall
				
		steps = []
		d = passdepth
		while totalDepth - d > 0.0001: 
			steps.append(-d)
			d += passdepth
		steps.append(-(totalDepth + extradepth))
		
		if icw:
			cmd = "G2"
		else:
			cmd = "G3"

		mirrorSide = False			
		if hasBlindSlots:
			dlg = wx.MessageDialog(self, 'Blind slots requires cutting on back side\nPress yes to mirror side\notherwise press no cut as defined',
                           'Mirror Side?',
                           wx.YES_NO | wx.ICON_WARNING)
			mirrorSide = dlg.ShowModal() == wx.ID_YES
			dlg.Destroy()


		if len(crc) > 0:
			gcode.append("( circles )")		
		for c in crc:
			cx = c[0][0]
			cy = c[0][1]
			if mirrorSide:
				cx = -cx

			crad = c[1] - trad
			if self.settings.annotate:
				gcode.append(("( New circle - center " + self.fmt + "," + self.fmt + " radius " + self.fmt + " " + self.fmt +" )")
						 % (self.normalX(cx), self.normalY(cy), c[1], crad))
				
			gcode.append(("G0 X" + self.fmt + " Y" + self.fmt + self.addSpeedTerm("G0XY")) 
						% (self.normalX(cx), self.normalY(cy - crad)))
			for p in steps:
				gcode.append(("G1 Z" + self.fmt + self.addSpeedTerm("G1Z")) % p)
				gcode.append((cmd+" J" + self.fmt + " X" + self.fmt + " Y" + self.fmt + self.addSpeedTerm("G1XY"))
						% (crad, self.normalX(cx), self.normalY(cy) - crad))
			
			gcode.append(("G0 Z" + self.fmt + self.addSpeedTerm("G0Z")) % self.safez)
			
		if len(rct) > 0:
			gcode.append("( rectangles )")
		for r in rct:
			dx = r[1]/2.0 - trad
			dy = r[2]/2.0 - trad
			cx = r[0][0]
			cy = r[0][1]
			if mirrorSide:
				cx = -cx
				
			if self.settings.annotate:
				gcode.append(("( New rectangle - center " + self.fmt + "," + self.fmt + " width " + self.fmt + " " + self.fmt +" height " + self.fmt + " " + self.fmt +" )")
						% (self.normalX(cx), self.normalY(cy), r[1], r[1]-2*trad, r[2], r[2]-2*trad))	
			if icw:
				rpts = [ [-dx, dy], [dx, dy], [dx, -dy], [-dx, -dy] ]
			else:
				rpts = [ [dx, -dy], [dx, dy], [-dx, dy], [-dx, -dy] ]

			gcode.append(("G0 X" + self.fmt + " Y" + self.fmt + self.addSpeedTerm("G0XY")) 
						% (self.normalX(cx-dx), self.normalY(cy-dy)))
			for p in steps:
				gcode.append(("G1 Z" + self.fmt + self.addSpeedTerm("G1Z")) % p)
				for rp in rpts:
					gcode.append(("G1 X" + self.fmt + " Y" + self.fmt + self.addSpeedTerm("G1XY")) 
								% (self.normalX(cx+rp[0]), self.normalY(cy+rp[1])))

			gcode.append(("G0 Z" + self.fmt + self.addSpeedTerm("G0Z")) % self.safez)
			
		if self.settings.annotate:
			gcode.append("( perimeter )")
		if ocw:
			data = pts
		else:
			data = pts[::-1]
			
		dx = data[0][0]
		dy = data[0][1]
		if mirrorSide:
			dx = -dx
			
		gcode.append(("G0 X" + self.fmt + " Y" + self.fmt + self.addSpeedTerm("G0XY")) 
					% (self.normalX(dx), self.normalY(dy)))
		
		for i in range(len(steps)):
			p = steps[i]
			if self.settings.annotate:
				gcode.append(("( layer at depth "+DEPTHFORMAT + " )") % p)
			pts = self.bx.render(ft, tdiam, stepover, -p >= totalDepth/2.0)[0]
			if ocw:
				data = [pt for pt in pts]
			else:
				data = [pt for pt in pts[::-1]]

			gcode.append(("G1 Z" + self.fmt + self.addSpeedTerm("G1Z")) % p)
			for d in range(1, len(data)):
				dx = data[d][0]
				dy = data[d][1]
				if mirrorSide:
					dx = -dx
				gcode.append(("G1 X" + self.fmt + " Y" + self.fmt + self.addSpeedTerm("G1XY")) 
						% (self.normalX(dx), self.normalY(dy)))

		gcode.append(("G0 Z" + self.fmt + self.addSpeedTerm("G0Z")) % self.safez)
			
		self.gcl.updateList(gcode)
		self.bVisualize.Enable()
		self.bSave.Enable()
		self.setState(modified=False, unsaved=True)
	
	def bVisualizePressed(self, _):
		if self.modified:
			rc = verifyStaleGCodeView(self)
			if not rc:
				return 

		self.gcl.visualize()
		
	def bSavePressed(self, _):
		if self.modified:
			rc = verifyStaleGCodeSave(self)
			if not rc:
				return 

		if self.gcl.save(self.settings):
			self.setState(modified=False, unsaved=False)

	def normalX(self, x):
		return x+self.offsetX
	
	def normalY(self, y):
		return y+self.offsetY
			
	def addSpeedTerm(self, stype):
		if not self.addspeed:
			return ""
		
		if stype == "G0XY":
			return self.parent.speedTerm(True, self.feedxyG0)
		if stype == "G0Z":
			return self.parent.speedTerm(True, self.feedzG0)
		if stype == "G1XY":
			return self.parent.speedTerm(True, self.feedxyG1)
		if stype == "G1Z":
			return self.parent.speedTerm(True,  self.feedzG1)
		
		return ""
