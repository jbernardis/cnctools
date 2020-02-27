import wx
try:
    from agw import floatspin as FS
except ImportError:
    import wx.lib.agw.floatspin as FS

from settings import BTNDIM

DEFAULT_TITLE = "Edit Model"

class editModel(wx.Dialog):
    def __init__(self, parent, title=DEFAULT_TITLE):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.parent = parent
        self.images = self.parent.images
        self.modified = False
        
        self.mirrorX = False
        self.mirrorY = False
        
        boxTrans = wx.StaticBox(self, wx.ID_ANY, "Translate")

        topBorder = boxTrans.GetBordersForSizer()[0]
        bsizer = wx.BoxSizer(wx.VERTICAL)
        bsizer.AddSpacer(topBorder+10)
        
        tsizer = wx.BoxSizer(wx.HORIZONTAL)
        tsizer.AddSpacer(10)
        
        vsz = wx.BoxSizer(wx.VERTICAL)
        hsz = wx.BoxSizer(wx.HORIZONTAL)
        
        hsz.Add(wx.StaticText(boxTrans, wx.ID_ANY, "X:"), 1, wx.ALIGN_CENTER_VERTICAL)
        hsz.AddSpacer(10)
        
        self.scX = FS.FloatSpin(boxTrans, wx.ID_ANY, min_val=-500, max_val=500,
                                       increment=0.1, value=0, agwStyle=FS.FS_RIGHT)
        
        self.scX.SetDigits(2)
        self.Bind(wx.EVT_SPINCTRL, self.onChange, self.scX)
        hsz.Add(self.scX)
        
        vsz.Add(hsz)
        vsz.AddSpacer(5)
        
        hsz = wx.BoxSizer(wx.HORIZONTAL)
        r1 = wx.RadioButton(boxTrans, wx.ID_ANY, "1", style = wx.RB_GROUP )
        self.Bind(wx.EVT_RADIOBUTTON, self.onXRadio, r1)
        hsz.Add(r1)
        r2 = wx.RadioButton(boxTrans, wx.ID_ANY, "0.1" )
        self.Bind(wx.EVT_RADIOBUTTON, self.onXRadio, r2)
        hsz.Add(r2)
        r3 = wx.RadioButton(boxTrans, wx.ID_ANY, "0.01" )
        self.Bind(wx.EVT_RADIOBUTTON, self.onXRadio, r3)
        hsz.Add(r3)
        r2.SetValue(True)
        vsz.Add(hsz)
        
        tsizer.Add(vsz)
        tsizer.AddSpacer(10)
        
        vsz = wx.BoxSizer(wx.VERTICAL)
        hsz = wx.BoxSizer(wx.HORIZONTAL)

        hsz.Add(wx.StaticText(boxTrans, wx.ID_ANY, "Y:"), 1, wx.ALIGN_CENTER_VERTICAL)
        hsz.AddSpacer(10)
        
        self.scY = FS.FloatSpin(boxTrans, wx.ID_ANY, min_val=-500, max_val=500,
                                       increment=0.1, value=0, agwStyle=FS.FS_RIGHT)
        
        self.scY.SetDigits(2)
        self.Bind(wx.EVT_SPINCTRL, self.onChange, self.scY)
        hsz.Add(self.scY)
        
        vsz.Add(hsz)
        vsz.AddSpacer(5)
        
        hsz = wx.BoxSizer(wx.HORIZONTAL)
        r1 = wx.RadioButton(boxTrans, wx.ID_ANY, "1", style = wx.RB_GROUP )
        self.Bind(wx.EVT_RADIOBUTTON, self.onYRadio, r1)
        hsz.Add(r1)
        r2 = wx.RadioButton(boxTrans, wx.ID_ANY, "0.1" )
        self.Bind(wx.EVT_RADIOBUTTON, self.onYRadio, r2)
        hsz.Add(r2)
        r3 = wx.RadioButton(boxTrans, wx.ID_ANY, "0.01" )
        self.Bind(wx.EVT_RADIOBUTTON, self.onYRadio, r3)
        hsz.Add(r3)
        r2.SetValue(True)
        vsz.Add(hsz)
        
        tsizer.Add(vsz)
        tsizer.AddSpacer(20)

        self.bShift = wx.BitmapButton(boxTrans, wx.ID_ANY, self.images.pngTranslate, size=BTNDIM)
        self.bShift.SetToolTip("Apply translation values")
        tsizer.Add(self.bShift)
        self.Bind(wx.EVT_BUTTON, self.bShiftPressed, self.bShift)
        
        tsizer.AddSpacer(10)
        bsizer.Add(tsizer)
        bsizer.AddSpacer(10)

        boxTrans.SetSizer(bsizer)









        boxMirr = wx.StaticBox(self, wx.ID_ANY, "Mirror")

        topBorder = boxTrans.GetBordersForSizer()[0]
        bsizer = wx.BoxSizer(wx.VERTICAL)
        bsizer.AddSpacer(topBorder+10)
        
        tsizer = wx.BoxSizer(wx.HORIZONTAL)
        tsizer.AddSpacer(10)
        
        self.bMirrorX = wx.BitmapButton(boxMirr, wx.ID_ANY, self.images.pngMirrorx, size=BTNDIM)
        self.bMirrorX.SetToolTip("Mirror about X axis")
        tsizer.Add(self.bMirrorX)
        self.Bind(wx.EVT_BUTTON, self.bMirrorXPressed, self.bMirrorX)
        
        tsizer.AddSpacer(50)
        
        self.bMirrorY = wx.BitmapButton(boxMirr, wx.ID_ANY, self.images.pngMirrory, size=BTNDIM)
        self.bMirrorY.SetToolTip("Mirror about Y axis")
        tsizer.Add(self.bMirrorY)
        self.Bind(wx.EVT_BUTTON, self.bMirrorYPressed, self.bMirrorY)
         
        tsizer.AddSpacer(10)
        bsizer.Add(tsizer, 1, wx.ALIGN_CENTER_HORIZONTAL)
        bsizer.AddSpacer(10)
        
        boxMirr.SetSizer(bsizer)






        
        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.AddSpacer(5)
        vsz.Add(boxTrans)
        vsz.AddSpacer(5)
        vsz.Add(boxMirr, 1, wx.EXPAND)
        vsz.AddSpacer(5)
        
        self.bCancel = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCancel, size=BTNDIM)
        self.bCancel.SetToolTip("Cancel with no changes")
        vsz.Add(self.bCancel, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)

        vsz.AddSpacer(5)
        
        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(10)
        hsz.Add(vsz)
        hsz.AddSpacer(10)

        self.SetSizer(hsz)
        self.Layout()
        self.Fit();
        
    def onClose(self, evt):
        self.doCancel()
        
    def bCancelPressed(self, _):
        self.doCancel()
        
    def doCancel(self):
        if self.modified:
            print("Modified")
        self.EndModal(wx.ID_CANCEL)
        
    def bShiftPressed(self, _):
        self.EndModal(wx.ID_OK)   
        
    def bMirrorXPressed(self, _):
        self.mirrorX = True
        self.mirrorY = False
        self.EndModal(wx.ID_OK) 
        
    def bMirrorYPressed(self, _):
        self.mirrorY = True
        self.mirrorX = False
        self.EndModal(wx.ID_OK) 
    
    def onChange(self, _):
        self.setModified()
        
    def onXRadio(self, evt):
        r = evt.GetEventObject()
        self.scX.SetIncrement(float(r.GetLabel()))
        
    def onYRadio(self, evt):
        r = evt.GetEventObject()
        self.scY.SetIncrement(float(r.GetLabel()))
        
    def setModified(self, flag=True):
        self.modified = flag
        
    def getEditValues(self):
        return self.scX.GetValue(), self.scY.GetValue(), self.mirrorX, self.mirrorY
        


