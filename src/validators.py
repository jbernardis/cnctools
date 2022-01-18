import wx

def ValidateToolSize(parent, tool, item, name):
	if tool <= item:
		return True
	
	dlg = wx.MessageDialog(parent, "Tool Size must be <= %s" % name,
		'Tool Size Too Large', wx.OK | wx.ICON_ERROR)
	
	dlg.ShowModal()
	dlg.Destroy()

	return False

def ValidateMinLength(parent, size, minv, name, namemin):
	if size >= minv:
		return True
	
	dlg = wx.MessageDialog(parent, "%s must be >= %s" % (name, namemin),
		name + " too small", wx.OK | wx.ICON_ERROR)
	
	dlg.ShowModal()
	dlg.Destroy()

	return False

def ValidateNonZero(parent, val, name):
	if val != 0:
		return True
	
	dlg = wx.MessageDialog(parent, name + " is 0",
		'Zero Value', wx.OK | wx.ICON_ERROR)
	
	dlg.ShowModal()
	dlg.Destroy()
	return False
	
def ValidateRange(parent, value, vmin, vmax, name, rangename):
	if value >= vmin and value <= vmax:
		return True
	
	dlg = wx.MessageDialog(parent, name + " is out or range: " + rangename,
		'Value Our Of Range', wx.OK | wx.ICON_ERROR)
	
	dlg.ShowModal()
	dlg.Destroy()
	return False

def ValidateTrue(parent, condition, message):
	if not condition:
		dlg = wx.MessageDialog(parent, message,
							'Value must be True', wx.OK | wx.ICON_ERROR)
	
		dlg.ShowModal()
		dlg.Destroy()
	return condition
	
def ValidateNoEntryErrors(parent, fields):
	if len(fields) == 0:
		return True
	dlg = wx.MessageDialog(parent, "The values for the following fields cannot be interpreted: " + ", ".join(fields),
		'Field value errors', wx.OK | wx.ICON_ERROR)
	
	dlg.ShowModal()
	dlg.Destroy()
	return False
	
def verifyStaleGCodeSave(parent):
	dlg = wx.MessageDialog(parent, 'Generated G Code is stale\nPress yes to save anyway\notherwise press no to go back and re-generate',
                               'Stale G Code',
                               wx.YES_NO | wx.ICON_WARNING)
	rc = dlg.ShowModal()
	dlg.Destroy()
	return rc == wx.ID_YES
	
def verifyStaleGCodeView(parent):
	dlg = wx.MessageDialog(parent, 'Generated G Code is stale\nPress yes to view anyway\notherwise press no to go back and re-generate',
                               'Stale G Code',
                               wx.YES_NO | wx.ICON_WARNING)
	rc = dlg.ShowModal()
	dlg.Destroy()
	return rc == wx.ID_YES
	
def verifyExitNoGenerate(parent):
	dlg = wx.MessageDialog(parent, 'Changes made, G Code not generated\nPress yes to exit anyway',
                               'Data has changed',
                               wx.YES_NO | wx.ICON_WARNING)
	rc = dlg.ShowModal()
	dlg.Destroy()
	return rc == wx.ID_YES
	
def verifyExitNoSave(parent):
	dlg = wx.MessageDialog(parent, 'Generated G Code has not been saved\nPress yes to exit anyway',
                               'Unsaved G Code',
                               wx.YES_NO | wx.ICON_WARNING)
	rc = dlg.ShowModal()
	dlg.Destroy()
	return rc == wx.ID_YES

	

