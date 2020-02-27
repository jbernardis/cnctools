import os
import  wx
from viewer.ncviewer import NCViewer

wildcard = "G Code (*.nc)|*.nc|"	 \
		   "All files (*.*)|*.*"

class GCodeList(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent
		self.model = None
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(-1, 300),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_NO_HEADER
			)

		self.InsertColumn(0, "")
		self.SetColumnWidth(0, 300)
		self.Bind(wx.EVT_SIZE, self.onResize)

		self.gcode = []
		self.SetItemCount(0)

		self.attr2 = wx.ListItemAttr()
		self.attr2.SetBackgroundColour("light blue")

	def updateList(self, gcode):
		self.SetItemCount(0)
		self.gcode = gcode[:]
		self.SetItemCount(len(self.gcode))
		
	def save(self, settings):
		dlg = wx.FileDialog(self.parent, message="Save G Code file as ...", defaultDir=settings.lastsavedir,
			defaultFile="", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return False
		
		path = dlg.GetPath()
		dlg.Destroy()
		pdir = os.path.split(path)[0]
		if pdir != settings.lastsavedir:
			settings.lastsavedir = pdir
			settings.setModified()
			
		try:
			with open(path, 'w') as f:
				for item in self.gcode:
					f.write("%s\n" % item)
		except IOError:
			dlg = wx.MessageDialog(self.parent, "Unable to open (%s) for writing" % path,
					'I/O Error', wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return False
		
		return True
		
	def clear(self):
		self.SetItemCount(0)
		self.gcode = []
		
	def onResize(self, evt):
		cw = self.GetSize()[0]
		self.SetColumnWidth(0, cw)

	def OnGetItemText(self, item, col):
		if item < 0 or item >= len(self.gcode):
			return None
		
		return self.gcode[item]

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.attr2
		else:
			return None
		
	def visualize(self, title=""):
		vwrDlg = NCViewer(self.parent, title, self.parent.settings)
		vwrDlg.loadGCode(self.gcode)
		vwrDlg.ShowModal()
		vwrDlg.Destroy()
