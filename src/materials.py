import json
import wx
from settings import BTNDIM

class MaterialsList(wx.ListCtrl):
	def __init__(self, parent, materials):
		self.parent = parent
		self.materials = materials
		self.matnames = sorted(list(self.materials.json.keys()))
		
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(580, 300),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)

		self.InsertColumn(0, "Material")
		self.InsertColumn(1, "XY Normal")
		self.InsertColumn(2, "XY Rapid")
		self.InsertColumn(3, "Z Normal")
		self.InsertColumn(4, "Z Rapid")
		self.InsertColumn(5, "Depth/Pass")
		self.InsertColumn(6, "Stepover")
		self.SetColumnWidth(0, 100)
		self.SetColumnWidth(1, 80)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(3, 80)
		self.SetColumnWidth(4, 80)
		self.SetColumnWidth(5, 80)
		self.SetColumnWidth(6, 80)

		self.SetItemCount(len(self.matnames))

		self.attr2 = wx.ItemAttr()
		self.attr2.SetBackgroundColour("light blue")
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)
		
	def initialize(self):
		if len(self.matnames) > 0:
			self.setSelection(0)
		else:
			self.setSelection(None)		
			
	def setSelection(self, mx):
		self.selected = mx;
		if mx is not None:
			self.Select(mx)
			
		self.parent.reportSelection(mx)
				
	def selectMaterial(self, m):
		if m in self.matnames:
			mx = self.matnames.index(m)
			self.setSelection(mx)
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
		self.matnames = sorted(list(self.materials.json.keys()))
		self.SetItemCount(len(self.matnames))
		
	def getSelectedMaterial(self):
		if self.selected is None:
			return None
		
		return self.matnames[self.selected]
		

	def OnGetItemText(self, item, col):
		if item < 0 or item >= len(self.matnames):
			return None
		
		nm = self.matnames[item]
		if col == 0:
			return nm
		elif col == 1:
			return "%12d" % self.materials.json[nm]["G1XY"]
		elif col == 2:
			return "%12d" % self.materials.json[nm]["G0XY"]
		elif col == 3:
			return "%12d" % self.materials.json[nm]["G1Z"]
		elif col == 4:
			return "%12d" % self.materials.json[nm]["G0Z"]
		elif col == 5:
			return "%12.2f" % self.materials.json[nm]["depthperpass"]
		elif col == 6:
			return "%12.2f" % self.materials.json[nm]["stepover"]

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.attr2
		else:
			return None

LABELSIZE = (150, -1)
SPINSIZE = (100, -1)

class EditMaterialDlg(wx.Dialog):
	def __init__(self, parent, mname, properties):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.modified = False
		self.parent = parent
		self.nmame = mname
		self.properties = properties.copy()
		self.settings = self.parent.settings
		self.images = self.parent.images
		
		self.SetTitle("Edit Material '%s' properties" % mname)
		
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
	
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=self.properties["G1XY"], size=SPINSIZE)
		sc.SetRange(1,10000)
		sc.SetValue(self.properties["G1XY"])
		self.scXYspeed = sc

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "XY Normal Speed: ", size=LABELSIZE))		
		hsz.Add(self.scXYspeed, 0)
		vsizer.Add(hsz)
		vsizer.AddSpacer(3)

		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scXYspeed)
		self.Bind(wx.EVT_TEXT, self.OnText, self.scXYspeed)
		

		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=self.properties["G1Z"], size=SPINSIZE)
		sc.SetRange(1,10000)
		sc.SetValue(self.properties["G1Z"])
		self.scZspeed = sc

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Z Normal Speed: ", size=LABELSIZE))		
		hsz.Add(self.scZspeed, 0)
		vsizer.Add(hsz)
		vsizer.AddSpacer(3)

		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scZspeed)
		self.Bind(wx.EVT_TEXT, self.OnText, self.scZspeed)

		
		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=self.properties["G0XY"], size=SPINSIZE)
		sc.SetRange(1,10000)
		sc.SetValue(self.properties["G0XY"])
		self.scXYrapid = sc

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "XY Rapid Speed: ", size=LABELSIZE))		
		hsz.Add(self.scXYrapid, 0)
		vsizer.Add(hsz)
		vsizer.AddSpacer(3)

		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scXYrapid)
		self.Bind(wx.EVT_TEXT, self.OnText, self.scXYrapid)
		

		sc = wx.SpinCtrl(self, wx.ID_ANY, "", initial=self.properties["G0Z"], size=SPINSIZE)
		sc.SetRange(1,10000)
		sc.SetValue(self.properties["G0Z"])
		self.scZrapid = sc

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Z Rapid Speed: ", size=LABELSIZE))		
		hsz.Add(self.scZrapid, 0)
		vsizer.Add(hsz)

		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scZrapid)
		self.Bind(wx.EVT_TEXT, self.OnText, self.scZrapid)

		vsizer.AddSpacer(8)

		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=self.properties["depthperpass"], min=0.1, max=5.0, inc=0.1, size=SPINSIZE)
		sc.SetValue(self.properties["depthperpass"])
		sc.SetDigits(2)
		self.scDpp = sc

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Depth Per Pass: ", size=LABELSIZE))		
		hsz.Add(self.scDpp, 0)
		vsizer.Add(hsz)

		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scDpp)
		self.Bind(wx.EVT_TEXT, self.OnText, self.scDpp)

		vsizer.AddSpacer(8)

		sc = wx.SpinCtrlDouble(self, wx.ID_ANY, "", initial=self.properties["stepover"], min=0.1, max=1.0, inc=0.01, size=SPINSIZE)
		sc.SetValue(self.properties["stepover"])
		sc.SetDigits(2)
		self.scStepover = sc

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Stepover: ", size=LABELSIZE))		
		hsz.Add(self.scStepover, 0)
		vsizer.Add(hsz)

		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scStepover)
		self.Bind(wx.EVT_TEXT, self.OnText, self.scStepover)

		
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
		properties["G0XY"] = self.scXYrapid.GetValue()
		properties["G1XY"] = self.scXYspeed.GetValue()
		properties["G0Z"] = self.scZrapid.GetValue()
		properties["G1Z"] = self.scZspeed.GetValue()
		properties["depthperpass"] = self.scDpp.GetValue()
		properties["stepover"] = self.scStepover.GetValue()
		return properties

class ManageMaterialsDlg(wx.Dialog):
	def __init__(self, parent, materials, tname=None, mlist=None):
		if tname is None:
			title = "Manage Materials"
		else:
			title = "Manage Material Overrides for tool '%s'" % tname
			
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.modified = False
		self.parent = parent
		self.materials = materials
		self.settings = self.parent.settings
		self.images = self.parent.images
		self.matnames = sorted(list(self.materials.json.keys()))
		self.tname = tname
		self.mlist = mlist
		
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
	
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		self.ml = MaterialsList(self, self.materials)
		vsizer.Add(self.ml)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.bAdd = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAdd, size=BTNDIM)
		self.bAdd.SetToolTip("Add a new material")
		btnSizer.Add(self.bAdd)
		self.Bind(wx.EVT_BUTTON, self.bAddPressed, self.bAdd)
		
		btnSizer.AddSpacer(10)

		self.bEdit = wx.BitmapButton(self, wx.ID_ANY, self.images.pngReplace, size=BTNDIM)
		self.bEdit.SetToolTip("Edit selected material properties")
		btnSizer.Add(self.bEdit)
		self.Bind(wx.EVT_BUTTON, self.bEditPressed, self.bEdit)
		self.bEdit.Enable(False)
		
		btnSizer.AddSpacer(10)

		self.bDel = wx.BitmapButton(self, wx.ID_ANY, self.images.pngDelete, size=BTNDIM)
		self.bDel.SetToolTip("Delete the selected material")
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
		
		self.ml.initialize()
		
		if self.mlist is not None:
			self.checkAllMaterials()
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit();
		
	def bAddPressed(self, _):
		if self.mlist is None:
			dlg = wx.TextEntryDialog(
					self, 'Enter new material name:',
					'Add New Material', '')
	
			rc = dlg.ShowModal()
			
			if rc == wx.ID_OK:
				nm = dlg.GetValue()	
				
			dlg.Destroy()
			
			if rc != wx.ID_OK:
				return
			
			if nm in self.matnames:
				dlg = wx.MessageDialog(self, 'Name already in use',
						'Duplicate name', wx.OK | wx.ICON_ERROR )
				dlg.ShowModal()
				dlg.Destroy()
				return 
		else:
			mlist = [m for m in self.mlist if m not in self.matnames]
			
			dlg = wx.SingleChoiceDialog(
				self, 'Choose material to be overriden', 'Add new override',
				mlist,
				wx.CHOICEDLG_STYLE
				)

			rc = dlg.ShowModal()
			if rc == wx.ID_OK:
				nm = dlg.GetStringSelection()
	
			dlg.Destroy()

			if rc != wx.ID_OK:
				return
		
		self.materials.json[nm] = {
			"G0XY": self.settings.speedG0XY,
			"G0Z": self.settings.speedG0Z,
			"G1XY": self.settings.speedG1XY,
			"G1Z": self.settings.speedG1Z,
			"depthperpass": self.settings.depthperpass,
			"stepover": self.settings.stepover
		}
		self.matnames = sorted(list(self.materials.json.keys()))
		self.ml.redrawList()
		self.ml.selectMaterial(nm)
		self.modified = True
		
		if self.mlist is not None:
			self.checkAllMaterials()
		
	def bEditPressed(self, _):
		m = self.ml.getSelectedMaterial()
		if m is None:
			return 
		
		props = self.materials.json[m].copy()
		dlg = EditMaterialDlg(self, m, props)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			props = dlg.getResults()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return
		
		self.materials.json[m] = props
		self.ml.redrawList()
		self.ml.selectMaterial(m)
		
		self.modified = True
		
	def bDelPressed(self, _):
		m = self.ml.getSelectedMaterial()
		if m is None:
			return 
		
		dlg = wx.MessageDialog(self, "Delete material '%s'?" % m,
	                               'Delete Confirmation',
	                               wx.YES_NO | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_YES:
			return
	
		del(self.materials.json[m])
		self.matnames = sorted(list(self.materials.json.keys()))
		self.ml.redrawList()
		self.ml.selectMaterial(None)
		self.modified = True
		
		if self.mlist is not None:
			self.checkAllMaterials()
			
	def checkAllMaterials(self):
		mlist = [m for m in self.mlist if m not in self.matnames]
		self.bAdd.Enable(len(mlist) != 0)
		
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

class Materials:
	def __init__(self, fn):
		self.fn = fn
		self.reload()
		
	def reload(self):
		with open(self.fn, "r") as fp:
			self.json = json.load(fp)
			
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
		dlg = ManageMaterialsDlg(parent, self)
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
	
	def save(self):
		with open(self.fn, "w") as fp:
			json.dump(self.json, fp, sort_keys=True, indent=4)
			


