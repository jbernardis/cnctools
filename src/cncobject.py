'''
Created on Jan 31, 2020

@author: jeffb
'''
from validators import verifyExitNoSave, verifyExitNoGenerate, verifyStaleGCodeSave
import wx

class CNCObject:
    def __init__(self):
        pass
        
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
       
    def bVisualizePressed(self, _):
        self.gcl.visualize(title=self.viewTitle)

