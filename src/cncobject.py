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
		self.teFeedXYG0.Enable(f)
		self.teFeedXYG1.Enable(f)
		self.teFeedZG0.Enable(f)
		self.teFeedZG1.Enable(f)
		
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
		
	def preamble(self, measSys, tDiam, tInfo, safeZ):
		code = []
		if self.settings.annotate:
			code.append("({})".format(self.viewTitle))
			if tDiam == tInfo["diameter"]:
				code.append("(Tool %s - diameter %6.2f)" % (tInfo["name"], tInfo["diameter"]))
			else:
				code.append("(Tool diameter %6.2f)" % (tDiam))
			code.append("(preamble)")
		code.append("G90")
		if measSys == "Imperial":
			code.append("G20")
		else:
			code.append("G21")
		  
		code.append("G0 X0 Y0 Z%6.2f" % safeZ)  
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
		
		return " F" + self.fmt % speed
	
	def IJTerm(self, label, val):
		if val == 0.0:
			return ""
		else:
			return " " + label + self.fmt % val
	   
	def bVisualizePressed(self, _):
		self.gcl.visualize(title=self.viewTitle)
