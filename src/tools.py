import json
import wx
from settings import BTNDIM
from materials import ManageMaterialsDlg
LABELSIZE = (150, -1)
SPINSIZE = (100, -1)
TEXTSIZE = (200, -1)

class EditToolDlg(wx.Dialog):
	def __init__(self, parent, tname, properties, mlist):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.modified = False
		self.parent = parent
		self.tname = tname
		self.properties = properties.copy()
		self.mlist = mlist
		
		self.settings = self.parent.settings
		self.images = self.parent.images
		
		self.SetTitle("Edit tool '%s' properties" % tname)
		
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
	
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)

		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=self.properties["diameter"], min=0.1, max=5.0, inc=0.1, size=SPINSIZE)
		sc.SetValue(self.properties["diameter"])
		sc.SetDigits(2)
		self.scDiam = sc

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Diameter: ", size=LABELSIZE))		
		hsz.Add(self.scDiam, 0)
		vsizer.Add(hsz)

		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scDiam)
		self.Bind(wx.EVT_TEXT, self.OnText, self.scDiam)

		vsizer.AddSpacer(8)

		tc = wx.TextCtrl(self, wx.ID_ANY, self.properties["name"], size=TEXTSIZE)
		self.tcDesc = tc

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Description: ", size=LABELSIZE))		
		hsz.Add(self.tcDesc, 0)
		vsizer.Add(hsz)
		
		self.Bind(wx.EVT_TEXT, self.OnText, self.tcDesc)

		vsizer.AddSpacer(8)

		tc = wx.TextCtrl(self, wx.ID_ANY, self.materialsString(), style=wx.TE_READONLY, size=TEXTSIZE)
		self.tcOverrides = tc
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Material Overrides:: ", size=LABELSIZE))		
		hsz.Add(self.tcOverrides, 0)
		
		hsz.AddSpacer(5)
		
		sz = tc.GetSize()
		sz[0] = BTNDIM[0]
		b = wx.Button(self, wx.ID_ANY, "...", size=sz)
		b.SetToolTip("Edit material overrides")
		self.bOverrides = b
		hsz.Add(b)
		
		self.Bind(wx.EVT_BUTTON, self.onBOverrides, self.bOverrides)
		
		vsizer.Add(hsz)
		
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
		
	def materialsString(self):
		return ", ".join(self.properties["speeds"].keys())

	def OnSpin(self, _):
		self.modified = True

	def OnText(self, _):
		self.modified = True
		
	def onBOverrides(self, _):
		t = ToolMaterials(self.properties["speeds"], self.tname, self.mlist)
		newOverrides = t.manage(self)
		if newOverrides is not None:
			self.properties["speeds"] = newOverrides
			self.tcOverrides.SetValue(self.materialsString())
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
		properties["diameter"] = self.scDiam.GetValue()
		properties["name"] = self.tcDesc.GetValue()
		properties["speeds"] = self.properties["speeds"]

		return properties

class ToolsList(wx.ListCtrl):
	def __init__(self, parent, tools):
		self.parent = parent
		self.tools = tools
		self.toolnames = sorted(list(self.tools.json.keys()))
		
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(680, 300),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)

		self.InsertColumn(0, "Tool Name")
		self.InsertColumn(1, "Description")
		self.InsertColumn(2, "Diameter")
		self.InsertColumn(3, "Material Overrides")
		self.SetColumnWidth(0, 100)
		self.SetColumnWidth(1, 200)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(3, 300)

		self.SetItemCount(len(self.toolnames))

		self.attr2 = wx.ItemAttr()
		self.attr2.SetBackgroundColour("light blue")
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)
		
	def initialize(self):
		if len(self.toolnames) > 0:
			self.setSelection(0)
		else:
			self.setSelection(None)		
			
	def setSelection(self, tx):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)
			
		self.parent.reportSelection(tx)
				
	def selectTool(self, t):
		if t in self.toolnames:
			tx = self.toolnames.index(t)
			self.setSelection(tx)
		else:
			self.setSelection(None)

	def OnItemSelected(self, event):
		self.setSelection(event.Index)

	def OnItemDeselected(self, evt):
		self.setSelection(None)

	def OnItemHint(self, evt):
		if self.GetFirstSelected() == -1:
			self.setSelection(None)

	def redrawList(self):
		self.SetItemCount(0)
		self.toolnames = sorted(list(self.tools.json.keys()))
		self.SetItemCount(len(self.toolnames))
		
	def getSelectedTool(self):
		if self.selected is None:
			return None
		
		return self.toolnames[self.selected]
		

	def OnGetItemText(self, item, col):
		if item < 0 or item >= len(self.toolnames):
			return None
		
		nm = self.toolnames[item]
		if col == 0:
			return nm
		elif col == 1:
			return "%s" % self.tools.json[nm]["name"]
		elif col == 2:
			return "%12.2f" % self.tools.json[nm]["diameter"]
		elif col == 3:
			return ", ".join(list(self.tools.json[nm]["speeds"].keys()))

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.attr2
		else:
			return None


class ToolMaterials:
	def __init__(self, json, tname, mlist):
		self.json = json.copy()
		self.tname = tname
		self.mlist = mlist
			
	def getMaterials(self):
		return sorted(self.json.keys())
			
	def getMaterial(self, mname):
		if mname not in self.json.keys():
			return None
		
		return self.json[mname]
	
	def getSpeedInfo(self, mname):
		if mname not in self.json:
			return None
		
		return self.json[mname]
	
	def manage(self, parent):
		dlg = ManageMaterialsDlg(parent, self, tname=self.tname, mlist=self.mlist)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc == wx.ID_OK:
			return self.json # changes made - menu needs to be rebuilt
		else: # no changes made  - no need to rebuild
			return None	

class ManageToolsDlg(wx.Dialog):
	def __init__(self, parent, tools, mlist):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Manage Tools")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.modified = False
		self.parent = parent
		self.tools = tools
		self.mlist = mlist
		self.settings = self.parent.settings
		self.images = self.parent.images
		self.toolnames = sorted(list(self.tools.json.keys()))
		
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
	
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		self.tl = ToolsList(self, self.tools)
		vsizer.Add(self.tl)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.bAdd = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAdd, size=BTNDIM)
		self.bAdd.SetToolTip("Add a new tool")
		btnSizer.Add(self.bAdd)
		self.Bind(wx.EVT_BUTTON, self.bAddPressed, self.bAdd)
		
		btnSizer.AddSpacer(10)

		self.bEdit = wx.BitmapButton(self, wx.ID_ANY, self.images.pngReplace, size=BTNDIM)
		self.bEdit.SetToolTip("Edit selected tooll properties")
		btnSizer.Add(self.bEdit)
		self.Bind(wx.EVT_BUTTON, self.bEditPressed, self.bEdit)
		self.bEdit.Enable(False)
		
		btnSizer.AddSpacer(10)

		self.bDel = wx.BitmapButton(self, wx.ID_ANY, self.images.pngDelete, size=BTNDIM)
		self.bDel.SetToolTip("Delete the selected tool")
		btnSizer.Add(self.bDel)
		self.Bind(wx.EVT_BUTTON, self.bDelPressed, self.bDel)
		self.bDel.Enable(False)
		
		btnSizer.AddSpacer(30)

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
		
		self.tl.initialize()
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit();
		
	def bAddPressed(self, _):
		dlg = wx.TextEntryDialog(
				self, 'Enter new tool name:',
				'Add New tool', '')

		rc = dlg.ShowModal()
		
		if rc == wx.ID_OK:
			nm = dlg.GetValue()	
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		if nm in self.toolnames:
			dlg = wx.MessageDialog(self, 'Name already in use',
					'Duplicate name', wx.OK | wx.ICON_ERROR )
			dlg.ShowModal()
			dlg.Destroy()
			return 
		

		self.tools.json[nm] = {
			"diameter": 1,
			"name": "NEW TOOL",
			"speeds": {}
		}
		
		self.toolnames = sorted(list(self.tools.json.keys()))
		self.tl.redrawList()
		self.tl.selectTool(nm)
		self.modified = True
		
	def bEditPressed(self, _):
		t = self.tl.getSelectedTool()
		if t is None:
			return 

		props = self.tools.json[t].copy()
		dlg = EditToolDlg(self, t, props, self.mlist)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			props = dlg.getResults()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return
		
		self.tools.json[t] = props
		self.tl.redrawList()
		self.tl.selectTool(t)

		self.modified = True
		
	def bDelPressed(self, _):
		m = self.tl.getSelectedTool()
		if m is None:
			return 

		dlg = wx.MessageDialog(self, "Delete tool '%s'?" % m,
		                              'Delete Confirmation',
		                              wx.YES_NO | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_YES:
			return

		del(self.tools.json[m])
		self.toolnames = sorted(list(self.tools.json.keys()))
		self.tl.redrawList()
		self.tl.selectTool(None)
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
	
	def reportSelection(self, sx):
		self.bEdit.Enable(sx is not None)
		self.bDel.Enable(sx is not None)

class Tools:
	def __init__(self, fn, settings):
		self.fn = fn
		self.settings = settings
		self.reload()
		
	def reload(self):
		with open(self.fn, "r") as fp:
			self.json = json.load(fp)
	
	def save(self):
		with open(self.fn, "w") as fp:
			json.dump(self.json, fp, sort_keys=True, indent=4)
			
	def getTools(self):
		return sorted(self.json.keys())
			
	def getTool(self, tname):
		if tname not in self.json.keys():
			return None
		
		return self.json[tname]
			
	def getToolSpeeds(self, tname, mname, materials):
		if tname not in self.json.keys():
			# unknown tool name - just return system default values
			rv = {
				"G0XY": self.settings.speedG0XY,
				"G1XY": self.settings.speedG1XY,
				"G0Z": self.settings.speedG0Z,
				"G1Z": self.settings.speedG1Z,
				"depthperpass": self.settings.depthperpass,
				"stepover": self.settings.stepover
			}
			return rv
		
		if mname not in self.json[tname]["speeds"].keys():
			# the tool dpes not give us an override for this material, so
			# return the material values
			return materials.getSpeedInfo(mname)
		
		# otherwise, return the tool override values
		return self.json[tname]["speeds"][mname]
	
	def manage(self, parent, mlist):
		dlg = ManageToolsDlg(parent, self, mlist)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc == wx.ID_OK:
			self.save()
			return True # changes made - menu needs to be rebuilt
		elif rc == wx.ID_CANCEL:
			self.reload()
			return False # changes discarded - menu does NOT need to be rebuilt
		else: # no changes made  - no need to rebuild
			return False
		
	def pruneMaterials(self, mlist):
		deletions = []
		for t in self.json.keys():
			for m in self.json[t]["speeds"].keys():
				if m not in mlist:
					deletions.append([t, m])
					
		for t, m in deletions:
			del(self.json[t]["speeds"][m])
					
		if len(deletions) > 0:
			self.save()
			return True
			
		return False
			


