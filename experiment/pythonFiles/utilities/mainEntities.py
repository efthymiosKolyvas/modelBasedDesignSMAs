""" main Classes:
    - MainWindow
    - IoManager
"""

from __future__ import print_function
from guiElementariesRepo import MakeCanva, EntriesTable, LabelsTable, GenericButtons
from springRepo import SpringEntity
from ioElementariesRepo import ThreadedActivites, SerialComm, getWii, echo_client, echo_server, createServer, emptyQueue
from mathElementariesRepo import  calcDist, calcHomography, fixPointPos, sortLeds, isnumber

import Tkinter as tk
import re, sys, time, select, StringIO, Queue, subprocess
from threading import Thread
from numpy import array, eye, linalg, mod

class MainWindow(object):
    def __init__(self, parent,iomanager,noSprings):
        self.parent = parent
        self.ioman = iomanager
        self.noSprings = noSprings
        self.frameLeft = tk.Frame(self.parent, bg="#000", name="frameleft")
        self.frameLeft.pack(side="left", fill="x")
        self.frameRight = tk.Frame(self.parent, bg="#f66", name="frameright")
        self.frameRight.pack(side="right", fill="y")
        # LEFT side of GUI:_______functionality buttons_________________
        """canvas"""
        self.canvasFrame = tk.Frame(self.frameLeft, background = "black", name = "canvasframe")
        self.canvas = MakeCanva(self.canvasFrame)
        self.canvasFrame.pack(side="top", fill="x")
        """ buttons"""
        self.mainButtonFrame = tk.Frame(self.frameLeft, background = "black", name = "mainButtons")
        self.mainButtonFrame.pack(side="bottom", fill="x")
        self.mainButtons = GenericButtons(self.mainButtonFrame,2,3)
        """ reference & time entries"""
        self.parent.bind("<Button-1>", lambda event: self.canvas.callback(event))
        self.mainEntryFrame = tk.Frame(self.frameLeft, background = "black", name = "mainEntries")
        self.mainEntryFrame.pack(side="bottom", fill="x")
        self.referenceTab = EntriesTable(self.mainEntryFrame, 1,3)
        self.referenceTab.set(0,0, "time \t looptime"), self.referenceTab.set(0,1, "x-position"), self.referenceTab.set(0,2, "y-position")
        self.initializeVariables()
        # RIGHT side of GUI:_________ springs' guis ___________
        colorTable = ["#f66", "Azure", "#bee"];
        for index in range(self.noSprings):
            newframe = tk.Frame(self.frameRight, background = colorTable[index])
            newframe.pack(side="top", fill="x")
            self.springsArray.append(SpringEntity(newframe,str(index+1), colorTable[index], self.ioman))

    def update(self):
        """update leds on Canva and entries in main gui"""
        pointFxd = self.drawLEDs()
        self.updateEntries(pointFxd)
        """advance to next reference point from the list"""
        if self.mainButtons.changeReference:
            self.pointPointer += 1
            self.setReferenceByList()
            self.mainButtons.changeReference = False
        """get referencePoint from Canva or Entry"""
        if not(self.mainButtons.firstRun):
            self.pickReference()
        """interact through shell"""
        self.ioman.getUserInput(self.springsArray)
        """ update springs"""
        for spring in self.springsArray:
            spring.curPostn, spring.reference = pointFxd, self.reference
            if self.mainButtons.controllerOn: spring.controlOn = True
            spring.update(self.dtime)
            if spring.moveToNextRefPoint: self.sprReachedPostn +=1
        self.butterflyControlScheme()
        self.mainButtons.controllerOn = False 
        """push data to clients"""
        publicmsg = []
        for index in range(self.noSprings):
            s = self.springsArray[index]
            publicmsg.append([self.mytime, s.s.force, s.s.delta, 1.0, s.s.th])
        self.ioman.publishtoClients(publicmsg)
        """ write to File"""
        if self.ioman.UseFile:
            packetToWrite = []
            for index in range(self.noSprings):
                s = self.springsArray[index]
                packetToWrite.append([s.duty, s.s.delta, s.s.h, self.mytime, s.curPostn[0], s.curPostn[1], 
                                      self.reference[0], self.reference[1], s.error, index])
            if self.mainButtons.recordDemand and not(self.mainButtons.ToggleLatch):
                self.ioman.recordtoFile(packetToWrite)
                self.mainButtons.recordDemand = False
            if self.mainButtons.ToggleLatch:
                self.ioman.recordtoFile(packetToWrite)

    def initializeVariables(self):
        self.springsArray = []
        self.reference = [0, 0]
        self.homographyMtrx, self.InvhomographyMtrx = [eye(3) for _ in range(2)]
        self.ir = [[] for _ in range(1)]
        self.startTime, self.storeValue, self.dtime = time.time(), time.time(), 0.0
        self.referencePointsLst = [[61.5, 51.0], [61.5, 44.0], [71.0, 48.0]]
        self.sprReachedPostn = 0
        self.pointPointer = -1
        self.inCoolingPeriod, self.waitStartTime = False, 0.0

    def drawLEDs(self):
        points = []
        if self.ioman.UseWii:
            self.ir = self.ioman.que.get()
            emptyQueue(self.ioman.que)
            """you need to sort the Leds to get the Homography matrix (at least-once) or the brighter Led (if not all 4 visible)"""
            for indx, point in enumerate(sortLeds(self.ir)):
                points.append(point[0])
            self.canvas.update(points)
            pointFxd = self.corrPointCoords(points)
        else:
            pointFxd = [-9.9, -9.9]
        return pointFxd
        
    def corrPointCoords(self, points):
        """ update homography matrix if needed"""
        if self.mainButtons.firstRun:
            """ if firstRun or recalibrate (re)calculate the homography matrix"""
            print("points seen are: ", points)
            self.homographyMtrx = calcHomography(points)
            if linalg.cond(self.homographyMtrx) < 1/sys.float_info.epsilon:
                self.InvhomographyMtrx = linalg.inv(self.homographyMtrx)
            else:
                self.InvhomographyMtrx = eye(3)
            self.mainButtons.firstRun = False
            pointFxd = [-9.9, -9.9]
        else:
            pointFxd = fixPointPos(self.homographyMtrx, points).tolist()[0]
        return pointFxd

    def butterflyControlScheme(self):
        """ when all spring errors<0.1, the position has been reached; start the cooling period (disable all controls & start timer)
        when the cooling period ends, update the reference position and activate the controllers
        """
        if not(self.inCoolingPeriod) and self.sprReachedPostn == 3:
            self.waitStartTime, self.inCoolingPeriod = self.mytime, True
            for spring in self.springsArray:
                spring.gui.ButtonsTab.resetSpring = True
        if self.inCoolingPeriod and (self.mytime>self.waitStartTime+0.0):
            self.changeReferenceFnc()
            for spring in self.springsArray:
                spring.controlOn = True
            self.inCoolingPeriod = False
        self.sprReachedPostn = 0 
    
    def setReferenceByList(self):
        pointer = int(self.pointPointer % 3)
        self.referenceTab.set(0,1, self.referencePointsLst[pointer][0])
        self.referenceTab.set(0,2, self.referencePointsLst[pointer][1])

    def changeReferenceFnc(self):
        self.pointPointer += 1
        self.setReferenceByList()
        if not(mod(self.pointPointer, 3)): subprocess.call(["spd-say", "loop complete"])
        
    def pickReference(self):
        """get reference either from canvas or the entries and update each other
        self.reference is in Real world Coords, self.canvas.reference is in Canvas Coords"""
        if isnumber(self.referenceTab.get(0,1)) & isnumber(self.referenceTab.get(0,2)):
            if self.reference != [float(self.referenceTab.get(0,1)), float(self.referenceTab.get(0,2))]:
                print(self.reference, [float(self.referenceTab.get(0,1)), float(self.referenceTab.get(0,2))])
                self.reference = [float(self.referenceTab.get(0,1)), float(self.referenceTab.get(0,2))]
                referencePxls = fixPointPos(self.InvhomographyMtrx,[self.reference]).tolist()[0]
                self.canvas.canvas.coords(self.canvas._elements[-1], referencePxls[0], referencePxls[1], 
                                          referencePxls[0]+4, referencePxls[1]+4)
        if self.canvas.referencePoint != []:
            self.reference = fixPointPos(self.homographyMtrx,[self.canvas.referencePoint]).tolist()[0]
            self.reference = [round(item,2)  for item  in self.reference]
            self.referenceTab.set(0,1, self.reference[0]), self.referenceTab.set(0,2, self.reference[1])
            self.canvas.referencePoint = []

    def updateEntries(self, pointFxd):
        self.dtime = self.updateTime()
        self.referenceTab.set(0,0,'[{0:4.1f},{1:4.1f}] \t {2:07.2f} \t {3:04.1f}'.
                              format(pointFxd[0], pointFxd[1], self.mytime, self.dtime))

    def updateTime(self):
        self.mytime = time.time() - self.startTime
        self.showValue = time.time() - self.startTime
        timeDiff = round(1e3*(self.showValue - self.storeValue),2)
        self.storeValue = self.mytime
        return timeDiff






class IoManager(object):
    def __init__(self, **kwargs):
        """ serve connections to external resources: [wii, arduino, write to file, clients, bash]
        """
        self.UseWii = kwargs.get("UseWii", False)
        self.UseSerial = kwargs.get("UseSerial", False)
        self.UseFile = kwargs.get("UseFile", False)
        self.PublishData = kwargs.get("PublishData", False)
        self.noSprings = kwargs.get("noSprings", 2)
        "--wii_init::"
        if self.UseWii: 
            self.que = Queue.LifoQueue()
            self.t = ThreadedActivites(self.que, getWii())
            self.t.start()
        "--client_init for spring simulation plotter::"
        if self.PublishData:
            self.clientsQueue = Queue.Queue()
            self.l = Thread(target=createServer, name='publishingThread', args = (self.clientsQueue, ))
            self.l.daemon = True
            self.l.start()
        "-- serial_init::"
        addresses, self.serialConnectionsList =  ['/dev/ttyACM0', '/dev/ttyUSB0'], []
        if self.UseSerial:
            if self.noSprings==3:
                for item in addresses:
                    self.serialConnectionsList.append(SerialComm(item))
            else:
                self.serialConnectionsList.append(SerialComm())
        "--initialize file::"
        if self.UseFile:
            print("fileName: dataCollection_")
            piece_together = raw_input('-->')
            """ StringIO makes a copy in the memory, actual file is written during mainWindow closing-see self.closingCleanup() (if the process is killed from the terminal, all data is lost)"""
            self.vFile = StringIO.StringIO()
            self.filePath = '~/Documents/data/dataCollection_' + piece_together + '.txt'
            with open(self.filePath, 'w') as overwriteFile:
                print("duty, deformation, h*1e3, time, cposX, cposY, referenceX, referenceY, error, index \n", file=overwriteFile)
        else:
            self.filePath, self.vFile = None, None

    def closingCleanup(self, addDataToWrite):
        if self.UseWii: self.t.join()
        if self.UseSerial:
            for connection in self.serialConnectionsList:
                connection.closeSerial()
        if self.filePath:
            with open(self.filePath, 'a') as outfile:
                outfile.write(self.vFile.getvalue())
                for itemToWrite in addDataToWrite:
                    itemMtrx = np.array(itemToWrite)
                    print(itemMtrx)
                    itemMtrx.tofile(outfile, sep="\t", format="%f")
                    print("\t\t", file=outfile)
            self.vFile.close()

    def getUserInput(self, springLib):
        r""" set or recover a spring property for the user via shell -- check the regular expression for the format of the command"""
        flag=False
        while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            if line:
                setSpringValue = re.findall("@" +r"(\s*\d\s*)" + "::"+r"(\s*[a-zA-Z]+\d*[a-zA-Z]*\s*=\s*[+-]*\d+.*\d*)", line)
                requestSpringValue = re.findall("&" +r"(\s*\d\s*)" + "::"+r"(\s*[a-zA-Z]+\d*[a-zA-Z]*)", line)
                if setSpringValue:
                    a, = setSpringValue
                    springNo = int(a[0])-1
                    if springNo > len(springLib)-1: break
                    xx = re.split("=", a[1])
                    attributeFound, value = [item.strip() for item in xx]
                    if  springLib[springNo].s.__dict__.has_key(attributeFound):
                        springLib[springNo].s.__dict__[attributeFound]=float(value)
                        print("s:{0:1d}:{1:s} set.".format(springNo, attributeFound))
                        flag=True
                if requestSpringValue:
                    b, = requestSpringValue
                    springNo, attributeSought = int(b[0])-1, b[1].strip()
                    if springNo > len(springLib)-1: break
                    if  springLib[springNo].s.__dict__.has_key(attributeSought):
                        print(springLib[springNo].s.__dict__[attributeSought])
                    else:
                        print("no value for: %s" % attributeSought)
            else: # an empty line means stdin has been closed
                print('eof')
                exit(0)
                return flag

    def publishtoClients(self, publicmsg):
        """ update the queues of the clients w/ the data in the publicmsg ([client side is pending])
        """
        remakeList = []
        while not self.clientsQueue.empty():
            innerQueue = self.clientsQueue.get()   # remember this is a queue of queues (each client has each own queue)
            innerQueue.put(publicmsg)
            remakeList.append(innerQueue)      # this is measured data: time - deformation - current
        for item in remakeList:
            self.clientsQueue.put(item)

    def recordtoFile(self, packetToWrite):
        for packet in packetToWrite:
            duty, deformation, h, time, cposX, cposY, referenceX, referenceY, error, index = packet
            self.vFile.write("{0:6.1f} \t {1:5.2f} \t {2:5.2f} \t {3:9.3f} \t {4:5.1f} \t {5:5.1f} \t {6:5.1f} \t {7:5.1f} \t {8:6.2f} \t {9:1d} \n".
                             format(duty, deformation, h, time, cposX, cposY, referenceX, referenceY, error, index))


    def writeSerial(self, serialID, message):
        if self.UseSerial:
            self.serialConnectionsList[serialID].writeSerial(message)
