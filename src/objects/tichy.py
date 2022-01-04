import wx
import math
from gcodelist import GCodeList
from cncobject import CNCObject
from validators import ValidateToolSize, ValidateNoEntryErrors
from settings import SPINSIZE

TYPE_RECTANGLE = 1
TYPE_CIRCLE = 2
TYPE_ROUNDTOP = 3
TYPE_ARCTOP = 4
tichyWindows = {
	"8010": { "type": TYPE_RECTANGLE, "params": [ 13.21, 11.94 ] },
	"8014": { "type": TYPE_RECTANGLE, "params": [ 10.92, 17.27 ] },
	"8023": { "type": TYPE_RECTANGLE, "params": [ 9.40, 8.38 ] },
	"8024": { "type": TYPE_RECTANGLE, "params": [ 11.68, 19.81 ] },
	"8025": { "type": TYPE_RECTANGLE, "params": [ 9.14, 19.05 ] },
	"8026": { "type": TYPE_RECTANGLE, "params": [ 12.95, 8.89 ] },
	"8028": { "type": TYPE_RECTANGLE, "params": [ 9.40, 19.81 ] },
	"8029": { "type": TYPE_RECTANGLE, "params": [ 8.64, 15.75 ] },
	"8030": { "type": TYPE_RECTANGLE, "params": [ 10.16, 24.89 ] },
	"8031": { "type": TYPE_RECTANGLE, "params": [ 9.65, 21.08 ] },
	"8042": { "type": TYPE_RECTANGLE, "params": [ 16.26, 10.67 ] },
	"8043": { "type": TYPE_RECTANGLE, "params": [ 11.43, 19.81 ] },
	"8047": { "type": TYPE_ROUNDTOP,  "params": [ 9.65, 17.02 ] },
	"8048": { "type": TYPE_ROUNDTOP,  "params": [ 5.59, 10.16 ] },
	"8054": { "type": TYPE_RECTANGLE, "params": [ 13.72, 27.18 ] },
	"8055": { "type": TYPE_ARCTOP,    "params": [ 13.72, 27.18, -2.0 ] },
	"8056": { "type": TYPE_RECTANGLE, "params": [ 11.94, 28.19 ] },
	"8057": { "type": TYPE_RECTANGLE, "params": [ 8.64, 28.19 ] },
	"8061": { "type": TYPE_RECTANGLE, "params": [ 12.70, 25.40 ] },
	"8062": { "type": TYPE_RECTANGLE, "params": [ 8.32, 18.03 ] },
	"8063": { "type": TYPE_RECTANGLE, "params": [ 17.15, 18.03 ] },
	"8064": { "type": TYPE_RECTANGLE, "params": [ 14.99, 16.26 ] },
	"8065": { "type": TYPE_RECTANGLE, "params": [ 53.59, 20.32 ] },
	"8069": { "type": TYPE_RECTANGLE, "params": [ 9.40, 19.81 ] },
	"8070": { "type": TYPE_RECTANGLE, "params": [ 19.05, 19.94 ] },
	"8071": { "type": TYPE_RECTANGLE, "params": [ 11.56, 15.49 ] },
	"8072": { "type": TYPE_ARCTOP,    "params": [ 9.91, 18.03, -2.0 ] },
	"8074": { "type": TYPE_RECTANGLE, "params": [ 12.70, 3.86 ] },
	"8088": { "type": TYPE_RECTANGLE, "params": [ 11.18, 24.89 ] },
	"8089": { "type": TYPE_RECTANGLE, "params": [ 16.51, 13.46 ] },
	"8090": { "type": TYPE_RECTANGLE, "params": [ 11.18, 19.81 ] },
	"8094": { "type": TYPE_RECTANGLE, "params": [ 29.97, 27.94 ] },
	"8095": { "type": TYPE_RECTANGLE, "params": [ 20.07, 27.94 ] },
	"8096": { "type": TYPE_RECTANGLE, "params": [ 9.78, 27.94 ] },
	"8097": { "type": TYPE_RECTANGLE, "params": [ 9.40, 20.96 ] },
	"8098": { "type": TYPE_RECTANGLE, "params": [ 19.94, 21.08 ] },
	"8100": { "type": TYPE_RECTANGLE, "params": [ 13.46, 41.40 ] },
	"8102": { "type": TYPE_RECTANGLE, "params": [ 12.70, 25.40 ] },
	"8103": { "type": TYPE_RECTANGLE, "params": [ 19.05, 19.05 ] },
	"8104": { "type": TYPE_RECTANGLE, "params": [ 28.96, 19.05 ] },
	"8105": { "type": TYPE_RECTANGLE, "params": [ 9.14, 14.73 ] },
	"8106": { "type": TYPE_RECTANGLE, "params": [ 19.05, 14.73 ] },
	"8113": { "type": TYPE_ROUNDTOP,  "params": [ 8.64, 20.96 ] },
	"8126": { "type": TYPE_RECTANGLE, "params": [ 20.57, 24.89 ] },
	"8127": { "type": TYPE_RECTANGLE, "params": [ 31.12, 24.89 ] },
	"8131": { "type": TYPE_RECTANGLE, "params": [ 9.14, 19.81 ] },
	"8136": { "type": TYPE_RECTANGLE, "params": [ 10.16, 19.05 ] },
	"8137": { "type": TYPE_RECTANGLE, "params": [ 24.26, 19.30 ] },
	"8138": { "type": TYPE_RECTANGLE, "params": [ 23.50, 25.40 ] },
	"8139": { "type": TYPE_RECTANGLE, "params": [ 9.91, 12.70 ] },
	"8149": { "type": TYPE_CIRCLE,    "params": [ 10.54 ] },
	"8153": { "type": TYPE_RECTANGLE, "params": [ 9.78, 20.57 ] },
	"8157": { "type": TYPE_RECTANGLE, "params": [ 11.94, 27.94 ] },
	"8159": { "type": TYPE_RECTANGLE, "params": [ 23.88, 19.81 ] },
	"8161": { "type": TYPE_RECTANGLE, "params": [ 36.07, 19.81 ] },
	"8163": { "type": TYPE_RECTANGLE, "params": [ 11.68, 25.91 ] },
	"8200": { "type": TYPE_ROUNDTOP,  "params": [ 8.51, 17.65 ] },
	"8201": { "type": TYPE_RECTANGLE, "params": [ 9.40, 21.34 ] },
	"8202": { "type": TYPE_ROUNDTOP,  "params": [ 8.64, 23.11 ] },
	"8203": { "type": TYPE_ROUNDTOP,  "params": [ 8.64, 11.18 ] },
	"8205": { "type": TYPE_ROUNDTOP,  "params": [ 8.64, 20.96 ] },
	"8217": { "type": TYPE_RECTANGLE, "params": [ 10.16, 17.53 ] },
	"8218": { "type": TYPE_RECTANGLE, "params": [ 8.64, 15.24 ] },
	"8236": { "type": TYPE_RECTANGLE, "params": [ 6.35, 17.40 ] },
	"8237": { "type": TYPE_RECTANGLE, "params": [ 8.89, 17.40 ] },
	"8238": { "type": TYPE_RECTANGLE, "params": [ 6.35, 17.40 ] },
	"8239": { "type": TYPE_RECTANGLE, "params": [ 8.89, 17.40 ] },
	"8240": { "type": TYPE_RECTANGLE, "params": [ 9.65, 20.57 ] },
	"8241": { "type": TYPE_RECTANGLE, "params": [ 10.29, 20.57 ] },
	"8242": { "type": TYPE_RECTANGLE, "params": [ 6.35, 12.70 ] },
	"8243": { "type": TYPE_RECTANGLE, "params": [ 14.22, 8.64 ] },
	"8244": { "type": TYPE_RECTANGLE, "params": [ 9.53, 23.75 ] },
	"8245": { "type": TYPE_RECTANGLE, "params": [ 13.34, 23.75 ] },
	"8250": { "type": TYPE_RECTANGLE, "params": [ 9.78, 16.26 ] },
	"8251": { "type": TYPE_RECTANGLE, "params": [ 8.00, 22.48 ] },
	"8301": { "type": TYPE_RECTANGLE, "params": [ 11.18, 25.40 ] },
	"8302": { "type": TYPE_RECTANGLE, "params": [ 11.43, 22.73 ] },
	"8303": { "type": TYPE_RECTANGLE, "params": [ 11.43, 13.59 ] },
	"8304": { "type": TYPE_RECTANGLE, "params": [ 6.73, 9.27 ] },
	"8305": { "type": TYPE_RECTANGLE, "params": [ 6.22, 6.22 ] },
	"8306": { "type": TYPE_RECTANGLE, "params": [ 10.16, 9.27 ] },
	"8323": { "type": TYPE_RECTANGLE, "params": [ 8.00, 11.05 ] },
}

tichyDoors = {
	"8009": { "type": TYPE_RECTANGLE, "params": [ 9.65, 23.88 ] },
	"8015": { "type": TYPE_RECTANGLE, "params": [ 21.59, 24.89 ] },
	"8022": { "type": TYPE_ARCTOP,    "params": [ 24.38, 34.29, -13.9 ] },
	"8032": { "type": TYPE_RECTANGLE, "params": [ 10.16, 24.38 ] },
	"8033": { "type": TYPE_RECTANGLE, "params": [ 9.65, 29.46 ] },
	"8038": { "type": TYPE_RECTANGLE, "params": [ 30.48, 34.54 ] },
	"8049": { "type": TYPE_RECTANGLE, "params": [ 11.18, 23.88 ] },
	"8050": { "type": TYPE_RECTANGLE, "params": [ 11.18, 23.88 ] },
	"8053": { "type": TYPE_RECTANGLE, "params": [ 28.45, 28.45 ] },
	"8066": { "type": TYPE_RECTANGLE, "params": [ 27.94, 27.18 ] },
	"8108": { "type": TYPE_RECTANGLE, "params": [ 12.70, 17.78 ] },
	"8111": { "type": TYPE_RECTANGLE, "params": [ 22.23, 34.54 ] },
	"8112": { "type": TYPE_RECTANGLE, "params": [ 14.48, 33.02 ] },
	"8116": { "type": TYPE_RECTANGLE, "params": [ 11.94, 29.85 ] },
	"8118": { "type": TYPE_RECTANGLE, "params": [ 12.70, 34.29 ] },
	"8119": { "type": TYPE_RECTANGLE, "params": [ 12.70, 34.29 ] },
	"8121": { "type": TYPE_RECTANGLE, "params": [ 27.31, 38.86 ] },
	"8124": { "type": TYPE_RECTANGLE, "params": [ 16.76, 24.77 ] },
	"8125": { "type": TYPE_RECTANGLE, "params": [ 24.13, 32.77 ] },
	"8130": { "type": TYPE_RECTANGLE, "params": [ 11.43, 29.21 ] },
	"8132": { "type": TYPE_RECTANGLE, "params": [ 10.67, 33.27 ] },
	"8140": { "type": TYPE_RECTANGLE, "params": [ 19.30, 33.53 ] },
	"8150": { "type": TYPE_RECTANGLE, "params": [ 10.54, 24.26 ] },
	"8151": { "type": TYPE_RECTANGLE, "params": [ 20.07, 24.13 ] },
	"8189": { "type": TYPE_RECTANGLE, "params": [ 24.51, 34.54 ] },
	"8190": { "type": TYPE_RECTANGLE, "params": [ 24.51, 34.54 ] },
	"8191": { "type": TYPE_RECTANGLE, "params": [ 11.94, 25.02 ] },
	"8192": { "type": TYPE_RECTANGLE, "params": [ 22.23, 25.07 ] },
	"8194": { "type": TYPE_RECTANGLE, "params": [ 11.68, 29.92 ] },
	"8195": { "type": TYPE_RECTANGLE, "params": [ 11.68, 24.89 ] },
	"8196": { "type": TYPE_RECTANGLE, "params": [ 11.68, 29.92 ] },
	"8197": { "type": TYPE_RECTANGLE, "params": [ 11.68, 24.89 ] },
	"8198": { "type": TYPE_RECTANGLE, "params": [ 22.23, 24.89 ] },
	"8199": { "type": TYPE_RECTANGLE, "params": [ 22.23, 24.89 ] },
	"8324": { "type": TYPE_RECTANGLE, "params": [ 8.00, 23.75 ] },
}

margin = 0.5

class MainFrame(wx.Frame):
	def __init__(self, toolInfo, speedInfo, parent):
		self.parent = parent
		self.settings = parent.settings
		self.images = self.parent.images
		
		wx.Frame.__init__(self, None, size=(480, 800), title="")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = TichyPanel(toolInfo, speedInfo, self)
		sizer.Add(self.panel)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def okToClose(self):
		return self.panel.okToClose()
	
	def onClose(self, _):
		return self.panel.onClose(None)

class TichyPanel(wx.Panel, CNCObject):
	seqNo = 1
	def __init__(self, toolInfo, speedInfo, parent):
		CNCObject.__init__(self, parent, "object:tichy")
		self.toolInfo = toolInfo
		
		self.modified = False
		self.unsaved = False
		self.viewTitle = "Tichy %d" % TichyPanel.seqNo
		self.titleText = "G Code Generator: %s" % self.viewTitle
		TichyPanel.seqNo += 1
		
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		sizer = wx.GridBagSizer(wx.HORIZONTAL)
		sizer.Add(10, 10, wx.GBPosition(0, 4))
		ln = 1
		
		self.setTitleFlag()

		t = wx.StaticText(self, wx.ID_ANY, "Tichy Part Number")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		
		self.cbTichyPart = wx.ComboBox(self, wx.ID_ANY, "", 
				 choices=sorted(tichyWindows.keys()) + sorted(tichyDoors.keys()),
				 style=wx.CB_DROPDOWN
				 )
		self.cbTichyPart.SetSelection(0)
		self.Bind(wx.EVT_COMBOBOX, self.onCbTichyPart, self.cbTichyPart)
		self.addWidget(self.cbTichyPart, "tichypart")
		sizer.Add(self.cbTichyPart, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		st = wx.StaticText(self, wx.ID_ANY, "")
		sizer.Add(st, pos=(ln, 2), span=(1, 2), flag=wx.LEFT, border=20)
		self.stInfo = st
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
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=self.settings.safez, min=0.0, max=5.0, inc=0.1, size=SPINSIZE)
		sc.SetValue(self.settings.safez)
		sc.SetDigits(2)
		self.scSafeZ = sc
		self.addWidget(self.scSafeZ, "safez")
		sizer.Add(self.scSafeZ, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Tool Diameter")
		td = "%6.3f" % self.resolveToolDiameter(toolInfo)
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teToolDiam = wx.TextCtrl(self, wx.ID_ANY, td, style=wx.TE_RIGHT)
		self.addWidget(self.teToolDiam, "tooldiameter")
		sizer.Add(self.teToolDiam, pos=(ln, 1), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Total Depth")
		td = "%6.3f" % self.settings.totaldepth
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		self.teTotalDepth = wx.TextCtrl(self, wx.ID_ANY, td, style=wx.TE_RIGHT)
		self.addWidget(self.teTotalDepth, "depth")
		sizer.Add(self.teTotalDepth, pos=(ln, 1), flag=wx.LEFT, border=10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Depth/Pass")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=speedInfo["depthperpass"], min=0.1, max=5.0, inc=0.1, size=SPINSIZE)
		sc.SetValue(speedInfo["depthperpass"])
		sc.SetDigits(2)
		self.scPassDepth = sc
		self.addWidget(self.scPassDepth, "passdepth")
		sizer.Add(self.scPassDepth, pos=(ln, 3), flag=wx.LEFT, border=10)
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Starting Point")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)	
		sizer.Add(self.getStartingPoints(), pos=(ln, 1), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	

		t = wx.StaticText(self, wx.ID_ANY, "Cutting Direction")
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sizer.Add(self.getCuttingDirection(), pos=(ln, 3), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	
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
		sc.SetRange(1,10000)
		sc.SetValue(g0xy)
		self.scFeedXYG0 = sc
		self.addWidget(self.scFeedXYG0, "feedXYG0")
		sizer.Add(self.scFeedXYG0, pos=(ln, 1), flag=wx.LEFT, border=10)		
		
		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate XY (G1)")
		g1xy = speedInfo["G1XY"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=g1xy, size=SPINSIZE)
		sc.SetRange(1,10000)
		sc.SetValue(g1xy)
		self.scFeedXYG1 = sc
		self.addWidget(self.scFeedXYG1, "feedXYG1")
		sizer.Add(self.scFeedXYG1, pos=(ln, 3), flag=wx.LEFT, border=10)		
		ln += 1

		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate Z (G0)")
		g0z = speedInfo["G0Z"]
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=g0z, size=SPINSIZE)
		sc.SetRange(1,10000)
		sc.SetValue(g0z)
		self.scFeedZG0 = sc
		self.addWidget(self.scFeedZG0, "feedZG0")
		sizer.Add(self.scFeedZG0, pos=(ln, 1), flag=wx.LEFT, border=10)		
		
		t = wx.StaticText(self, wx.ID_ANY, "Feed Rate Z (G1)")
		g1z = speedInfo["G1Z"]
		sizer.Add(t, pos=(ln, 2), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=g1z, size=SPINSIZE)
		sc.SetRange(1,10000)
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
		
		self.enableStartingPoints()
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def getTichyPartType(self, cbv):
		if cbv in tichyWindows.keys():
			return tichyWindows[cbv]["type"]
		return tichyDoors[cbv]["type"]
		
	def getTichyPartParams(self, cbv):
		if cbv in tichyWindows.keys():
			return tichyWindows[cbv]["params"]
		return tichyDoors[cbv]["params"]
		
	def getStartingPoints(self):
		labels = ["Lower Left", "Upper Left", "Lower Right", "Upper Right", "Center"]
		self.rbStartPoints = []
		sz = wx.BoxSizer(wx.VERTICAL)
		self.startPoints = []
		for i in range(len(labels)):
			if i == 0:
				style = wx.RB_GROUP
			else:
				style = 0
			r = wx.RadioButton(self, wx.ID_ANY, labels[i], style=style)
			self.addWidget(r, labels[i])
			sz.Add(r)
			self.rbStartPoints.append(r)
			self.startPoints.append([labels[i], r])
		return sz
		
	def enableStartingPoints(self):
		cbv = self.cbTichyPart.GetValue()
		tp = self.getTichyPartType(cbv)
		p = self.getTichyPartParams(cbv)
		if tp == TYPE_RECTANGLE:
			info = "Rectangle %6.2fw x %6.2fh" % (p[0], p[1])
		elif tp == TYPE_ROUNDTOP:
			info = "Round Top %6.2fw x %6.2fh" % (p[0], p[1])
		elif tp == TYPE_ARCTOP:
			info = "Arc Top %6.2fw x %6.2fh y offset %6.2f" % (p[0], p[1], p[2])
		elif tp == TYPE_CIRCLE:
			info = "Circle diameter %6.2f" % p[0]
		else:
			info = ""
			
		self.stInfo.SetLabel(info)
		
		for l, r in self.startPoints:
			if l != "Center":
				if tp == TYPE_CIRCLE:
					r.Enable(False)
				else:
					r.Enable(True)
			else:
				if l == "Center":
					if tp == TYPE_CIRCLE:
						r.SetValue(True)
	
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
		self.setState(True, False)
		flag = self.cbAddSpeed.IsChecked()
		self.scFeedXYG0.Enable(flag)
		self.scFeedXYG1.Enable(flag)
		self.scFeedZG0.Enable(flag)
		self.scFeedZG1.Enable(flag)
		
	def onCbTichyPart(self, _):
		self.enableStartingPoints()
		
	def bGeneratePressed(self, _):
		self.bSave.Enable(False)
		self.bVisualize.Enable(False)
		self.gcl.clear()
		self.gcode = []
		
		tpn = self.cbTichyPart.GetValue()
		tp = self.getTichyPartType(tpn)
		p = self.getTichyPartParams(tpn)
		
		if tp == TYPE_RECTANGLE:
			self.tichyRectangle(p, self.settings.metric)
		elif tp == TYPE_ROUNDTOP:
			self.tichyRoundTop(p+[0], self.settings.metric)
		elif tp == TYPE_ARCTOP:
			self.tichyRoundTop(p, self.settings.metric)
		elif tp == TYPE_CIRCLE:
			self.tichyCircle(p, self.settings.metric)
		
			
	def tichyRectangle(self, p, metric):
		width = p[0] + margin
		height = p[1] + margin
		if not metric:
			width = float(width) / 25.4;
			height = float(height) / 25.4
		
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
		feedxyG1 = self.scFeedXYG1.GetValue()
		passdepth = self.scPassDepth.GetValue()

		try:
			depth = float(self.teTotalDepth.GetValue())
		except:
			errs.append("Depth")	
		try:
			tdiam = float(self.teToolDiam.GetValue())
		except:
			errs.append("Tool Diameter")	

		if not ValidateNoEntryErrors(self, errs):
			return
			
		if not ValidateToolSize(self, tdiam, height, "Height"):
			return
		if not ValidateToolSize(self, tdiam, width, "Width"):
			return

		if self.toolInfo["diameter"] == tdiam:
			toolname = self.toolInfo["name"]
		else:
			toolname = None
			
		self.gcode = self.preamble(self.settings, self.viewTitle, tdiam, toolname, self.settings.metric)					
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % safez)
		
		self.tDiam = tdiam
		rad = float(tdiam)/2.0
		if self.settings.annotate:
			self.gcode.append("(Tichy Rectangle (%6.2f,%6.2f) to (%6.2f,%6.2f) depth from %6.2f to %6.2f) dpp %6.2f" % (sx, sy, width, height, sz, depth, passdepth))

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

		cd = self.getChosen(self.rbCutDir)
		if cd != "Clockwise":
			np = points[::-1]
			points = np
	
		if self.settings.annotate:
			self.gcode.append("(Start point: %s)" % sp)
			self.gcode.append("(Cutting direction: %s)" % cd)

		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
		self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (points[0][0], points[0][1]))

		
		passes = int(math.ceil(depth/passdepth))
		
		cz = sz
		for i in range(passes):
			cz -= passdepth
			if cz < -depth:
				cz = -depth
			if self.settings.annotate:
				self.gcode.append("(Pass number %d at depth %f)" % (i, cz))
				
			self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (cz))
			for p in points[1:]:
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (p[0], p[1]))
			
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
		if self.settings.annotate:
			self.gcode.append("(End object %s)" % self.viewTitle)
				
		self.gcl.updateList(self.gcode)
		self.bSave.Enable()
		self.bVisualize.Enable()
		self.setState(False, True)
			
	def tichyRoundTop(self, p, metric):
		width = p[0] + margin
		height = p[1] + margin
		yoff = p[2]
		if not metric:
			width = float(width) / 25.4;
			height = float(height) / 25.4
			yoff = yoff / 25.4
		
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
		feedxyG1 = self.scFeedXYG1.GetValue()

		passdepth = self.scPassDepth.GetValue()

		try:
			depth = float(self.teTotalDepth.GetValue())
		except:
			errs.append("Depth")	
		try:
			tdiam = float(self.teToolDiam.GetValue())
		except:
			errs.append("Tool Diameter")	

		if not ValidateNoEntryErrors(self, errs):
			return
			
		if not ValidateToolSize(self, tdiam, height, "Height"):
			return
		if not ValidateToolSize(self, tdiam, width, "Width"):
			return

		if self.toolInfo["diameter"] == tdiam:
			toolname = self.toolInfo["name"]
		else:
			toolname = None			

		self.gcode = self.preamble(self.settings, self.viewTitle, tdiam, toolname, self.settings.metric)					
		
		self.tDiam = tdiam
		rad = float(tdiam)/2.0
		if self.settings.annotate:
			if yoff == 0:
				self.gcode.append("(Tichy Round Top (%6.2f,%6.2f) to (%6.2f,%6.2f) depth from %6.2f to %6.2f) dpp %6.2f" % (sx, sy, width, height, sz, depth, passdepth))
			else:
				self.gcode.append("(Tichy Arc Top (%6.2f,%6.2f) to (%6.2f,%6.2f) y offset %6.2f depth from %6.2f to %6.2f) dpp %6.2f" % (sx, sy, width, height, yoff, sz, depth, passdepth))

		points = [[sx, sy], [sx, sy+height], [sx+width, sy+height], [sx+width, sy], [sz, sy]]
			
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

		cd = self.getChosen(self.rbCutDir)
		if cd != "Clockwise":
			np = points[::-1]
			points = np
			cw = False
			cmd = "G3"
		else:
			cw = True
			cmd = "G2"
			
		wrad = (float(width)-float(tdiam))/2.0

		if self.settings.annotate:
			self.gcode.append("(Start point: %s)" % sp)
			self.gcode.append("(Cutting direction: %s)" % cd)

		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
		self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (points[0][0], points[0][1]))
		
		passes = int(math.ceil(depth/passdepth))
		
		cz = sz
		for i in range(passes):
			cz -= passdepth
			if cz < -depth:
				cz = -depth
			if self.settings.annotate:
				self.gcode.append("(Pass number %d at depth %f)" % (i, cz))
				
			self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (cz))
			self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (points[1][0], points[1][1]))
			if cw:
				# arc here to point 2
				self.gcode.append((cmd+self.IJTerm("I", wrad)+self.IJTerm("J", yoff)+" X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1))
								% (points[2][0], points[2][1]))
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (points[3][0], points[3][1]))
			else:
				self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (points[2][0], points[2][1]))
				# arc here to point 3
				self.gcode.append((cmd+self.IJTerm("I", -wrad)+self.IJTerm("J", yoff)+" X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1))
								% (points[3][0], points[3][1]))
			self.gcode.append(("G1 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (points[4][0], points[4][1]))
			
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
		if self.settings.annotate:
			self.gcode.append("(End object %s)" % self.viewTitle)
				
		self.gcl.updateList(self.gcode)
		self.bSave.Enable()
		self.bVisualize.Enable()
		self.setState(False, True)
		
	def tichyCircle(self, p, metric):			
		diam = p[0] + margin
		if not metric:
			diam = float(diam) / 25.4;
			
		self.fmt = "%%0.%df" % self.settings.decimals

		errs = []
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
			
		safez = self.scSafeZ.GetValue()
			
		addspeed = self.cbAddSpeed.IsChecked()
		feedzG0 = self.scFeedZG0.GetValue()
		feedzG1 = self.scFeedZG1.GetValue()
		feedxyG0 = self.scFeedXYG0.GetValue()
		feedxyG1 = self.scFeedXYG1.GetValue()
		
		passdepth = self.scPassDepth.GetValue()
		
		try:
			depth = float(self.teTotalDepth.GetValue())
		except:
			errs.append("Depth")
		try:
			tdiam = float(self.teToolDiam.GetValue())
		except:
			errs.append("Tool Diameter")

		if not ValidateNoEntryErrors(self, errs):
			return
			
		if not ValidateToolSize(self, tdiam, diam, "Circle Diameter"):
			return
		
		diam -= tdiam
		rad = diam/2

		if self.toolInfo["diameter"] == tdiam:
			toolname = self.toolInfo["name"]
		else:
			toolname = None			

		self.gcode = self.preamble(self.settings, self.viewTitle, tdiam, toolname, self.settings.metric)					
			
		self.tDiam = tdiam
		if self.settings.annotate:
			self.gcode.append("(Tichy Circle center (%6.2f,%6.2f) radius %6.2f depth from %6.2f to %6.2f dpp %6.2f" % (sx, sy, rad, sz, depth, passdepth))	
			
		cd = self.getChosen(self.rbCutDir)
		if cd == "Clockwise":
			cmd = "G2"
		else:
			cmd = "G3"

		passes = int(math.ceil(depth/passdepth))
				
		if self.settings.annotate:
			self.gcode.append("(Cutting direction: %s)" % cd)

		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
		self.gcode.append(("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG0)) % (sx, sy-rad))
			
		cz = sz
		for i in range(passes):
			cz -= passdepth
			if cz < -depth:
				cz = -depth
				
			if self.settings.annotate:
				self.gcode.append("(Pass number %d at depth %f)" % (i, cz))

			self.gcode.append(("G1 Z"+self.fmt+self.speedTerm(addspeed, feedzG1)) % (cz))

			self.gcode.append((cmd+" J"+self.fmt+" X"+self.fmt+" Y"+self.fmt+self.speedTerm(addspeed, feedxyG1)) % (rad, sx, sy-rad))

					
		self.gcode.append(("G0 Z"+self.fmt+self.speedTerm(addspeed, feedzG0)) % (safez))
		if self.settings.annotate:
			self.gcode.append("(End object %s)" % self.viewTitle)
		self.gcl.updateList(self.gcode)
		self.bSave.Enable(True)
		self.bVisualize.Enable()
		self.setState(False, True)

			


