import wx
import os
from gcodelist import GCodeList
from addtomerge import AddToMergeDialog
from settings import BTNDIM

DEFAULT_TITLE = "File Merge"
wildcard = "G Code (*.nc)|*.nc|"     \
           "All files (*.*)|*.*"

class FileMergeDialog(wx.Dialog):
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

        self.bAdd = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAdd, size=BTNDIM)
        self.bAdd.SetToolTip("Add a file to the merge")
        btnSizer.Add(self.bAdd)
        self.Bind(wx.EVT_BUTTON, self.bAddPressed, self.bAdd)
        
        btnSizer.AddSpacer(10)

        self.bSave = wx.BitmapButton(self, wx.ID_ANY, self.images.pngFilesaveas, size=BTNDIM)
        self.bSave.SetToolTip("Save files merged thus far")
        btnSizer.Add(self.bSave)
        self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
        self.bSave.Enable(False)
        
        btnSizer.AddSpacer(10)

        self.bView = wx.BitmapButton(self, wx.ID_ANY, self.images.pngView, size=BTNDIM)
        self.bView.SetToolTip("View the merged data")
        btnSizer.Add(self.bView)
        self.Bind(wx.EVT_BUTTON, self.bViewPressed, self.bView)
        self.bView.Enable(False)
        
        btnSizer.AddSpacer(60)

        self.bOK = wx.BitmapButton(self, wx.ID_ANY, self.images.pngExit, size=BTNDIM)
        btnSizer.Add(self.bOK)
        self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
          
        vsizer.Add(btnSizer, 1, wx.ALIGN_CENTER_HORIZONTAL)

 
        vsizer.AddSpacer(20)
        hsizer.Add(vsizer)       
        hsizer.AddSpacer(10)
        self.SetSizer(hsizer)
        self.Layout()
        self.Fit();
        
    def setTitle(self):
        t = self.title
        if self.modified:
            t += " *"
        self.SetTitle(t)
        
    def setModified(self, flag=True):
        self.modified = flag
        self.bSave.Enable(flag)
        self.setTitle()
       
    def bOKPressed(self, _):
        self.cancelMerge()
        
    def onClose(self, _):
        self.cancelMerge()
        
    def cancelMerge(self):
        if self.modified:
            dlg = wx.MessageDialog(self, 'Merged G Code not saved',
                               'Proceed?',
                               wx.YES_NO | wx.ICON_WARNING)
            rc = dlg.ShowModal()
            dlg.Destroy()
            if rc == wx.ID_NO:
                return 
            
        self.EndModal(wx.ID_CANCEL)
        
    def bAddPressed(self, _):
        dlg = AddToMergeDialog(self)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return 

        self.gCode.extend(dlg.getGCode())
        dlg.Destroy()
            
        self.gcl.updateList(self.gCode)
            
        self.setModified()
        self.bView.Enable(True)
        
    def bViewPressed(self, _):
        self.gcl.visualize("Merged files")
        
    def bSavePressed(self, _):
        if self.gcl.save(self.settings):
            self.setModified(False)

