from sys import platform
import os, wx
import inspect

cmdFolder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
	
from settings import Settings, BTNDIM
from tools import Tools
from materials import Materials

import contours.line as line
import contours.rectangle as rect
import contours.circle as circ
import contours.arc as arc
import contours.regpolygon as polygon
import contours.polyline as polyline
import contours.roundedslot as rslot

import drills.rectangle as drillrect
import drills.circle as drillcirc
import drills.linear as drillline

import carving.grid as grid
import carving.diamonds as diamonds
import carving.hatch as hatch

import objects.tichy as tichy
import objects.box.tabbedbox as tabbedbox
import objects.stringer as stringer

from viewer.ncviewer import NCViewer
from merge import FileMergeDialog
from images import Images
from settingsdlg import SettingsDlg

wildcard = "G Code (*.nc)|*.nc|"	 \
		   "All files (*.*)|*.*"

weightSingle = 1
weightDouble = 16

MENU_FILE_VIEW = 101
MENU_FILE_MERGE = 102
MENU_OPTS_ANNOTATE = 201
MENU_OPTS_ADD_SPEED = 203
MENU_OPTS_METRIC = 204
MENU_OPTS_SETTINGS = 205

MENU_MATERIALS_BASE = 300
MENU_MATERIALS_MANAGE = 1300
MENU_TOOLS_BASE = 500
MENU_TOOLS_MANAGE = 1500

class MainFrame(wx.Frame):
	def __init__(self):
		self.wline = None
		self.wrect = None
		self.wcirc = None
		self.warc = None
		self.wpolygon = None
		self.wpolyline = None
		self.wrslot = None
		self.wdrillrect = None
		self.wdrillcirc = None
		self.wdrillline = None
		self.wgrid = None
		self.wdiamonds = None
		self.whatch = None
		self.wtichy = None
		self.wbox = None
		self.wstringer = None

		self.modified = False
		
		wx.Frame.__init__(self, None, size=(480, 800), title="G Code Generators - Main Menu")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetBackgroundColour("white")
		
		self.settings = Settings(self, cmdFolder)
		
		self.materials = Materials("materials.json")
		self.materialList = self.materials.getMaterials()
		if self.settings.material not in self.materialList:
			self.settings.material = self.materialList[0]
			self.settings.setModified()
			
		self.tools = Tools("tools.json", self.settings)
		self.toolList = self.tools.getTools()
		if self.settings.tool not in self.toolList:
			self.settings.tool = self.toolList[0]
			self.settings.setModified()
		self.toolInfo = self.tools.getTool(self.settings.tool)
		self.speedInfo = self.tools.getToolSpeeds(self.settings.tool, self.settings.material, self.materials)
		
		self.images = Images(os.path.join(cmdFolder, "images"))
			
		self.CreateStatusBar()
		
		menuBar = wx.MenuBar()
		
		self.menuFile = wx.Menu()
		self.menuFile.Append(MENU_FILE_VIEW, "&View", "View a G Code File")
		self.menuFile.Append(MENU_FILE_MERGE, "&Merge", "Merge G Code Files")
		menuBar.Append(self.menuFile, "&File")

		self.menuOpts = wx.Menu()
		self.menuOpts.Append(MENU_OPTS_ANNOTATE, "&Annotate", "Annotate G Code", wx.ITEM_CHECK)
		self.menuOpts.Append(MENU_OPTS_ADD_SPEED, "A&dd Speed Term", "Default setting for add speed term", wx.ITEM_CHECK)
		self.menuOpts.Append(MENU_OPTS_METRIC, "&Metric", "Use Metric Measurement System", wx.ITEM_CHECK)
		self.menuOpts.AppendSeparator()
		self.menuOpts.Append(MENU_OPTS_SETTINGS, "&Settings", "Enter/modify settings values")
		menuBar.Append(self.menuOpts, "&Options")

		self.createMaterialsMenu()					
		menuBar.Append(self.menuMaterials, "&Material")

		self.createToolsMenu()		
		menuBar.Append(self.menuTools, "&Tool")
				
		self.SetMenuBar(menuBar)
		self.menuBar = menuBar
		self.Bind(wx.EVT_MENU, self.onMenuFileView, id=MENU_FILE_VIEW)
		self.Bind(wx.EVT_MENU, self.onMenuFileMerge, id=MENU_FILE_MERGE)
		self.Bind(wx.EVT_MENU, self.onMenuOptsAnnotate, id=MENU_OPTS_ANNOTATE)
		self.Bind(wx.EVT_MENU, self.onMenuOptsAddSpeed, id=MENU_OPTS_ADD_SPEED)
		self.Bind(wx.EVT_MENU, self.onMenuOptsMetric, id=MENU_OPTS_METRIC)
		self.Bind(wx.EVT_MENU, self.onMenuOptsSettings, id=MENU_OPTS_SETTINGS)
		
		self.menuOpts.Check(MENU_OPTS_ANNOTATE, self.settings.annotate)
		self.menuOpts.Check(MENU_OPTS_ADD_SPEED, self.settings.addspeed)
		self.menuOpts.Check(MENU_OPTS_METRIC, self.settings.metric)
		
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		msizer = wx.BoxSizer(wx.VERTICAL)
		
		boxCont = wx.StaticBox(self, wx.ID_ANY, " Contours ")
		topBorder = boxCont.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder)
		
		szContours = wx.BoxSizer(wx.HORIZONTAL)
		szContours.AddSpacer(10)
		
		self.bLine = wx.BitmapButton(boxCont, wx.ID_ANY, self.images.pngContourline, size=BTNDIM)
		self.bLine.SetToolTip("Generate G Code for a straight line")
		szContours.Add(self.bLine)
		self.Bind(wx.EVT_BUTTON, self.bLinePressed, self.bLine)
		szContours.AddSpacer(5)
		
		self.bRect = wx.BitmapButton(boxCont, wx.ID_ANY, self.images.pngContourrectangle, size=BTNDIM)
		self.bRect.SetToolTip("Generate G Code for a rectangle")
		szContours.Add(self.bRect)
		self.Bind(wx.EVT_BUTTON, self.bRectPressed, self.bRect)
		szContours.AddSpacer(5)
		
		self.bCirc = wx.BitmapButton(boxCont, wx.ID_ANY, self.images.pngContourcircle, size=BTNDIM)
		self.bCirc.SetToolTip("Generate G Code for a circle")
		szContours.Add(self.bCirc)
		self.Bind(wx.EVT_BUTTON, self.bCircPressed, self.bCirc)
		szContours.AddSpacer(5)
		
		self.bArc = wx.BitmapButton(boxCont, wx.ID_ANY, self.images.pngContourarc, size=BTNDIM)
		self.bArc.SetToolTip("Generate G Code for an arc")
		szContours.Add(self.bArc)
		self.Bind(wx.EVT_BUTTON, self.bArcPressed, self.bArc)
		szContours.AddSpacer(5)
		
		self.bPolygon = wx.BitmapButton(boxCont, wx.ID_ANY, self.images.pngContourpolygon, size=BTNDIM)
		self.bPolygon.SetToolTip("Generate G Code for a regular polygon")
		szContours.Add(self.bPolygon)
		self.Bind(wx.EVT_BUTTON, self.bPolygonPressed, self.bPolygon)
		szContours.AddSpacer(5)
		
		self.bPolyline = wx.BitmapButton(boxCont, wx.ID_ANY, self.images.pngContourpolyline, size=BTNDIM)
		self.bPolyline.SetToolTip("Generate G Code for an open or close path")
		szContours.Add(self.bPolyline)
		self.Bind(wx.EVT_BUTTON, self.bPolylinePressed, self.bPolyline)
		szContours.AddSpacer(5)
		
		self.bRSlot = wx.BitmapButton(boxCont, wx.ID_ANY, self.images.pngContourroundedslot, size=BTNDIM)
		self.bRSlot.SetToolTip("Generate G Code for a rounded slot")
		szContours.Add(self.bRSlot)
		self.Bind(wx.EVT_BUTTON, self.bRSlotPressed, self.bRSlot)
		
		szContours.AddSpacer(10)

		bsizer.Add(szContours, 0, wx.ALL, 5)
		bsizer.AddSpacer(10)
		boxCont.SetSizer(bsizer)
		msizer.Add(boxCont, weightSingle, wx.EXPAND|wx.ALL, 10)

		
		boxDrills = wx.StaticBox(self, wx.ID_ANY, " Drills ")
		topBorder = boxDrills.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder)
		
		szDrills = wx.BoxSizer(wx.HORIZONTAL)
		
		szDrills.AddSpacer(10)
		
		self.bDrillRect = wx.BitmapButton(boxDrills, wx.ID_ANY, self.images.pngDrillrectangle, size=BTNDIM)
		self.bDrillRect.SetToolTip("Generate G Code for a rectangular drill pattern")
		szDrills.Add(self.bDrillRect)
		self.Bind(wx.EVT_BUTTON, self.bDrillRectPressed, self.bDrillRect)
		szDrills.AddSpacer(5)
		
		self.bDrillCirc = wx.BitmapButton(boxDrills, wx.ID_ANY, self.images.pngDrillcircle, size=BTNDIM)
		self.bDrillCirc.SetToolTip("Generate G Code for a circular drill pattern")
		szDrills.Add(self.bDrillCirc)
		self.Bind(wx.EVT_BUTTON, self.bDrillCircPressed, self.bDrillCirc)
		szDrills.AddSpacer(5)
		
		self.bDrillLine = wx.BitmapButton(boxDrills, wx.ID_ANY, self.images.pngDrilllinear, size=BTNDIM)
		self.bDrillLine.SetToolTip("Generate G Code for a linear drill pattern")
		szDrills.Add(self.bDrillLine)
		self.Bind(wx.EVT_BUTTON, self.bDrillLinePressed, self.bDrillLine)

		bsizer.Add(szDrills, 0, wx.ALL, 5)
		bsizer.AddSpacer(10)
		boxDrills.SetSizer(bsizer)
		msizer.Add(boxDrills, weightSingle, wx.EXPAND|wx.ALL, 10)

		boxCarve = wx.StaticBox(self, wx.ID_ANY, " Carvings ")
		topBorder = boxCarve.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder)
		
		szCarving = wx.BoxSizer(wx.HORIZONTAL)
		
		szCarving.AddSpacer(10)
		
		self.bGrid = wx.BitmapButton(boxCarve, wx.ID_ANY, self.images.pngCarvegrid, size=BTNDIM)
		self.bGrid.SetToolTip("Generate G Code for a grid pattern")
		szCarving.Add(self.bGrid)
		self.Bind(wx.EVT_BUTTON, self.bGridPressed, self.bGrid)
		szCarving.AddSpacer(5)
		
		self.bDiamonds = wx.BitmapButton(boxCarve, wx.ID_ANY, self.images.pngCarvediamond, size=BTNDIM)
		self.bDiamonds.SetToolTip("Generate G Code for a diamond pattern")
		szCarving.Add(self.bDiamonds)
		self.Bind(wx.EVT_BUTTON, self.bDiamondPressed, self.bDiamonds)
		szCarving.AddSpacer(5)

		self.bHatch = wx.BitmapButton(boxCarve, wx.ID_ANY, self.images.pngCarvehatch, size=BTNDIM)
		self.bHatch.SetToolTip("Generate G Code for a cross-hatch pattern")
		szCarving.Add(self.bHatch)
		self.Bind(wx.EVT_BUTTON, self.bHatchPressed, self.bHatch)

		bsizer.Add(szCarving, 0, wx.ALL, 5)
		bsizer.AddSpacer(10)
		boxCarve.SetSizer(bsizer)
		msizer.Add(boxCarve, weightSingle, wx.EXPAND|wx.ALL, 10)
		

		boxObject = wx.StaticBox(self, wx.ID_ANY, " Objects ")
		topBorder = boxObject.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder)
		
		szObjects = wx.BoxSizer(wx.HORIZONTAL)
		
		szObjects.AddSpacer(10)
		
		self.bTichy = wx.BitmapButton(boxObject, wx.ID_ANY, self.images.pngTichy, size=BTNDIM)
		self.bTichy.SetToolTip("Generate G Code for tichy windows and doors")
		szObjects.Add(self.bTichy)
		self.Bind(wx.EVT_BUTTON, self.bTichyPressed, self.bTichy)
		
		szObjects.AddSpacer(5)
		
		self.bBox = wx.BitmapButton(boxObject, wx.ID_ANY, self.images.pngBox, size=BTNDIM)
		self.bBox.SetToolTip("Generate G Code for a tabbed box")
		szObjects.Add(self.bBox)
		self.Bind(wx.EVT_BUTTON, self.bBoxPressed, self.bBox)
		
		szObjects.AddSpacer(5)
		
		self.bStringer = wx.BitmapButton(boxObject, wx.ID_ANY, self.images.pngStringer, size=BTNDIM)
		self.bStringer.SetToolTip("Generate G Code for a stair stringers")
		szObjects.Add(self.bStringer)
		self.Bind(wx.EVT_BUTTON, self.bStringerPressed, self.bStringer)
		
		bsizer.Add(szObjects, 0, wx.ALL, 5)
		bsizer.AddSpacer(10)
		boxObject.SetSizer(bsizer)
		msizer.Add(boxObject, weightSingle, wx.EXPAND|wx.ALL, 10)
		
		sizer.Add(msizer)
		
		sizer.AddSpacer(10)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def createMaterialsMenu(self):		
		self.menuMaterials = wx.Menu()
		mx = 0
		for m in self.materialList:
			mid = MENU_MATERIALS_BASE + mx
			self.menuMaterials.Append(mid, m, "Material: {}".format(m), wx.ITEM_RADIO)
			if m == self.settings.material:
				self.menuMaterials.Check(mid, True)
			self.Bind(wx.EVT_MENU, self.onMenuMaterials, id=mid)
			mx += 1
			
		self.menuMaterials.AppendSeparator()
		
		self.menuMaterials.Append(MENU_MATERIALS_MANAGE, "Manage materials")
		self.Bind(wx.EVT_MENU, self.onMenuManageMaterials, id=MENU_MATERIALS_MANAGE)
		
	def rebuildMaterialsMenu(self):
		menu = self.menuMaterials
		mid = MENU_MATERIALS_BASE
		while self.menuBar.FindItemById(mid):
			menu.Remove(mid)
			mid += 1
			
		self.materialList = self.materials.getMaterials()
		mx = 0
		for m in self.materialList:
			mid = MENU_MATERIALS_BASE + mx
			self.menuMaterials.InsertRadioItem(mx, mid, m, "Material: {}".format(m))
			if m == self.settings.material:
				self.menuMaterials.Check(mid, True)
			self.Bind(wx.EVT_MENU, self.onMenuMaterials, id=mid)
			mx += 1
		
	def createToolsMenu(self):
		self.menuTools = wx.Menu()
		tx = 0
		for t in self.toolList:
			tinfo = self.tools.getTool(t)
			tid = MENU_TOOLS_BASE + tx
			self.menuTools.Append(tid, t, "{}".format(tinfo["name"]), wx.ITEM_RADIO)
			if t == self.settings.tool:
				self.menuTools.Check(tid, True)
			self.Bind(wx.EVT_MENU, self.onMenuTools, id=tid)
			tx += 1
			
		self.menuTools.AppendSeparator()
		
		self.menuTools.Append(MENU_TOOLS_MANAGE, "Manage tools")
		self.Bind(wx.EVT_MENU, self.onMenuManageTools, id=MENU_TOOLS_MANAGE)
			
	def rebuildToolsMenu(self):
		menu = self.menuTools
		mid = MENU_TOOLS_BASE
		while self.menuBar.FindItemById(mid):
			menu.Remove(mid)
			mid += 1
			
		self.toolList = self.tools.getTools()
		tx = 0
		for t in self.toolList:
			mid = MENU_TOOLS_BASE + tx
			self.menuTools.InsertRadioItem(tx, mid, t, "Tool: {}".format(t))
			if t == self.settings.tool:
				self.menuTools.Check(mid, True)
			self.Bind(wx.EVT_MENU, self.onMenuTools, id=mid)
			tx += 1
		
		
	def onMenuFileView(self, _):
		dlg = wx.FileDialog(
			self, message="Choose a file",
			defaultDir=self.settings.lastloaddir,
			defaultFile="",
			wildcard=wildcard,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return 

		path = dlg.GetPath()
		dlg.Destroy()
		
		pdir = os.path.split(path)[0]
		if pdir != self.settings.lastloaddir:
			self.settings.lastloaddir = pdir
			self.settings.setModified()
		
		with open(path, "r") as fp:
			glines = fp.readlines()

		vwrDlg = NCViewer(self, path, self.settings)
		vwrDlg.loadGCode(glines)
		vwrDlg.ShowModal()
		vwrDlg.Destroy()	
		
	def onMenuFileMerge(self, _):
		dlg = FileMergeDialog(self)
		dlg.ShowModal()
		dlg.Destroy()
		
	def onMenuOptsAnnotate(self, _):
		self.settings.annotate = self.menuOpts.IsChecked(MENU_OPTS_ANNOTATE)
		self.settings.setModified()
		
	def onMenuOptsAddSpeed(self, _):
		self.settings.addspeed = self.menuOpts.IsChecked(MENU_OPTS_ADD_SPEED)
		self.settings.setModified()
		
	def onMenuOptsMetric(self, _):
		self.settings.metric = self.menuOpts.IsChecked(MENU_OPTS_METRIC)
		self.settings.setModified()
		
	def onMenuOptsSettings(self, _):
		dlg = SettingsDlg(self)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			result = dlg.getResults()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return 
		
		self.settings.safez = result["safez"]
		self.settings.totaldepth = result["totaldepth"]
		self.settings.decimals = result["decimals"]
		self.settings.setModified()
		
	def onMenuMaterials(self, evt):
		self.settings.material = self.menuMaterials.GetLabel(evt.GetId())
		self.settings.setModified()
		self.speedInfo = self.tools.getToolSpeeds(self.settings.tool, self.settings.material, self.materials)
		
	def onMenuManageMaterials(self, evt):
		if self.materials.manage(self):
			self.rebuildMaterialsMenu()
			self.tools.pruneMaterials(self.materials.getMaterials())
			if self.settings.material not in self.materialList:
				self.settings.material = self.materialList[0]
			self.settings.setModified()

		self.settings.setModified()
		self.speedInfo = self.tools.getToolSpeeds(self.settings.tool, self.settings.material, self.materials)
		
	def onMenuTools(self, evt):
		self.settings.tool = self.menuTools.GetLabel(evt.GetId())
		self.settings.setModified()
		self.toolInfo = self.tools.getTool(self.settings.tool)
		self.speedInfo = self.tools.getToolSpeeds(self.settings.tool, self.settings.material, self.materials)
		
	def onMenuManageTools(self, evt):
		if self.tools.manage(self, self.materials.getMaterials()):
			self.rebuildToolsMenu()
			if self.settings.tool not in self.toolList:
				self.settings.tool = self.toolList[0]
			self.settings.setModified()

		self.settings.setModified()
		self.toolInfo = self.tools.getTool(self.settings.tool)
		self.speedInfo = self.tools.getToolSpeeds(self.settings.tool, self.settings.material, self.materials)
		
	def onClose(self, _):
		if not self.closeIfOkay(self.wline):
			return
		self.wline = None
			
		if not self.closeIfOkay(self.wrect):
			return
		self.wrect = None
			
		if not self.closeIfOkay(self.wcirc):
			return
		self.wcirc = None
			
		if not self.closeIfOkay(self.warc):
			return
		self.warc = None
			
		if not self.closeIfOkay(self.wpolygon):
			return
		self.wpolygon = None
			
		if not self.closeIfOkay(self.wpolyline):
			return
		self.wpolyline = None
			
		if not self.closeIfOkay(self.wrslot):
			return
		self.wrslot = None

		if not self.closeIfOkay(self.wdrillrect):
			return
		self.wdrillrect = None
			
		if not self.closeIfOkay(self.wdrillcirc):
			return
		self.wdrillcirc = None
			
		if not self.closeIfOkay(self.wdrillline):
			return
		self.wdrillline = None
			
		if not self.closeIfOkay(self.wgrid):
			return
		self.wgrid = None
			
		if not self.closeIfOkay(self.wdiamonds):
			return
		self.wdiamonds = None
			
		if not self.closeIfOkay(self.whatch):
			return
		self.whatch = None
			
		if not self.closeIfOkay(self.wtichy):
			return
		self.wtichy = None
			
		if not self.closeIfOkay(self.wbox):
			return
		self.wbox = None

		self.settings.save()
			
		self.Destroy()
	
	def closeIfOkay(self, w):
		if w is None:
			return True
		if w.okToClose():
			w.Destroy()
			return True
		
		return False
		
	def bLinePressed(self, _):
		if self.wline:
			self.wline.SetFocus()
		else:
			self.wline = line.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wline.Bind(wx.EVT_CLOSE, self.lineClose)
			self.wline.Show()
		
	def lineClose(self, _):
		if self.closeIfOkay(self.wline):
			self.wline = None
		
	def bRectPressed(self, _):
		if self.wrect:
			self.wrect.SetFocus()
		else:
			self.wrect = rect.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wrect.Bind(wx.EVT_CLOSE, self.rectClose)
			self.wrect.Show()
		
	def rectClose(self, _):
		if self.closeIfOkay(self.wrect):
			self.wrect = None
		
	def bCircPressed(self, _):
		if self.wcirc:
			self.wcirc.SetFocus()
		else:
			self.wcirc = circ.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wcirc.Bind(wx.EVT_CLOSE, self.circClose)
			self.wcirc.Show()
		
	def circClose(self, _):
		if self.closeIfOkay(self.wcirc):
			self.wcirc = None
		
	def bArcPressed(self, _):
		if self.warc:
			self.warc.SetFocus()
		else:
			self.warc = arc.MainFrame(self.toolInfo, self.speedInfo, self)
			self.warc.Bind(wx.EVT_CLOSE, self.arcClose)
			self.warc.Show()
		
	def arcClose(self, _):
		if self.closeIfOkay(self.warc):
			self.warc = None
		
	def bPolygonPressed(self, _):
		if self.wpolygon:
			self.wpolygon.SetFocus()
		else:
			self.wpolygon = polygon.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wpolygon.Bind(wx.EVT_CLOSE, self.polygonClose)
			self.wpolygon.Show()
		
	def polygonClose(self, _):
		if self.closeIfOkay(self.wpolygon):
			self.wpolygon = None
		
	def bPolylinePressed(self, _):
		if self.wpolyline:
			self.wpolyline.SetFocus()
		else:
			self.wpolyline = polyline.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wpolyline.Bind(wx.EVT_CLOSE, self.polylineClose)
			self.wpolyline.Show()
		
	def polylineClose(self, _):
		if self.closeIfOkay(self.wpolyline):
			self.wpolyline = None
		
	def bRSlotPressed(self, _):
		if self.wrslot:
			self.wrslot.SetFocus()
		else:
			self.wrslot = rslot.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wrslot.Bind(wx.EVT_CLOSE, self.rslotClose)
			self.wrslot.Show()
		
	def rslotClose(self, _):
		if self.closeIfOkay(self.wrslot):
			self.wrslot = None
		
	def bDrillRectPressed(self, _):
		if self.wdrillrect:
			self.wdrillrect.SetFocus()
		else:
			self.wdrillrect = drillrect.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wdrillrect.Bind(wx.EVT_CLOSE, self.drillrectClose)
			self.wdrillrect.Show()
		
	def drillrectClose(self, _):
		if self.closeIfOkay(self.wdrillrect):
			self.wdrillrect = None
		
	def bDrillCircPressed(self, _):
		if self.wdrillcirc:
			self.wdrillcirc.SetFocus()
		else:
			self.wdrillcirc = drillcirc.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wdrillcirc.Bind(wx.EVT_CLOSE, self.drillcircClose)
			self.wdrillcirc.Show()
		
	def drillcircClose(self, _):
		if self.closeIfOkay(self.wdrillcirc):
			self.wdrillcirc = None
		
	def bDrillLinePressed(self, _):
		if self.wdrillline:
			self.wdrillline.SetFocus()
		else:
			self.wdrillline = drillline.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wdrillline.Bind(wx.EVT_CLOSE, self.drilllineClose)
			self.wdrillline.Show()
		
	def drilllineClose(self, _):
		if self.closeIfOkay(self.wdrillline):
			self.wdrillline = None
		
	def bGridPressed(self, _):
		if self.wgrid:
			self.wgrid.SetFocus()
		else:
			self.wgrid = grid.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wgrid.Bind(wx.EVT_CLOSE, self.gridClose)
			self.wgrid.Show()
		
	def gridClose(self, _):
		if self.closeIfOkay(self.wgrid):
			self.wgrid = None
		
	def bDiamondPressed(self, _):
		if self.wdiamonds:
			self.wdiamonds.SetFocus()
		else:
			self.wdiamonds = diamonds.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wdiamonds.Bind(wx.EVT_CLOSE, self.diamondsClose)
			self.wdiamonds.Show()
		
	def diamondsClose(self, _):
		if self.closeIfOkay(self.wdiamonds):
			self.wdiamonds = None
		
	def bHatchPressed(self, _):
		if self.whatch:
			self.whatch.SetFocus()
		else:
			self.whatch = hatch.MainFrame(self.toolInfo, self.speedInfo, self)
			self.whatch.Bind(wx.EVT_CLOSE, self.hatchClose)
			self.whatch.Show()
		
	def hatchClose(self, _):
		if self.closeIfOkay(self.whatch):
			self.whatch = None
		
	def bTichyPressed(self, _):
		if self.wtichy:
			self.wtichy.SetFocus()
		else:
			self.wtichy = tichy.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wtichy.Bind(wx.EVT_CLOSE, self.tichyClose)
			self.wtichy.Show()
		
	def tichyClose(self, _):
		if self.closeIfOkay(self.wtichy):
			self.wtichy = None
		
	def bBoxPressed(self, _):
		if self.wbox:
			self.wbox.SetFocus()
		else:
			self.wbox = tabbedbox.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wbox.Bind(wx.EVT_CLOSE, self.boxClose)
			self.wbox.Show()
		
	def boxClose(self, _):
		if self.closeIfOkay(self.wbox):
			self.wbox = None
		
	def bStringerPressed(self, _):
		if self.wstringer:
			self.wstringer.SetFocus()
		else:
			self.wstringer = stringer.MainFrame(self.toolInfo, self.speedInfo, self)
			self.wstringer.Bind(wx.EVT_CLOSE, self.stringerClose)
			self.wstringer.Show()
		
	def stringerClose(self, _):
		if self.closeIfOkay(self.wstringer):
			self.wstringer = None
			
class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		self.SetTopWindow(self.frame)
		return True

app = App(False)
app.MainLoop()

	
