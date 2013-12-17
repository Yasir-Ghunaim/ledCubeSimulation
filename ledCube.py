from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from wx.glcanvas import GLCanvas
import wx,sys,time,serial

#============================================LED=======================================================
class Led():
    def __init__(self,x,y,z,color=[]):
        self.xPos=x
        self.yPos=y
        self.zPos=z
        self.numFrames=0
        self.frames=[]
        self.addFrame(color)
        #transition variables
        self.simulationColor = wx.Colour(0, 0, 0, 255)
        self.startColor = wx.Colour(0, 0, 0, 255)
        self.endColor = wx.Colour(0, 0, 0,255)
        self.colorTransitionFactor = [0, 0, 0]
    def addFrame(self,color=[]):
        self.frames.append(wx.Colour(color[0],color[1],color[2],color[3]))
        self.numFrames += 1
    def setFrame(self,index,color=[]):
        self.frames[index].Set(color[0],color[1],color[2],color[3])
    def makeColorTransition(self, index, time):
        self.startColor = self.frames[index]
        self.endColor = self.frames[index+1]
        for i in range(3):
            self.colorTransitionFactor[i] = (self.endColor[i] - self.startColor[i])/time
        

#============================================openGL=======================================================
class myGLCanvas(GLCanvas):
    def __init__(self, *args, **kwargs):
        GLCanvas.__init__(self, *args, **kwargs)
        glutInit(sys.argv) 
        self.Bind(wx.EVT_PAINT, self.OnPaint)
       # self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_MOTION, self.OnMouse)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPressed)
        self.init = False
        self.width, self.height = self.GetSize()

        self.selectedX = 0
        self.selectedY = 0
        self.selectedZ = 0
        self.selectionCounter = 0
       
        self.alpha = 0
        self.beta = 0
        self.distance = 12.0

        self.oldX = 0
        self.oldY = 0
        self.leftDown = False
        self.rightDown = False

        self.axes = False

        self.led = [[[0 for x in range(8)] for y in range(8)] for z in range(8)]
        for z in range(8):
            for y in range(8):
                for x in range(8):
                    self.led[z][y][x] = Led(x-4,y-4,z-4,color=(255,0,0,255)) # subtract 4 to align the cube in the center of the screen       
    #-----------------------------------------------------------------------------------------------
    def setPanel(self,panel):
        self.panel = panel
   
    def glut_print(self, x,  y,  font,  text, r,  g , b , a):
        blending = False
        if glIsEnabled(GL_BLEND) :
            blending = True
            #glEnable(GL_BLEND)
        glColor3f(1,1,1)
        glWindowPos2f(x,y)
        for ch in text :
            glutBitmapCharacter( font , ctypes.c_int( ord(ch) ) )

        if not blending :
            glDisable(GL_BLEND) 
    
    #-----------------------------------------------------------------------------------------------
    def Axes(self, allow):
        self.axes = allow

    #-----------------------------------------------------------------------------------------------
    def onSimulate(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        wx.CallAfter(self.SetFocus)
        self.glut_print( 10 , 465 , GLUT_BITMAP_9_BY_15 , "Left click to rotate" , 1.0 , 1.0 , 1.0 , 1.0 ) 
        self.glut_print( 640 , 465 , GLUT_BITMAP_9_BY_15 , "Right click to zoom" , 1.0 , 1.0 , 1.0 , 1.0 ) 
        
        for z in range(8):
            for y in range(8):
                for x in range(8):
                    currentLed = self.led[z][y][x]
                    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (currentLed.simulationColor.Red()/255.0,currentLed.simulationColor.Green()/255.0,currentLed.simulationColor.Blue()/255.0, 1.0)) 
                    self.drawSphere(currentLed.xPos,currentLed.yPos,currentLed.zPos)
       
        if self.axes:
            self.ShowAxes()

        self.SwapBuffers()

    def OnDraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        wx.CallAfter(self.SetFocus)
        self.glut_print( 10 , 465 , GLUT_BITMAP_9_BY_15 , "Left click to rotate" , 1.0 , 1.0 , 1.0 , 1.0 ) 
        self.glut_print( 640 , 465 , GLUT_BITMAP_9_BY_15 , "Right click to zoom" , 1.0 , 1.0 , 1.0 , 1.0 ) 
        index = self.panel.selectedFrame
        
        for z in range(8):
            for y in range(8):
                for x in range(8):
                    currentLed = self.led[z][y][x]
                    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (currentLed.frames[index].Red()/255.0,currentLed.frames[index].Green()/255.0,currentLed.frames[index].Blue()/255.0, 1.0)) 
                    #set color of selected led to black
                    if self.panel.colorAll == False and x == self.selectedX and y == self.selectedY and z == self.selectedZ:
                        if self.selectionCounter == 0:
                            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1.0, 1.0, 1.0, 0.5)) 
               
                    self.drawSphere(currentLed.xPos,currentLed.yPos,currentLed.zPos)
        
        if self.axes:
            self.ShowAxes()

        self.SwapBuffers()

    def drawSphere(self,x,y,z):
        glPushMatrix()
        glTranslate(x,y,z)
        glutSolidSphere(0.2,20,20)
        glPopMatrix()
      
      #-----------------------------------------------------------------------------------------------
    def ChangeView(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslate(0.0, 0.0, -self.distance)
        glRotate(-90, 0.0, 1.0, 0.0)
        glRotate(-90, 1.0, 0.0, 0.0)

        glRotate(self.alpha, 0.0, 0.0, 1.0)
        glRotate(self.beta, 0.0, 1.0, 0.0)

        self.OnDraw()

    #-----------------------------------------------------------------------------------------------
    def Resize(self):
        ratio = float(self.width) / self.height;

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0, 0, self.width, self.height)
        gluPerspective(45, ratio, 1, 1000)
        self.ChangeView()

    #-----------------------------------------------------------------------------------------------
    def OnPaint(self, event):
        wx.PaintDC(self)
        self.SetCurrent()
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    #-----------------------------------------------------------------------------------------------
    def OnLeftDown(self, event):
        self.oldX, self.oldY = event.GetPosition()
        self.leftDown = True

    def OnRightDown(self, event):
        self.oldX, self.oldY = event.GetPosition()
        self.rightDown = True

    def OnLeftUp(self, event):
        self.leftDown = False

    def OnRightUp(self, event):
        self.rightDown = False

    def OnMouse(self, event):
        if self.leftDown or self.rightDown:
            X, Y = event.GetPosition()
            if self.rightDown:
                self.distance += (Y - self.oldY) * 0.05

            if self.leftDown:
                self.alpha += (X - self.oldX) * 0.5
                self.beta += (Y - self.oldY) * 0.5

            self.ChangeView()
            self.oldX, self.oldY = X, Y
    def onKeyPressed(self, event):
        keycode = event.GetKeyCode()
        if keycode == 314:      #left arrow
            self.selectedX = (self.selectedX - 1) % 8
            print self.selectedX
        elif keycode == 315:    #up arrow
            self.selectedY = (self.selectedY + 1) % 8
            print self.selectedY
        elif keycode == 316:    #right arrow
            self.selectedX = (self.selectedX + 1) % 8
            print self.selectedX
        elif keycode == 317:    #down arrow
            self.selectedY = (self.selectedY - 1) % 8
            print self.selectedY
        elif keycode == 366:    #page up
            self.selectedZ = (self.selectedZ + 1) % 8
            print self.selectedZ
        elif keycode == 367:    #page down
            self.selectedZ = (self.selectedZ - 1) % 8
            print self.selectedZ
        elif keycode == 67:     #c clicked
            self.panel.onColorChanged(None)
        print keycode
        self.selectionCounter = 0
        self.OnDraw()
        event.Skip()
        
  #-----------------------------------------------------------------------------------------------
    def OnResize(self, e):
        self.width, self.height = e.GetSize()
        self.Resize()

    #-----------------------------------------------------------------------------------------------
    def ShowAxes(self):
        glDisable(GL_LIGHTING)

        glColor3f(1.0, 1.0, 0.0)
        glRasterPos3f(1.2, 0.0, 0.0)
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('x'))
        glRasterPos3f(0.0, 1.2, 0.0)
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('y'))
        glRasterPos3f(0.0, 0.0, 1.2)
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('z'))

        glColor3f(0.1, 0.1, 0.1)
        glBegin(GL_QUADS)
        glVertex3f(-5, -5, -4.2)
        glVertex3f(5, -5, -4.2)
        glVertex3f(5, 5, -4.2)
        glVertex3f(-5, 5, -4.2)
        glEnd()
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 1)
        glVertex3f(0, 1, 1)
        glVertex3f(0, 1, 0)
        glEnd()
        glColor3f(0.0, 0.0, 1.0)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(1, 0, 0)
        glVertex3f(1, 0, 1)
        glVertex3f(0, 0, 1)
        glEnd()

        glEnable(GL_LIGHTING)

    #-----------------------------------------------------------------------------------------------
    def InitGL(self):
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  (0.8, 0.8, 0.8, 1.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT,  (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, (1.0, 1.0, 1.0, 0.0))
        glEnable(GL_LIGHT0)

      #  glShadeModel(GL_SMOOTH)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)

        self.Resize()










#=========================================Right Side Panel==========================================================
class ToolPanel(wx.Panel):
    def __init__(self, parent, canvas, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.canvas = canvas
        self.selectedFrame = 0
        self.running = False
        self.colorAll = True
      
      #create layout childs on the right side 
        self.frameButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.addFrameButton = wx.Button(self, label="Add")
        self.removeFrameButton = wx.Button(self, label="Remove")
        self.frameList = wx.ListCtrl(self, size=(-1,180),style=wx.LC_REPORT)
        self.frameList.InsertColumn(0, 'Name')
        self.frameList.InsertColumn(1, 'Time')
        self.frameList.InsertStringItem(0, 'frame 1')
        self.frameList.SetStringItem(0, 1, '1000')
        self.colorPicker = wx.ColourPickerCtrl(self, col=(255,0,0,1), style=wx.CLRP_USE_TEXTCTRL)
        radioList = ['All', 'Specific LED']
        self.colorRadio = wx.RadioBox(self, label="Coloring options:", choices=radioList,  majorDimension=3, style=wx.RA_SPECIFY_COLS)
        self.axesCheck = wx.CheckBox(self, label="Show Axes")    
        self.runButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.runButton = wx.Button(self, label="Run")
        self.stopButton = wx.Button(self, label="Stop")
        self.stopButton.Disable()
        self.generateButton = wx.Button(self, label ="Generate")
        self.gaugeBar = wx.Gauge(self, size =(150,25))
        self.gaugeBar.Hide()

        #bind 
        self.Bind(wx.EVT_CHECKBOX, self.axesCheckBox)
        self.addFrameButton.Bind(wx.EVT_BUTTON, self.onAddFrame)
        self.removeFrameButton.Bind(wx.EVT_BUTTON, self.onRemoveFrame)
        self.frameList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onEditFrame)
        self.frameList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        self.colorPicker.Bind(wx.EVT_COLOURPICKER_CHANGED, self.onColorChanged)
        self.colorRadio.Bind(wx.EVT_RADIOBOX, self.onRadio)

        self.runButton.Bind(wx.EVT_BUTTON, self.onRunButton)
        self.stopButton.Bind(wx.EVT_BUTTON, self.onStopButton)
        self.generateButton.Bind(wx.EVT_BUTTON, self.onGenerateButton)
        
        # add childs to a BoxSizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.frameButtonSizer.Add(self.addFrameButton, border=5)
        self.frameButtonSizer.Add(self.removeFrameButton, border=5)
        self.sizer.Add(self.frameButtonSizer, flag=wx.CENTER)
        self.sizer.Add(self.frameList, flag=wx.CENTER|wx.EXPAND, border=5)
        self.sizer.Add(self.colorPicker, flag=wx.CENTER, border=5)
        self.sizer.Add(self.colorRadio, flag = wx.TOP|wx.BOTTOM, border = 5)
        self.sizer.Add(self.axesCheck)
        
        self.runButtonSizer.Add(self.runButton, border=5)
        self.runButtonSizer.Add(self.stopButton, border=5)
        self.sizer.Add(self.runButtonSizer, flag=wx.CENTER|wx.BOTTOM|wx.TOP, border = 15)
        self.sizer.Add(self.generateButton, flag=wx.CENTER, border=5)
        self.sizer.Add(self.gaugeBar, flag=wx.CENTER|wx.TOP, border =30)

        self.border = wx.BoxSizer(wx.VERTICAL)
        self.border.Add(self.sizer, 0, wx.EXPAND|wx.ALL, 8)
        self.SetSizerAndFit(self.border)

    #-----------------------------------------------------------------------------------------------
    def onRadio(self, event):
        radioBox = self.colorRadio
        selected = radioBox.GetSelection()
        if selected == 0: # All
            self.colorAll = True
        else:             # Specific LED
            self.colorAll = False

    def onColorChanged(self, event):
        wx.CallAfter(self.canvas.SetFocus)
        color = self.colorPicker.GetColour()
        self.canvas.selectionCounter +=  1
        #change color of all LEDS
        if self.colorAll:
            for z in range(8):
                for y in range(8):
                    for x in range(8):
                        currentLed = self.canvas.led[z][y][x]
                        currentLed.setFrame(self.selectedFrame,color=(color.Red(),color.Green(), color.Blue(), color.Alpha()))
        #change color of the selected LED
        else:
            currentLed = self.canvas.led[self.canvas.selectedZ][self.canvas.selectedY][self.canvas.selectedX]
            currentLed.setFrame(self.selectedFrame,color=(color.Red(),color.Green(), color.Blue(), color.Alpha()))

        self.canvas.OnDraw()
    def axesCheckBox(self, e):
        self.canvas.Axes(e.Checked())
        self.canvas.OnDraw()
    def onStopButton(self, event):
        self.running = False 
    def onGenerateButton(self, event):
        #setup variables ----------------------------------
        self.generateButton.Disable()
        transitionTime = []
        numItems = self.frameList.GetItemCount()
        startByte = chr(0x7E)

        #get frames and transition time --------------------
        for index in range(numItems):
            transitionTime.append( int(self.frameList.GetItem(index,1).GetText()) )

        ser = serial.Serial('/dev/ttyACM0',9600) #open Arduino port
        ser.write(startByte)
        #ser.write('0');
       # ser.write();
        #start sending bytes -----------------------------
            
        self.generateButton.Enable()

    def onRunButton(self, event):
        #setup variables ----------------------------------
        self.runButton.Disable()
        self.stopButton.Enable()
        self.running = True
        self.gaugeBar.SetValue(0)
        self.gaugeBar.Show()
        self.GetSizer().Layout() 
        numItems = self.frameList.GetItemCount()
        transitionTime = []
        totalTime = 0
        gaugeFactor = 0
        #get frames and transition time --------------------
        for index in range(numItems):
            transitionTime.append( int(self.frameList.GetItem(index,1).GetText())/1000.0 )
            if index != numItems-1:
                totalTime += transitionTime[index]
        if totalTime != 0:
            gaugeFactor= 100.0/totalTime

        #start the simulation -----------------------------
        startTime = time.time()
        for index in range(numItems-1):
            #find transition factor
            for z in range(8):
                for y in range(8):
                    for x in range(8):
                        self.canvas.led[z][y][x].makeColorTransition(index, transitionTime[index])
                
            diffTime = 0
            internalStartTime = time.time()
            while(diffTime < transitionTime[index] and self.running):
                #calculate current color
                for z in range(8):
                    for y in range(8):
                        for x in range(8):
                            currentColor = [0, 0, 0, 255]
                            currentLed = self.canvas.led[z][y][x]
                            for i in range(3):
                                currentColor[i]=currentLed.colorTransitionFactor[i]*diffTime + currentLed.startColor[i]
                            currentLed.simulationColor.Set(currentColor[0], currentColor[1], currentColor[2], currentColor[3])
                #draw the simulation
                wx.Yield()
                self.canvas.onSimulate()
                diffTime = time.time() - internalStartTime
                self.gaugeBar.SetValue(gaugeFactor*(time.time() - startTime))
        
        self.gaugeBar.Hide()
        self.gaugeBar.SetValue(0)
        self.GetSizer().Layout() 
        self.running = False    
        self.stopButton.Disable()
        self.runButton.Enable()
    def onItemSelected(self, event):
        self.selectedFrame = self.frameList.GetFocusedItem()
        self.canvas.OnDraw()
    def onAddFrame(self, event):
        index = self.frameList.GetItemCount()
        nameDialog = wx.TextEntryDialog(self,"Enter frame name:", "Adding a frame", "frame " + str(index+1))
        timeDialog = wx.TextEntryDialog(self, "Enter transition time between this frame and the next(millisecond):", "Adding a frame", "1000")
        if nameDialog.ShowModal() == wx.ID_OK:  
            if timeDialog.ShowModal() == wx.ID_OK:
                self.frameList.InsertStringItem(index, nameDialog.GetValue())
                self.frameList.SetStringItem(index, 1, timeDialog.GetValue())
        for z in range(8):
            for y in range(8):
                for x in range(8):
                    self.canvas.led[z][y][x].addFrame(color=(255,0,0,255))
        timeDialog.Destroy()
        nameDialog.Destroy()
        self.canvas.OnDraw()
    def onRemoveFrame(self, event):
        index = self.frameList.GetFocusedItem()
        self.frameList.DeleteItem(index)
        self.canvas.OnDraw()
    def onEditFrame(self, event):
        index = self.frameList.GetFocusedItem()
        name = self.frameList.GetItem(index,0).GetText()
        time = self.frameList.GetItem(index,1).GetText()
        nameDialog = wx.TextEntryDialog(self,"Enter frame name:", "Adding a frame", name)
        timeDialog = wx.TextEntryDialog(self, "Enter transition time between this frame and the next(millisecond):", "Adding a frame", time)
        if nameDialog.ShowModal() == wx.ID_OK:  
            if timeDialog.ShowModal() == wx.ID_OK:
                self.frameList.SetStringItem(index, 0, nameDialog.GetValue())
                self.frameList.SetStringItem(index, 1, timeDialog.GetValue())
        timeDialog.Destroy()
        nameDialog.Destroy()
                  
#===============================================Main====================================================
class MainWin(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, title='LED cube simulation', *args, **kwargs)

        self.canvas = myGLCanvas(self, size=(840, 480))
        self.panel = ToolPanel(self, canvas=self.canvas)
        self.canvas.setPanel(self.panel)
        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.canvas, 0, wx.EXPAND)
        self.sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizerAndFit(self.sizer)

        self.Show()

#===================================================================================================
app = wx.App(False)
main_win = MainWin(None)
app.MainLoop()
