'''
Created on Jan 31, 2020

@author: jeffb
'''
from validators import verifyExitNoSave, verifyExitNoGenerate, verifyStaleGCodeSave
from settings import BTNDIM
import wx
import json
import os

wildcard = "JSON Code (*.json)|*.json|"	 \
		   "All files (*.*)|*.*"

metricspinvals = {
	"extradepth": [ 0.0, 5.0, 0.1, 1],
	"feedxyg0":   [ 1, 10000, 1, 1 ],
	"feedxyg1":   [ 1, 10000, 1, 1 ],
	"feedzg0":    [ 1, 10000, 1, 1 ],
	"feedzg1":    [ 1, 10000, 1, 1 ],
	"holediam":   [ 1, 30, 0.1, 1 ],
	"passdepth":  [ 0.1, 5.0, 0.1, 1 ],
	"rise":       [ 0.1, 10.0, 0.1, 1 ],
	"run":        [ 0.1, 10.0, 0.1, 1 ],
	"safez":      [ 0.1, 5.0, 0.1, 1 ],
	"spacing":    [ 0.1, 20, 0.1, 1 ],
	"tooldiam":   [ 0.001, 8, 0.001, 3 ],
	"totaldepth": [ 0.1, 8.0, 0.1, 1 ],
}

imperialspinvals = {
	"extradepth": [ 0.0, 0.5, 0.01, 2],
	"feedxyg0":   [ 1, 10000, 1, 1 ],
	"feedxyg1":   [ 1, 10000, 1, 1 ],
	"feedzg0":    [ 1, 10000, 1, 1 ],
	"feedzg1":    [ 1, 10000, 1, 1 ],
	"holediam":   [ 0.01, 1, 0.01, 2 ],
	"passdepth":  [ 0.01, 0.5, 0.01, 2 ],
	"rise":       [ 0.01, 0.5, 0.01, 2 ],
	"run":        [ 0.01, 0.5, 0.01, 2 ],
	"safez":      [ 0.01, 0.5, 0.01, 2 ],
	"spacing":    [ 0.01, 1.0, 0.01, 2 ],
	"tooldiam":   [ 0.001, 8, 0.001, 3 ],
	"totaldepth": [ 0.01, 0.5, 0.01, 2 ],
}

spinvals = {
	"angle":      [ 0, 359.9, 0.1, 1 ],
	"holecount":  [ 1, 50, 1, 1 ],
	"segments":   [ 1, 50, 1, 1 ],
	"sidecount":  [ 3, 50, 1, 1 ],
	"steps":      [ 3, 50, 1, 1 ],
	"tracks":     [ 1, 50, 1, 1 ],
}

class WidgetProxy:
	def __init__(self):
		self.svalue = ""
		
	def SetValue(self, v):
		self.svalue = v
		
	def GetValue(self):
		return self.svalue


class CNCObject:
	def __init__(self, parent, objectType):
		self.parent = parent
		self.objectType = objectType
		self.settings = parent.settings
		self.images = self.parent.images
		self.widgets = {}
		
	def buttons(self):
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
		
		bsz.AddSpacer(60)
		
		self.bSaveData = wx.BitmapButton(self, wx.ID_ANY, self.images.pngTojson, size=BTNDIM)
		self.bSaveData.SetToolTip("Export values to file")
		bsz.Add(self.bSaveData)
		self.Bind(wx.EVT_BUTTON, self.bSaveDataPressed, self.bSaveData)
		
		bsz.AddSpacer(20)
		
		self.bLoadData = wx.BitmapButton(self, wx.ID_ANY, self.images.pngFromjson, size=BTNDIM)
		self.bLoadData.SetToolTip("Import values from file")
		bsz.Add(self.bLoadData)
		self.Bind(wx.EVT_BUTTON, self.bLoadDataPressed, self.bLoadData)
		
		return bsz
	
	def getSpinValues(self, metric, fname):
		try:
			return spinvals[fname]
		except KeyError:
			pass
		
		if metric:
			vals = metricspinvals
		else:
			vals = imperialspinvals
			
		try:
			return vals[fname]
		except KeyError:
			print("unknown field name: (%s)" % fname)
			return [ 0, 1, 0.1, 1 ]
		
	def addWidget(self, wdg, name):
		self.widgets[name] = wdg

	def bSaveDataPressed(self, _):
		dlg = wx.FileDialog(self, message="Save raw data as ...", defaultDir=self.settings.lastjsondir,
			defaultFile="", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return False
		
		path = dlg.GetPath()
		dlg.Destroy()
		pdir = os.path.split(path)[0]
		if pdir != self.settings.lastjsondir:
			self.settings.lastjsondir = pdir
			self.settings.setModified()
			
		wvals = {}
		for w in self.widgets:
			wvals[w] = self.widgets[w].GetValue() 
			
		j = {self.objectType: wvals} 
			
		try:
			with open(path, 'w') as f:
				json.dump(j, f)
		except IOError:
			dlg = wx.MessageDialog(self.parent, "Unable to open (%s) for writing" % path,
					'I/O Error', wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
		
	def bLoadDataPressed(self, _):
		dlg = wx.FileDialog(
			self, message="Load raw data from ...",
			defaultDir=self.settings.lastjsondir,
			defaultFile="",
			wildcard=wildcard,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return 

		path = dlg.GetPath()
		dlg.Destroy()
		
		pdir = os.path.split(path)[0]
		if pdir != self.settings.lastjsondir:
			self.settings.lastjsondir = pdir
			self.settings.setModified()
		
		with open(path, "r") as fp:
			try:
				j = json.load(fp)
			except IOError:
				dlg = wx.MessageDialog(self.parent, "Unable to open (%s) for reading" % path,
						'I/O Error', wx.OK | wx.ICON_INFORMATION)
				dlg.ShowModal()
				dlg.Destroy()
				return

		kcount = 0			   
		for jk in j.keys():
			if kcount == 0:
				jkey = jk
			kcount += 1

		if kcount != 1:
			dlg = wx.MessageDialog(self.parent, "Unable to interpret data in (%s)" % path,
					'Unexpected format', wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return 

		if jkey != self.objectType:
			dlg = wx.MessageDialog(self.parent, "File %s\n\nWritten from object type: %s\nExpecting type: %s" % (path, jkey, self.objectType),
					'Incorrect Object Type', wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return 
		
		wvals = j[jkey]	   
		
		for w in self.widgets:
			if w in wvals:
				self.widgets[w].SetValue(wvals[w])
				
		self.checkEnable()
		self.setState(True, False)
		
	def checkEnable(self):
		f = self.cbAddSpeed.IsChecked()
		self.scFeedXYG0.Enable(f)
		self.scFeedXYG1.Enable(f)
		self.scFeedZG0.Enable(f)
		self.scFeedZG1.Enable(f)
		
	def setChosen(self, ids, label):
		for i in ids:
			if i.GetLabel() == label:
				i.SetValue(True)
				break
		
	def getChosen(self, ids):
		for i in ids:
			if i.GetValue():
				return i.GetLabel()
		return None
	
	def setName(self, name):
		self.name = name

	def setTitleFlag(self):
		title = self.titleText
		if self.modified:
			title += " (modified)"
			
		if self.unsaved:
			title += " (unsaved)"
		self.parent.SetTitle(title)
		
		
		
	def resolveToolDiameter(self, toolInfo):	
		tm = toolInfo["metric"]
		if tm == self.settings.metric:
			return toolInfo["diameter"]
		
		if tm:
			tdf = float(toolInfo["diameter"]) / 25.4
			msg = "Tool is metric, but object is imperial.\n" +\
				("Converted tool diameter of %6.3f mm to %6.3f in" % (toolInfo["diameter"], tdf))
		else:
			tdf = toolInfo["diameter"] * 25.4
			msg = "Tool is imperial, but object is metric.\n" +\
				("Converted tool diameter of %6.3f in to %6.3f mm" % (toolInfo["diameter"], tdf))
			
		dlg = wx.MessageDialog(self,
			msg,
			'Tool Diameter Converted',
			wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
		
		return tdf
		
		
		
		
	def preamble(self, settings, title, tooldiam, toolname, metric): #, toolinfo, feedZG0, safeZ):
		code = []
		if self.settings.annotate:
			code.append("({})".format(title))
			if toolname is None:
				code.append("(Tool diameter %7.3f %s)" % (tooldiam, "mm" if settings.metric else "in"))
			else:
				code.append("(Tool %s - diameter %7.3f %s)" % (
					toolname, tooldiam, "mm" if settings.metric else "in"))

		code.append("G90")
		if metric:
			code.append("G21")
		else:
			code.append("G20")
			
		return code
	
	def onChange(self, _):
		self.setState(True, False)

	def okToClose(self):
		if self.modified:
			rc = verifyExitNoGenerate(self)
			if not rc:
				return False
		elif self.unsaved:
			rc = verifyExitNoSave(self)
			if not rc:
				return False
		return True
			
	def onClose(self, _):
		if self.okToClose():
			self.Destroy()
			
	def setState(self, mFlag=True, sFlag=False):
		if mFlag is not None:
			self.modified = mFlag
		self.unsaved = sFlag
		self.setTitleFlag()
	
	def bSavePressed(self, _):
		if self.modified:
			rc = verifyStaleGCodeSave(self)
			if not rc:
				return 
			
		if self.gcl.save(self.settings):
			self.setState(None, False)

	def speedTerm(self, flag, speed):
		if not flag:
			return ""
		
		return " F%d" % speed
	
	def IJTerm(self, label, val):
		if val == 0.0:
			return ""
		else:
			return " " + label + self.fmt % val

	def bVisualizePressed(self, _):
		self.gcl.visualize(title=self.viewTitle)
