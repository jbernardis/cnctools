from viewer.cnc import CNC, MT_NORMAL, MT_RAPID
from wx import glcanvas
import wx

from OpenGL.GL import (glViewport, GLfloat, glColor3f, glClearColor, glEnable, GL_DEPTH_TEST, GL_CULL_FACE,
			GL_LIGHTING, GL_LIGHT0, GL_LIGHT1, glLightfv, GL_POSITION, GL_SPECULAR, GL_DIFFUSE,
					   glMaterialf, glMaterialfv, GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, GL_SHININESS,
					   GL_EMISSION, glMatrixMode, GL_PROJECTION, glLoadIdentity, glFrustum, GL_MODELVIEW,
					   glRotatef, glTranslatef, glClear, glColorMaterial, GL_COLOR_MATERIAL,
					   GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glBegin, GL_LINES, glColor, glVertex3f, glEnd,
					   glDisable, GL_LINE_STRIP)
from OpenGL.GLU import gluLookAt

BUTTONDIM = (48,48)



def vec(*args):
	return (GLfloat * len(args))(*args)
	
class ViewCanvas(glcanvas.GLCanvas):
	def __init__(self, parent, wid=-1, buildarea=(200, 200), pos=wx.DefaultPosition,
				 size=(600, 600), style=0):
		attribList = (glcanvas.WX_GL_RGBA,  # RGBA
					  glcanvas.WX_GL_DOUBLEBUFFER,  # Double Buffered
					  glcanvas.WX_GL_DEPTH_SIZE, 24)  # 24 bit

		glcanvas.GLCanvas.__init__(self, parent, wid, size=size, style=style, pos=pos, attribList=attribList)
		self.init = False
		self.context = glcanvas.GLContext(self)

		self.gridVertices = None
		self.gridColors = None
		self.dataPoints = []

		# initial mouse position
		self.lastx = self.x = 0
		self.lasty = self.y = 0
		self.anglex = self.angley = self.anglez = 0
		self.transx = self.transy = 0
		self.resetView = True
		self.light0Pos = [0, 50, 150]
		self.light1Pos = [0, -50, 150]
		self.size = None
		
		self.clientwidth = size[0]
		self.drawGrid = True
		self.drawZGrid = False
		self.zoom = 1.0
		self.buildarea = buildarea
		self.adjPt = [x/2 for x in buildarea]
		
		self.setGridArrays()

		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
		self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDouble)
		self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
		self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheel)
		self.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
		self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

	def OnEraseBackground(self, event):
		pass # Do nothing, to avoid flashing on MSW.

	def OnSize(self, event):
		size = self.size = self.GetClientSize()
		if self.GetParent().IsShown():
			if self.context is not None:
				self.SetCurrent(self.context)
			glViewport(0, 0, size.width, size.height)
		event.Skip()

	def OnPaint(self, _):
		_ = wx.PaintDC(self)
		if self.IsShown():
			self.SetCurrent(self.context)
			if not self.init:
				self.init = True
				self.InitGL()
			self.OnDraw()

	def OnMouseDown(self, evt):
		self.SetFocus()
		self.CaptureMouse()
		self.x, self.y = self.lastx, self.lasty = evt.GetPosition()
		
	def OnMouseRightDown(self, evt):
		self.SetFocus()
		self.CaptureMouse()
		self.x, self.y = self.lastx, self.lasty = evt.GetPosition()

	def OnMouseUp(self, _):
		if self.HasCapture():
			self.ReleaseMouse()

	def OnMouseRightUp(self, _):
		if self.HasCapture():
			self.ReleaseMouse()
		
	def OnMouseDouble(self, _):
		self.resetView = True
		self.setZoom(1.0)
		self.Refresh(False)

	def OnMouseMotion(self, evt):
		if evt.Dragging() and evt.LeftIsDown():
			self.lastx, self.lasty = self.x, self.y
			self.x, self.y = evt.GetPosition()
			self.anglex = self.x - self.lastx
			self.angley = self.y - self.lasty
			self.transx = 0
			self.transy = 0
			self.Refresh(False)

		elif evt.Dragging() and evt.RightIsDown():
			self.lastx, self.lasty = self.x, self.y
			self.x, self.y = evt.GetPosition()
			self.anglex = 0
			self.angley = 0
			self.transx = (self.x - self.lastx)*self.zoom/3.0
			self.transy = -(self.y - self.lasty)*self.zoom/3.0
			self.Refresh(False)
		
	def OnWheel(self, evt):
		z = evt.GetWheelRotation()
		if z < 0:
			zoom = self.zoom*0.9
		else:
			zoom = self.zoom*1.1
				
		self.setZoom(zoom)
		self.Refresh(False)
		
	def InitGL(self):
		glClearColor(0.0, 0.0, 0.0, 1)
		glColor3f(1, 0, 0)
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_CULL_FACE)

		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		glEnable(GL_LIGHT1)

		glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
		glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 0.5, 1))
		glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
		glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
		glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
		glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))

		glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0, 0.3, 1))
		glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
		glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 80)
		glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, vec(0.1, 0.1, 0.1, 0.9))
		
		glLightfv(GL_LIGHT0, GL_POSITION, vec(0.0, 200.0, 100.0, 1))
		glLightfv(GL_LIGHT1, GL_POSITION, vec(0.0, -200.0, 100.0, 1))
		
	def setDrawGrid(self, flag):
		self.drawGrid = flag
		self.setGridArrays()
		self.Refresh(True)
		
	def setDrawZGrid(self, flag):
		self.drawZGrid = flag
		self.setGridArrays()
		self.Refresh(True)

	def setZoom(self, zoom):
		self.zoom = zoom
				
	def setGridArrays(self):
		self.gridVertices = []
		self.gridColors = []

		if self.drawGrid:		
			self.gridVertices.append([-500, 0, 0, 500, 0, 0])
			self.gridColors.append([1.0, 0.0, 0.0, 1])
			v = -500
			while v <= 500:
				if v % 50 == 0:
					vl = 4
				else:
					vl = 2
				if v != 0:
					self.gridVertices.append([v, -vl, 0, v, vl, 0])
					self.gridColors.append([1.0, 0.0, 0.0, 1])
				v += 10
	
			self.gridVertices.append([0, -500, 0, 0, 500, 0])
			self.gridColors.append([0.0, 1.0, 0.0, 1])
			v = -500
			while v <= 500:
				if v % 50 == 0:
					vl = 4
				else:
					vl = 2
				if v != 0:
					self.gridVertices.append([-vl, v, 0, vl, v, 0])
					self.gridColors.append([0.0, 1.0, 0.0, 1])
				v += 10

		if self.drawGrid and self.drawZGrid:			
			self.gridVertices.append([0, 0, -500, 0, 0, 500])
			self.gridColors.append([0.0, 0.0, 1.0, 1])
			v = -500
			while v <= 500:
				if v % 50 == 0:
					vl = 4
				else:
					vl = 2
				if v != 0:
					self.gridVertices.append([0, -vl, v, 0, vl, v])
					self.gridColors.append([0.0, 0.0, 1.0, 1])
				v += 10
			
			
	def setPoints(self, pts):
		self.dataPoints = pts[:]
		self.Refresh(True)

	def OnDraw(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glFrustum(-50.0*self.zoom, 50.0*self.zoom, -50.0*self.zoom, 50.0*self.zoom, 200, 800.0)
		#glTranslatef(0.0, 0.0, -400.0)
		gluLookAt (200.0, -200.0, 400.0, 0.0, 0.0, 0.0, -1.0, 1.0, 0.0)

		glMatrixMode(GL_MODELVIEW)
		if self.resetView:
			glLoadIdentity()
			self.lastx = self.x = 0
			self.lasty = self.y = 0
			self.anglex = self.angley = self.anglez = 0
			self.transx = self.transy = 0
			self.resetView = False
			
		if self.size is None:
			self.size = self.GetClientSize()
		w, h = self.size
		w = max(w, 1.0)
		h = max(h, 1.0)
		xScale = 180.0 / w
		yScale = 180.0 / h
		glRotatef(self.angley * yScale, 1.0, 0.0, 0.0)
		glRotatef(self.anglex * xScale, 0.0, 1.0, 0.0)
		glRotatef(self.anglez, 0.0, 0.0, 1.0)
		glTranslatef(self.transx, self.transy, 0.0)

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
		glEnable(GL_COLOR_MATERIAL)

		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		glEnable(GL_LIGHT1)
		
		if self.drawGrid:
			glBegin(GL_LINES)
			for i in range(len(self.gridVertices)):
				glColor(self.gridColors[i])
				p = self.gridVertices[i]
				glVertex3f(p[0], p[1], p[2])
				glVertex3f(p[3], p[4], p[5])
			glEnd()

		colors = {
			MT_RAPID:  [0.0, 1.0, 1.0, 1],
			MT_NORMAL: [1.0, 1.0, 1.0, 1]
		}
			
		currentLineType = MT_RAPID
		glColor(colors[MT_RAPID])
		
		glBegin(GL_LINE_STRIP)
		for p in self.dataPoints:
			if p[3] != currentLineType:
					currentLineType = p[3]
					glColor(colors[currentLineType])
			glVertex3f(p[0], p[1], p[2])
			
		glEnd()
				
		self.SwapBuffers()
		
		glDisable(GL_LIGHT0)
		glDisable(GL_LIGHT1)
		glDisable(GL_LIGHTING)
			
		self.anglex = self.angley = self.anglez = 0
		self.transx = self.transy = 0
		

class NCViewer(wx.Dialog):
	def __init__(self, parent, title, settings):
		self.settings = settings
		self.showGrid = True
		self.showZGrid = True
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(200,200)) #, style=wx.CAPTION)
		
		self.gl = ViewCanvas(self, buildarea=(200, 200))
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.AddSpacer(10)
		csizer = wx.BoxSizer(wx.HORIZONTAL)
		csizer.AddSpacer(10)
		csizer.Add(self.gl)
		csizer.AddSpacer(10)
		sizer.Add(csizer)
		sizer.AddSpacer(10)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.cbShowGrid = wx.CheckBox(self, wx.ID_ANY, "Draw Axes")
		self.cbShowGrid.SetValue(self.showGrid)
		self.gl.setDrawGrid(self.showGrid)
		self.Bind(wx.EVT_CHECKBOX, self.onShowGrid, self.cbShowGrid)		
		hsizer.Add(self.cbShowGrid)
		
		hsizer.AddSpacer(20)
		
		self.cbShowZGrid = wx.CheckBox(self, wx.ID_ANY, "Draw Z Axis")
		self.cbShowZGrid.SetValue(self.showZGrid)
		self.gl.setDrawZGrid(self.showZGrid)
		self.Bind(wx.EVT_CHECKBOX, self.onShowZGrid, self.cbShowZGrid)		
		hsizer.Add(self.cbShowZGrid)
		self.cbShowZGrid.Enable(self.showGrid)
		
		sizer.Add(hsizer, 1, wx.ALIGN_CENTER_HORIZONTAL)
		
		sizer.AddSpacer(10)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit()
		
	def onShowGrid(self, _):
		self.showGrid = self.cbShowGrid.GetValue()
		self.gl.setDrawGrid(self.showGrid)
		self.cbShowZGrid.Enable(self.showGrid)
		
	def onShowZGrid(self, _):
		self.showZGrid = self.cbShowZGrid.GetValue()
		self.gl.setDrawZGrid(self.showZGrid)

	def loadGCode(self, gcode):			
		self.gcode = gcode
		self.cnc = CNC()
				
		for gl in self.gcode:
			self.cnc.execute(gl)
			
		self.gl.setPoints(self.cnc.getPoints())
	
		


