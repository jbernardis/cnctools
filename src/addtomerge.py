import wx
import os
from gcodelist import GCodeList
from editmodel import editModel
from viewer.cnc import gShifter, gMirror

from settings import BTNDIM

DEFAULT_TITLE = "Add File to Merge"
wildcard = "G Code (*.nc)|*.nc|"     \
           "All files (*.*)|*.*"

class AddToMergeDialog(wx.Dialog):
    def __init__(self, parent, title=DEFAULT_TITLE):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        self.modified = False
        self.title = title
        self.parent = parent
        self.settings = self.parent.settings
        self.images = self.parent.images
        
        self.gCode = []
        
        hsizer=wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddSpacer(10)
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.AddSpacer(10)
        
        self.gcl = GCodeList(self)
        vsizer.Add(self.gcl)
        
        vsizer.AddSpacer(20)
        
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.bAdd = wx.BitmapButton(self, wx.ID_ANY, self.images.pngFileopen, size=BTNDIM)
        self.bAdd.SetToolTip("Choose a file to add")
        btnSizer.Add(self.bAdd)
        self.Bind(wx.EVT_BUTTON, self.bAddPressed, self.bAdd)
        
        btnSizer.AddSpacer(10)

        self.bEdit = wx.BitmapButton(self, wx.ID_ANY, self.images.pngEdit, size=BTNDIM)
        self.bEdit.SetToolTip("Modify file before merging")
        btnSizer.Add(self.bEdit)
        self.Bind(wx.EVT_BUTTON, self.bEditPressed, self.bEdit)
        self.bEdit.Enable(False)
        
        btnSizer.AddSpacer(10)

        self.bView = wx.BitmapButton(self, wx.ID_ANY, self.images.pngView, size=BTNDIM)
        self.bView.SetToolTip("Examine file and applied edits before merge")
        btnSizer.Add(self.bView)
        self.Bind(wx.EVT_BUTTON, self.bViewPressed, self.bView)
        self.bView.Enable(False)
        
        btnSizer.AddSpacer(10)

        self.bOK = wx.BitmapButton(self, wx.ID_ANY, self.images.pngMerge, size=BTNDIM)
        self.bOK.SetToolTip("Commit this file to the merge")
        btnSizer.Add(self.bOK)
        self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
        self.bOK.Enable(False)
        
        btnSizer.AddSpacer(20)

        self.bCancel = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCancel, size=BTNDIM)
        self.bCancel.SetToolTip("Cancel without adding this file to the merge")
        btnSizer.Add(self.bCancel)
        self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
        
        vsizer.Add(btnSizer, 1, wx.ALIGN_CENTER_HORIZONTAL)
 
        vsizer.AddSpacer(20)
        hsizer.Add(vsizer)       
        hsizer.AddSpacer(10)
        self.SetSizer(hsizer)
        self.Layout()
        self.Fit();
        
    def setTitle(self):
        self.SetTitle(self.title)
        
    def setModified(self, flag=True):
        self.modified = flag
        self.setTitle()
       
    def bOKPressed(self, _):
        self.EndModal(wx.ID_OK)
        
    def bCancelPressed(self, _):
        self.doCancel()
        
    def onClose(self, _):
        self.doCancel()
        
    def doCancel(self):
        if self.modified:
            dlg = wx.MessageDialog(self, 'File will not be added to merge',
                               'Proceed?',
                               wx.YES_NO | wx.ICON_WARNING)
            rc = dlg.ShowModal()
            dlg.Destroy()
            if rc == wx.ID_NO:
                return 
            
        self.EndModal(wx.ID_CANCEL)
        
    def bAddPressed(self, _):
        if self.modified:
            dlg = wx.MessageDialog(self, "File \"%s\" has not been added to merge" % self.title,
                'Proceed?',
                wx.YES_NO | wx.ICON_WARNING)
            rc = dlg.ShowModal()
            dlg.Destroy()
            if rc == wx.ID_NO:
                return 
            
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
        
        pdir, self.title = os.path.split(path)

        if pdir != self.settings.lastloaddir:
            self.settings.lastloaddir = pdir
            self.settings.setModified()
        
        with open(path, "r") as fp:
            self.gCode = fp.readlines()
            
        self.gcl.updateList(self.gCode)
            
        self.setModified()
        self.bView.Enable()
        self.bEdit.Enable()
        self.bOK.Enable()
        
    def bEditPressed(self, _):
        dlg = editModel(self)
        rc = dlg.ShowModal()
        if rc != wx.ID_OK:
            dlg.Destroy()
            return 
        
        dx, dy, mx, my = dlg.getEditValues()
        dlg.Destroy()
        
        if mx:
            mir = gMirror()
            self.gCode = [mir.mirrorX(x) for x in self.gCode]
            self.gcl.updateList(self.gCode)
        elif my:
            mir = gMirror()
            self.gCode = [mir.mirrorY(x) for x in self.gCode]
            self.gcl.updateList(self.gCode)
        else:
            shft = gShifter(dx, dy)
            self.gCode = [shft.shift(x) for x in self.gCode]
            self.gcl.updateList(self.gCode)
            
        self.setModified()
       
    def getGCode(self):
        return self.gCode
        
    def bViewPressed(self, _):
        self.gcl.visualize(title=self.title)

