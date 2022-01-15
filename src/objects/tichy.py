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
TYPE_HALFROUND = 5
tichyWindows = {
	"8010": { "type": TYPE_RECTANGLE, "params": [ 13.21, 11.94 ], "desc": "6 LITE WINDOW" },
	"8014": { "type": TYPE_RECTANGLE, "params": [ 10.92, 17.27 ], "desc": "4/4 DOUBLE HUNG WINDOW" },
	"8023": { "type": TYPE_RECTANGLE, "params": [ 9.40, 8.38 ], "desc": "6 LITE ATTIC WINDOW" },
	"8024": { "type": TYPE_RECTANGLE, "params": [ 11.68, 19.81 ], "desc": "6/6 DOUBLE HUNG WINDOW" },
	"8025": { "type": TYPE_RECTANGLE, "params": [ 9.14, 19.05 ], "desc": "2/2 DOUBLE HUNG WINDOW" },
	"8026": { "type": TYPE_RECTANGLE, "params": [ 12.95, 8.89 ], "desc": "6 LITE WINDOW" },
	"8028": { "type": TYPE_RECTANGLE, "params": [ 9.40, 19.81 ], "desc": "4/4 DOUBLE HUNG WINDOW" },
	"8029": { "type": TYPE_RECTANGLE, "params": [ 8.64, 15.75 ], "desc": "4/4 DOUBLE HUNG WINDOW" },
	"8030": { "type": TYPE_RECTANGLE, "params": [ 10.16, 24.89 ], "desc": "4/4 DOUBLE HUNG WINDOW" },
	"8031": { "type": TYPE_RECTANGLE, "params": [ 9.65, 21.08 ], "desc": "2/2 DOUBLE HUNG WINDOW" },
	"8042": { "type": TYPE_RECTANGLE, "params": [ 16.26, 10.67 ], "desc": "HORIZONTAL SLIDER" },
	"8043": { "type": TYPE_RECTANGLE, "params": [ 11.43, 19.81 ], "desc": "2/2 DOUBLE HUNG WINDOW" },
	"8047": { "type": TYPE_ROUNDTOP,  "params": [ 9.65, 17.02 ], "desc": "ROUND TOP WINDOW" },
	"8048": { "type": TYPE_ROUNDTOP,  "params": [ 5.59, 10.16 ], "desc": "ROUND TOP WINDOW" },
	"8054": { "type": TYPE_RECTANGLE, "params": [ 13.72, 27.18 ], "desc": "9/9 DOUBLE HUNG WINDOW" },
	"8055": { "type": TYPE_ARCTOP,    "params": [ 13.72, 27.18, -2.0 ], "desc": "9/9 DOUBLE HUNG ARCH TOP WINDOW" },
	"8056": { "type": TYPE_RECTANGLE, "params": [ 11.94, 28.19 ], "desc": "9/9 DOUBLE HUNG WINDOW" },
	"8057": { "type": TYPE_RECTANGLE, "params": [ 8.64, 28.19 ], "desc": "6/6 DOUBLE HUNG WINDOW" },
	"8061": { "type": TYPE_RECTANGLE, "params": [ 12.70, 25.40 ], "desc": "2/2 DOUBLE HUNG WINDOW" },
	"8062": { "type": TYPE_RECTANGLE, "params": [ 8.32, 18.03 ], "desc": "2/2 DOUBLE HUNG WINDOW" },
	"8063": { "type": TYPE_RECTANGLE, "params": [ 17.15, 18.03 ], "desc": "2/2 DOUBLE UNIT DBL HUNG WINDOW" },
	"8064": { "type": TYPE_RECTANGLE, "params": [ 14.99, 16.26 ], "desc": "4/4 DBL HUNG TWO UNIT WINDOW" },
	"8065": { "type": TYPE_RECTANGLE, "params": [ 53.59, 20.32 ], "desc": "4/4 DBL HUNG SIX UNIT WINDOW" },
	"8067": { "type": TYPE_RECTANGLE, "params": [ 9.4, 9.14 ], "desc": "WORK CAR WINDOW" },
	"8068": { "type": TYPE_RECTANGLE, "params": [ 6.6, 9.4 ], "desc": "WORK CAR WINDOW" },
	"8069": { "type": TYPE_RECTANGLE, "params": [ 9.40, 19.81 ], "desc": "4/4 DBL HUNG OPEN WINDOWS" },
	"8070": { "type": TYPE_RECTANGLE, "params": [ 19.05, 19.94 ], "desc": "4/4 DBL HUNG TWO UNIT WINDOW" },
	"8071": { "type": TYPE_RECTANGLE, "params": [ 11.56, 15.49 ], "desc": "8/8 DBL HUNG WINDOW" },
	"8072": { "type": TYPE_ARCTOP,    "params": [ 9.91, 18.03, -2.0 ], "desc": "2/2 ARCH TOP WINDOW" },
	"8074": { "type": TYPE_RECTANGLE, "params": [ 12.70, 3.86 ], "desc": "2 PANE SMALL WINDOW" },
	"8088": { "type": TYPE_RECTANGLE, "params": [ 11.18, 24.89 ], "desc": "4/4 DBL HUNG ADJUSTABLE SASH" },
	"8089": { "type": TYPE_RECTANGLE, "params": [ 16.51, 13.46 ], "desc": "HORIZONTAL SLIDER WITH ADJUSTABLE SASH" },
	"8090": { "type": TYPE_RECTANGLE, "params": [ 11.18, 19.81 ], "desc": "6 PANE WINDOW WITH 2 PANE TILT OUT TOP SASH" },
	"8094": { "type": TYPE_RECTANGLE, "params": [ 29.97, 27.94 ], "desc": "1/1 TRIPLE UNIT WINDOW" },
	"8095": { "type": TYPE_RECTANGLE, "params": [ 20.07, 27.94 ], "desc": "1/1 DOUBLE UNIT WINDOW" },
	"8096": { "type": TYPE_RECTANGLE, "params": [ 9.78, 27.94 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8097": { "type": TYPE_RECTANGLE, "params": [ 9.40, 20.96 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8098": { "type": TYPE_RECTANGLE, "params": [ 19.94, 21.08 ], "desc": "2/2 DOUBLE UNIT DBL HUNG WINDOW" },
	"8100": { "type": TYPE_RECTANGLE, "params": [ 13.46, 41.40 ], "desc": "27 PANE WINDOW" },
	"8102": { "type": TYPE_RECTANGLE, "params": [ 12.70, 25.40 ], "desc": "SINGLE SASH WINDOW" },
	"8103": { "type": TYPE_RECTANGLE, "params": [ 19.05, 19.05 ], "desc": "DOUBLE 2/2 DBL HUNG WINDOW" },
	"8104": { "type": TYPE_RECTANGLE, "params": [ 28.96, 19.05 ], "desc": "#8104 TRIPLE 2/2 DBL HUNG WINDOW" },
	"8105": { "type": TYPE_RECTANGLE, "params": [ 9.14, 14.73 ], "desc": "2/2 DOUBLE HUNG WINDOW" },
	"8106": { "type": TYPE_RECTANGLE, "params": [ 19.05, 14.73 ], "desc": "DOUBLE 2/2 DBL HUNG WINDOW" },
	"8113": { "type": TYPE_ROUNDTOP,  "params": [ 8.64, 20.96 ], "desc": "ROUND TOP WINDOW" },
	"8126": { "type": TYPE_RECTANGLE, "params": [ 20.57, 24.89 ], "desc": "4/4 DBL HUNG DBL UNIT WINDOW" },
	"8127": { "type": TYPE_RECTANGLE, "params": [ 31.12, 24.89 ], "desc": "4/4 TRIPLE UNIT WINDOW" },
	"8131": { "type": TYPE_RECTANGLE, "params": [ 9.14, 19.81 ], "desc": "4/4 DOUBLE HUNG WINDOW" },
	"8136": { "type": TYPE_RECTANGLE, "params": [ 10.16, 19.05 ], "desc": "12/12 DOUBLE HUNG WINDOW" },
	"8137": { "type": TYPE_RECTANGLE, "params": [ 24.26, 19.30 ], "desc": "4/4 DBL HUNG DBL UNIT WINDOW" },
	"8138": { "type": TYPE_RECTANGLE, "params": [ 23.50, 25.40 ], "desc": "2/2 STOREFRONT WINDOW" },
	"8139": { "type": TYPE_RECTANGLE, "params": [ 9.91, 12.70 ], "desc": "DOUBLE CASEMENT WINDOW" },
	"8149": { "type": TYPE_CIRCLE,    "params": [ 10.54 ], "desc": "ROUND WINDOW" },
	"8153": { "type": TYPE_RECTANGLE, "params": [ 9.78, 20.57 ], "desc": "6/6 DOUBLE HUNG WINDOW" },
	"8157": { "type": TYPE_RECTANGLE, "params": [ 11.94, 27.94 ], "desc": "18 PANE TOP TILT OUT INDUSTRIAL WINDOW" },
	"8159": { "type": TYPE_RECTANGLE, "params": [ 23.88, 19.81 ], "desc": "#8159 6/6 DOUBLE HUNG DOUBLE UNIT WINDOW" },
	"8161": { "type": TYPE_RECTANGLE, "params": [ 36.07, 19.81 ], "desc": "#8161 6/6 DOUBLE HUNG TRIPLE UNIT WINDOW" },
	"8163": { "type": TYPE_RECTANGLE, "params": [ 11.68, 25.91 ], "desc": "CENTER TILTING INDUSTRIAL WINDOW" },
	"8200": { "type": TYPE_ROUNDTOP,  "params": [ 8.51, 17.65 ], "desc": "1/1 ROUND TOP WINDOW" },
	"8201": { "type": TYPE_RECTANGLE, "params": [ 9.40, 21.34 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8202": { "type": TYPE_ROUNDTOP,  "params": [ 8.64, 23.11 ], "desc": "4/4 ROUND TOP WINDOW" },
	"8203": { "type": TYPE_ROUNDTOP,  "params": [ 8.64, 11.18 ], "desc": "4 PANE ROUND TOP WINDOW" },
	"8205": { "type": TYPE_ROUNDTOP,  "params": [ 8.64, 20.96 ], "desc": "4/4 ROUND TOP WINDOW" },
	"8217": { "type": TYPE_RECTANGLE, "params": [ 10.16, 17.53 ], "desc": "6/6 DOUBLE HUNG WINDOW" },
	"8218": { "type": TYPE_RECTANGLE, "params": [ 8.64, 15.24 ], "desc": "2/1 DOUBLE HUNG WINDOW" },
	"8229": { "type": TYPE_RECTANGLE, "params": [ 9.4, 5.33 ], "desc": "WORK CAR WINDOW" },
	"8236": { "type": TYPE_RECTANGLE, "params": [ 6.35, 17.40 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8237": { "type": TYPE_RECTANGLE, "params": [ 8.89, 17.40 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8238": { "type": TYPE_RECTANGLE, "params": [ 6.35, 17.40 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8239": { "type": TYPE_RECTANGLE, "params": [ 8.89, 17.40 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8240": { "type": TYPE_RECTANGLE, "params": [ 9.65, 20.57 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8241": { "type": TYPE_RECTANGLE, "params": [ 10.29, 20.57 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8242": { "type": TYPE_RECTANGLE, "params": [ 6.35, 12.70 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8243": { "type": TYPE_RECTANGLE, "params": [ 14.22, 8.64 ], "desc": "3 PANE HORIZONTAL WINDOW" },
	"8244": { "type": TYPE_RECTANGLE, "params": [ 9.53, 23.75 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8245": { "type": TYPE_RECTANGLE, "params": [ 13.34, 23.75 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8250": { "type": TYPE_RECTANGLE, "params": [ 9.78, 16.26 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8251": { "type": TYPE_RECTANGLE, "params": [ 8.00, 22.48 ], "desc": "1/1 DOUBLE HUNG WINDOW" },
	"8301": { "type": TYPE_RECTANGLE, "params": [ 11.18, 25.40 ], "desc": "DURANGO STATION WINDOW" },
	"8302": { "type": TYPE_RECTANGLE, "params": [ 11.43, 22.73 ], "desc": "RGS STATION WINDOW" },
	"8303": { "type": TYPE_RECTANGLE, "params": [ 11.43, 13.59 ], "desc": "2 PANE PEAKED WINDOW" },
	"8304": { "type": TYPE_RECTANGLE, "params": [ 6.73, 9.27 ], "desc": "VICTORIAN ATTIC WINDOW" },
	"8305": { "type": TYPE_RECTANGLE, "params": [ 6.22, 6.22 ], "desc": "SHED/ATTIC WINDOW" },
	"8306": { "type": TYPE_RECTANGLE, "params": [ 10.16, 9.27 ], "desc": "6 LITE WINDOW" },
	"8323": { "type": TYPE_RECTANGLE, "params": [ 8.00, 11.05 ], "desc": "6 PANE WINDOW" },
}

tichyDoors = {
	"8009": { "type": TYPE_RECTANGLE, "params": [ 9.65, 23.88 ], "desc": "4 LITE DOOR" },
	"8015": { "type": TYPE_RECTANGLE, "params": [ 21.59, 24.89 ], "desc": "DOUBLE STEEL DOOR" },
	"8022": { "type": TYPE_ARCTOP,    "params": [ 24.38, 34.29, -13.9 ], "desc": "FREIGHT DOOR" },
	"8032": { "type": TYPE_RECTANGLE, "params": [ 10.16, 24.38 ], "desc": "4 PANEL DOOR" },
	"8033": { "type": TYPE_RECTANGLE, "params": [ 9.65, 29.46 ], "desc": "4 LITE DOOR & TRANSOM" },
	"8038": { "type": TYPE_RECTANGLE, "params": [ 30.48, 34.54 ], "desc": "BAGGAGE DOOR" },
	"8049": { "type": TYPE_RECTANGLE, "params": [ 11.18, 23.88 ], "desc": "4 PANEL DOOR" },
	"8050": { "type": TYPE_RECTANGLE, "params": [ 11.18, 23.88 ], "desc": "2 LITE DOOR" },
	"8053": { "type": TYPE_RECTANGLE, "params": [ 28.45, 28.45 ], "desc": "BAGGAGE DOOR" },
	"8066": { "type": TYPE_RECTANGLE, "params": [ 27.94, 27.18 ], "desc": "LOADING DOCK DOOR" },
	"8108": { "type": TYPE_RECTANGLE, "params": [ 12.70, 17.78 ], "desc": "4 PANEL UTILITY DOOR" },
	"8111": { "type": TYPE_RECTANGLE, "params": [ 22.23, 34.54 ], "desc": "DOUBLE DOOR WITH TRANSOM" },
	"8112": { "type": TYPE_RECTANGLE, "params": [ 14.48, 33.02 ], "desc": "DOOR WITH IRON SHUTTERS" },
	"8116": { "type": TYPE_RECTANGLE, "params": [ 11.94, 29.85 ], "desc": "RESIDENTIAL DOOR" },
	"8118": { "type": TYPE_RECTANGLE, "params": [ 12.70, 34.29 ], "desc": "FACTORY DOOR 8118" },
	"8119": { "type": TYPE_RECTANGLE, "params": [ 12.70, 34.29 ], "desc": "FACTORY DOOR" },
	"8121": { "type": TYPE_RECTANGLE, "params": [ 27.31, 38.86 ], "desc": "DOUBLE DOOR WITH TRANSOM" },
	"8124": { "type": TYPE_RECTANGLE, "params": [ 16.76, 24.77 ], "desc": "DOUBLE 5 PANEL DOOR" },
	"8125": { "type": TYPE_RECTANGLE, "params": [ 24.13, 32.77 ], "desc": "FREIGHT DOOR/TRANSOM" },
	"8130": { "type": TYPE_RECTANGLE, "params": [ 11.43, 29.21 ], "desc": "RESIDENTIAL DOOR/TRANSOM" },
	"8132": { "type": TYPE_RECTANGLE, "params": [ 10.67, 33.27 ], "desc": "6 LITE DOOR & TRANSOM" },
	"8140": { "type": TYPE_RECTANGLE, "params": [ 19.30, 33.53 ], "desc": "DOUBLE DOOR WITH TRANSOM & IRON SHUTTERS" },
	"8150": { "type": TYPE_RECTANGLE, "params": [ 10.54, 24.26 ], "desc": "6 LITE DOOR" },
	"8151": { "type": TYPE_RECTANGLE, "params": [ 20.07, 24.13 ], "desc": "DOUBLE 6 LITE DOOR" },
	"8189": { "type": TYPE_RECTANGLE, "params": [ 24.51, 34.54 ], "desc": "DOUBLE DOOR & FRAME" },
	"8190": { "type": TYPE_RECTANGLE, "params": [ 24.51, 34.54 ], "desc": "DOUBLE DOOR & MASONRY FRAME" },
	"8191": { "type": TYPE_RECTANGLE, "params": [ 11.94, 25.02 ], "desc": "DOOR & FRAME" },
	"8192": { "type": TYPE_RECTANGLE, "params": [ 22.23, 25.07 ], "desc": "DOUBLE DOOR & FRAME" },
	"8194": { "type": TYPE_RECTANGLE, "params": [ 11.68, 29.92 ], "desc": "GLASS DOOR & FRAME" },
	"8195": { "type": TYPE_RECTANGLE, "params": [ 11.68, 24.89 ], "desc": "GLASS DOOR & FRAME" },
	"8196": { "type": TYPE_RECTANGLE, "params": [ 11.68, 29.92 ], "desc": "5 PANEL DOOR & FRAME" },
	"8197": { "type": TYPE_RECTANGLE, "params": [ 11.68, 24.89 ], "desc": "5 PANEL DOOR & FRAME" },
	"8198": { "type": TYPE_RECTANGLE, "params": [ 22.23, 24.89 ], "desc": "DOUBLE GLASS DOOR & FRAME" },
	"8199": { "type": TYPE_RECTANGLE, "params": [ 22.23, 24.89 ], "desc": "DOUBLE 5 PANEL DOOR & FRAME" },
	"8324": { "type": TYPE_RECTANGLE, "params": [ 8.00, 23.75 ], "desc": "6 LITE DOOR HO" },
}

margin = 0.5

class MainFrame(wx.Frame):
	def __init__(self, toolInfo, speedInfo, tichyImages, parent):
		self.parent = parent
		self.settings = parent.settings
		self.images = self.parent.images
		self.tichyImages = tichyImages
		
		wx.Frame.__init__(self, None, size=(480, 800), title="")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = TichyPanel(toolInfo, speedInfo, tichyImages, self)
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
	def __init__(self, toolInfo, speedInfo, tichyImages, parent):
		CNCObject.__init__(self, parent, "object:tichy")
		self.toolInfo = toolInfo
		
		self.modified = False
		self.unsaved = False
		self.viewTitle = "Tichy %d" % TichyPanel.seqNo
		self.titleText = "G Code Generator: %s" % self.viewTitle
		self.tichyImages = tichyImages
		TichyPanel.seqNo += 1
		
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		sizer = wx.GridBagSizer(wx.HORIZONTAL)
		sizer.Add(10, 10, wx.GBPosition(0, 4))
		ln = 1
		
		self.setTitleFlag()

		t = wx.StaticText(self, wx.ID_ANY, "Tichy Category")
		sizer.Add(t, pos=(ln, 0), flag=wx.LEFT+wx.ALIGN_CENTER_VERTICAL, border=20)		
		sizer.Add(self.getTichyCategories(), pos=(ln, 1), border=5, flag=wx.TOP+wx.BOTTOM+wx.ALIGN_CENTER_VERTICAL)	

		
		self.bmpTichyImage = wx.StaticBitmap(self, wx.ID_ANY, size=(75,75))
		sizer.Add(self.bmpTichyImage, pos=(ln, 2), span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL+wx.ALIGN_CENTER_HORIZONTAL, border=20)	
		ln += 1	
		
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
		
		sizer.Add(20, 20, wx.GBPosition(ln, 0))
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
		for rb in self.rbTichyCat:
			self.Bind(wx.EVT_RADIOBUTTON, self.onTichyCategory, rb)
		
		self.updateTichyDisplay()
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def onTichyCategory(self, evt):
		rb = evt.GetEventObject()
		l = rb.GetLabel().strip()
		print(l)

		
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
		
	def updateTichyDisplay(self):
		cbv = self.cbTichyPart.GetValue()
		tp = self.getTichyPartType(cbv)
		p = self.getTichyPartParams(cbv)
		
		for l, r in self.startPoints:
			if l != "Center":
				if tp == TYPE_CIRCLE:
					r.Enable(False)
				else:
					r.Enable(True)
			else:
				if tp == TYPE_CIRCLE:
					r.SetValue(True)

		p0 = p[0] if self.settings.metric else p[0]/25.4
		try:
			p1 = p[1] if self.settings.metric else p[1]/25.4
		except:
			p1 = 0
		try:
			p2 = p[2] if self.settings.metric else p[2]/25.4
		except:
			p2 = 0
			
		if self.settings.metric:
			units = "mm"
		else:
			units = "in"

		if tp == TYPE_RECTANGLE:
			info = "Rectangle %6.2f %s w x %6.2f %s h" % (p0, units, p1, units)
		elif tp == TYPE_ROUNDTOP:
			info = "Round Top %6.2f %s w x %6.2f %s h" % (p0, units, p1, units)
		elif tp == TYPE_ARCTOP:
			info = "Arc Top %6.2f %s w x %6.2f %s h,  y offset %6.2f %s" % (p0, units, p1, units, p2, units)
		elif tp == TYPE_CIRCLE:
			info = "Circle diameter %6.2f %s" % (p0, units)
		else:
			info = ""
			
		self.stInfo.SetLabel(info)
		bmp = self.tichyImages.getByName(cbv)
		if bmp is None:
			# no image found - clear the bitmap display
			bmp = wx.Bitmap(1,1)
			bmp.SetMaskColour('black')
			
		self.bmpTichyImage.SetBitmap(bmp)
	
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
	
	def getTichyCategories(self):
		labels = ["Framed windows", "Doors"]
		self.rbTichyCat = []
		sz = wx.BoxSizer(wx.VERTICAL)
		for i in range(len(labels)):
			if i == 0:
				style = wx.RB_GROUP
			else:
				style = 0
			r = wx.RadioButton(self, wx.ID_ANY, labels[i], style=style)
			self.addWidget(r, labels[i])
			sz.Add(r)
			self.rbTichyCat.append(r)
		return sz
		
	def onCbAddSpeed(self, _):
		self.setState(True, False)
		flag = self.cbAddSpeed.IsChecked()
		self.scFeedXYG0.Enable(flag)
		self.scFeedXYG1.Enable(flag)
		self.scFeedZG0.Enable(flag)
		self.scFeedZG1.Enable(flag)
		
	def onCbTichyPart(self, _):
		self.updateTichyDisplay()
		
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
		depth = self.scTotalDepth.GetValue()
		tdiam = self.scToolDiam.GetValue()

		if not ValidateNoEntryErrors(self, errs):
			return
			
		if not ValidateToolSize(self, tdiam, height, "Height"):
			return
		if not ValidateToolSize(self, tdiam, width, "Width"):
			return

		if self.databaseToolDiam == tdiam:
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

		depth = self.scTotalDepth.GetValue()
		tdiam = self.scToolDiam.GetValue()

		if not ValidateNoEntryErrors(self, errs):
			return
			
		if not ValidateToolSize(self, tdiam, height, "Height"):
			return
		if not ValidateToolSize(self, tdiam, width, "Width"):
			return

		if self.databaseToolDiam == tdiam:
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
			
		if not ValidateNoEntryErrors(self, errs):
			return

		safez = self.scSafeZ.GetValue()
			
		addspeed = self.cbAddSpeed.IsChecked()
		feedzG0 = self.scFeedZG0.GetValue()
		feedzG1 = self.scFeedZG1.GetValue()
		feedxyG0 = self.scFeedXYG0.GetValue()
		feedxyG1 = self.scFeedXYG1.GetValue()
		
		passdepth = self.scPassDepth.GetValue()
		
		depth = self.scTotalDepth.GetValue()
		tdiam = self.scToolDiam.GetValue()

			
		if not ValidateToolSize(self, tdiam, diam, "Circle Diameter"):
			return
		
		diam -= tdiam
		rad = diam/2

		if self.databaseToolDiam == tdiam:
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

			


