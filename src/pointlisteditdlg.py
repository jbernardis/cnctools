import wx
import os

BTNDIM = (64, 64) if os.name == 'posix' else (48,48)
TCDIM = (80, -1) if os.name == 'posix' else (60, -1)

DEFAULT_TITLE = "Point List Edit"
fmtFloat = "%8.3f"

class PointListEditDialog(wx.Dialog):
	def __init__(self, parent, data, minvals, title=DEFAULT_TITLE):
		self.title = "%s (minimum %d points)" % (title, minvals)
		wx.Dialog.__init__(self, parent, wx.ID_ANY, self.title)
		self.images = parent.images
		
		if data is None:
			self.data = [[0, 0], [10, 0]]
			if minvals > 2:
				self.data.append([0, 10])
		else:
			self.data = [x for x in data]
		self.modified = False
		self.minvals = minvals
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(10)

		self.lbData = wx.ListCtrl(self, wx.ID_ANY, size=(200, 200), style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES | wx.BORDER_SIMPLE | wx.LC_SINGLE_SEL)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onLbSelected, self.lbData)
		self.lbData.SetBackgroundColour(wx.Colour(200, 200, 200))
		self.lbData.InsertColumn(0, "", wx.LIST_FORMAT_RIGHT)
		self.lbData.InsertColumn(1, "X", wx.LIST_FORMAT_RIGHT)
		self.lbData.InsertColumn(2, "Y", wx.LIST_FORMAT_RIGHT)
		self.lbData.SetColumnWidth(0, 30)
		self.lbData.SetColumnWidth(1, 85)
		self.lbData.SetColumnWidth(2, 85)
		hsizer.Add(self.lbData)
		
		hsizer.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		self.bScrollUp = wx.BitmapButton(self, wx.ID_ANY, self.images.pngScrollup, size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBScrollUp, self.bScrollUp)
		self.bScrollUp.SetToolTip("Move the selection cursor up 1 line")
		self.bScrollUp.Enable(False)
		vsz.Add(self.bScrollUp)

		vsz.AddSpacer(50)

		self.bScrollDown = wx.BitmapButton(self, wx.ID_ANY, self.images.pngScrolldown, size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBScrollDown, self.bScrollDown)
		self.bScrollDown.SetToolTip("Move the selection cursor down 1 line")
		self.bScrollDown.Enable(False)
		vsz.Add(self.bScrollDown)

		hsizer.Add(vsz)
		hsizer.AddSpacer(10)

		vsz = wx.BoxSizer(wx.VERTICAL)
		self.bMoveUp = wx.BitmapButton(self, wx.ID_ANY, self.images.pngMoveup, size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBMoveUp, self.bMoveUp)
		self.bMoveUp.SetToolTip("Move the selected point up 1 line")
		self.bMoveUp.Enable(False)
		vsz.Add(self.bMoveUp)

		vsz.AddSpacer(50)

		self.bMoveDown = wx.BitmapButton(self, wx.ID_ANY, self.images.pngMovedown, size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBMoveDown, self.bMoveDown)
		self.bMoveDown.SetToolTip("Move the selected point down 1 line")
		self.bMoveDown.Enable(False)
		vsz.Add(self.bMoveDown)

		hsizer.Add(vsz)
		hsizer.AddSpacer(10)
		
		sizer.Add(hsizer)
		
		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "X:")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

		text = wx.TextCtrl(self, -1, "", size=TCDIM, style=wx.TE_RIGHT)
		text.SetToolTip("Enter the X coordinate")
		self.tcX = text
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

		box.AddSpacer(10)
		
		label = wx.StaticText(self, -1, "Y:")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

		text = wx.TextCtrl(self, -1, "", size=TCDIM, style=wx.TE_RIGHT)
		text.SetToolTip("Enter the Y coordinate")
		self.tcY = text
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
		
		box.AddSpacer(10)
		
		self.bAdd = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAdd, size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBAdd, self.bAdd)
		self.bAdd.SetToolTip("Add a new point to the bottom of the list")
		box.Add(self.bAdd)
		
		box.AddSpacer(10)
		
		self.bRepl = wx.BitmapButton(self, wx.ID_ANY, self.images.pngReplace, size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBRepl, self.bRepl)
		self.bRepl.SetToolTip("Replace the current point")
		self.bRepl.Enable(False)
		box.Add(self.bRepl)

		box.AddSpacer(10)

		self.bDel = wx.BitmapButton(self, wx.ID_ANY, self.images.pngDelete, size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBDel, self.bDel)
		self.bDel.SetToolTip("Delete the selected object")
		self.bDel.Enable(False)
		box.Add(self.bDel)

		sizer.AddSpacer(10)
		sizer.Add(box, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)

		btnsizer = wx.BoxSizer(wx.HORIZONTAL)

		btn = wx.BitmapButton(self, wx.ID_ANY, self.images.pngOk, size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBOk, btn)
		btn.SetToolTip("Complete dialog")
		btnsizer.Add(btn)
		self.bOk = btn
		
		btnsizer.AddSpacer(50)

		btn = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCancel, size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBCancel, btn)
		btn.SetToolTip("Cancel dialog")
		btnsizer.Add(btn)
		self.bCancel = btn

		sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)
		
		self.populateList() 
		self.setXValue(0.0)
		self.setYValue(0.0)
		
	def getValues(self):
		return self.data
		
	def onBOk(self, evt):
		self.EndModal(wx.ID_OK)
		
	def onBCancel(self, evt):
		dlg = wx.MessageDialog(self, 'Are you sure you want to continue?',
							   'Discard Changes?',
							   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()
		
		if rc == wx.ID_NO:
			return
			
		self.EndModal(wx.ID_CANCEL)

	def setXYValues(self, sx):
		self.setXValue(self.data[sx][0])
		self.setYValue(self.data[sx][1])
		
	def setXValue(self, x):
		self.tcX.SetValue(fmtFloat % x)
		
	def setYValue(self, y):
		self.tcY.SetValue(fmtFloat % y)
		
	def setModified(self, flag=True):
		self.modified = flag
		if self.modified:
			self.SetTitle("%s *" % self.title)
		else:
			self.SetTitle(self.title)
		
	def populateList(self):
		sx = self.lbData.GetFirstSelected()
		self.lbData.DeleteAllItems()
		for d in self.data:
			index = self.lbData.GetItemCount()
			self.lbData.InsertItem(index, "%3d" % (index+1))
			self.lbData.SetItem(index, 1, fmtFloat % d[0])
			self.lbData.SetItem(index, 2, fmtFloat % d[1])

		if sx != wx.NOT_FOUND:
			self.lbData.Select(sx)			
		self.updateScrollButtons()
		
	def onBAdd(self, evt):
		try:
			x = float(self.tcX.GetValue())
		except:
			x = 0.0
			
		try:
			y = float(self.tcY.GetValue())
		except:
			y = 0.0
			
		self.data.append([x, y])
		self.populateList()

		self.lbData.Select(len(self.data)-1)
		self.updateScrollButtons()
		self.setModified()
		
	def onBRepl(self, evt):
		sx = self.lbData.GetFirstSelected()
		if sx == wx.NOT_FOUND:
			return
		
		try:
			x = float(self.tcX.GetValue())
		except:
			x = 0.0
			
		try:
			y = float(self.tcY.GetValue())
		except:
			y = 0.0
			
		self.data[sx] = [x, y]
		self.populateList()
		self.setModified()
	
	def onBDel(self, evt):
		ox = self.lbData.GetFirstSelected()
		if ox == wx.NOT_FOUND:
			return

		self.setModified()

		del(self.data[ox])
		self.populateList()

		if ox >= len(self.data):
			ox = len(self.data)-1

		if ox >= 0:
			self.lbData.Select(ox)
		else:
			self.bDel.Enable(False)
			self.bRepl.Enable(False)

		self.updateScrollButtons()
		self.setModified()
		
	def onBScrollUp(self, evt):
		ox = self.lbData.GetFirstSelected()
		self.lbData.Select(ox-1)
		self.updateScrollButtons()

	def onBScrollDown(self, evt):
		ox = self.lbData.GetFirstSelected()
		self.lbData.Select(ox+1)
		self.updateScrollButtons()

	def onBMoveUp(self, evt):
		ox = self.lbData.GetFirstSelected()
		sdata = self.data[ox]
		self.data[ox] = self.data[ox-1]
		self.data[ox-1] = sdata
		self.populateList()
		self.lbData.Select(ox-1)
		self.updateScrollButtons()
		self.setModified()

	def onBMoveDown(self, evt):
		ox = self.lbData.GetFirstSelected()
		sdata = self.data[ox]
		self.data[ox] = self.data[ox+1]
		self.data[ox+1] = sdata
		self.populateList()
		self.lbData.Select(ox+1)
		self.updateScrollButtons()
		self.setModified()
			
	def updateScrollButtons(self):
		l = len(self.data)
		sx = self.lbData.GetFirstSelected()
		if l <= 1 or sx == wx.NOT_FOUND:
			self.bScrollUp.Enable(False)
			self.bScrollDown.Enable(False)
			self.bMoveUp.Enable(False)
			self.bMoveDown.Enable(False)
			self.bRepl.Enable(l == 1 and sx != wx.NOT_FOUND)
			self.bDel.Enable(False)
			return

		self.bScrollUp.Enable(not(sx == 0))
		self.bMoveUp.Enable(not(sx == 0))
		self.bScrollDown.Enable(not (sx == (l-1)))
		self.bMoveDown.Enable(not (sx == (l-1)))
		self.bRepl.Enable(True)
		self.bDel.Enable(l > self.minvals)
		
	def onLbSelected(self, evt):
		self.updateScrollButtons()
		sx = self.lbData.GetFirstSelected()
		self.setXYValues(sx)
