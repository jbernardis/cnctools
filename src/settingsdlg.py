import json
import wx
from settings import BTNDIM


LABELSIZE = (150, -1)
SPINSIZE = (100, -1)

class SettingsDlg(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.modified = False
		self.parent = parent
		self.settings = self.parent.settings
		self.images = self.parent.images
		
		self.SetTitle("Edit Settings")
		
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
	
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		

		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=self.settings.totaldepth, min=0.0, max=10.0, inc=0.1, size=SPINSIZE)
		sc.SetValue(self.settings.totaldepth)
		sc.SetDigits(2)
		self.scTotalDepth = sc

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Depth of cut/material: ", size=LABELSIZE))		
		hsz.Add(self.scTotalDepth, 0)
		vsizer.Add(hsz)

		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scTotalDepth)
		self.Bind(wx.EVT_TEXT, self.OnText, self.scTotalDepth)
		
		vsizer.AddSpacer(8)

		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=self.settings.safez, min=0.0, max=5.0, inc=0.1, size=SPINSIZE)
		sc.SetValue(self.settings.safez)
		sc.SetDigits(2)
		self.scSafeZ = sc

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Safe Z height: ", size=LABELSIZE))		
		hsz.Add(self.scSafeZ, 0)
		vsizer.Add(hsz)

		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scSafeZ)
		self.Bind(wx.EVT_TEXT, self.OnText, self.scSafeZ)
		
		vsizer.AddSpacer(8)

		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=self.settings.decimals, size=SPINSIZE)
		sc.SetRange(0, 5)
		sc.SetValue(self.settings.decimals)
		self.scDecimals = sc

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Decimal Places: ", size=LABELSIZE))		
		hsz.Add(self.scDecimals, 0)
		vsizer.Add(hsz)
		vsizer.AddSpacer(3)

		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scDecimals)
		self.Bind(wx.EVT_TEXT, self.OnText, self.scDecimals)
		
		vsizer.AddSpacer(20)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.bOK = wx.BitmapButton(self, wx.ID_ANY, self.images.pngOk, size=BTNDIM)
		self.bOK.SetToolTip("Save changes and exit dialog")
		btnSizer.Add(self.bOK)
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		
		btnSizer.AddSpacer(10)

		self.bCancel = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCancel, size=BTNDIM)
		self.bCancel.SetToolTip("Discard changes and exit dialog")
		btnSizer.Add(self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		
		vsizer.AddSpacer(10)
		vsizer.Add(btnSizer, 1, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)	   
		hsizer.AddSpacer(20)

		self.SetSizer(hsizer)
		self.Layout()
		self.Fit();

	def OnSpin(self, _):
		self.modified = True

	def OnText(self, _):
		self.modified = True
		
	def bOKPressed(self, _):
		if self.modified:
			self.EndModal(wx.ID_OK)
		else:
			self.EndModal(wx.ID_EXIT)
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Changes have not been saved\nPress yes to exit anyway',
		                               'Unsaved Changes',
		                               wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			self.EndModal(wx.ID_CANCEL)
		else:
			self.EndModal(wx.ID_EXIT)
			
	def getResults(self):
		properties = {}
		properties["decimals"] = self.scDecimals.GetValue()
		properties["totaldepth"] = self.scTotalDepth.GetValue()
		properties["safez"] = self.scSafeZ.GetValue()
		return properties
