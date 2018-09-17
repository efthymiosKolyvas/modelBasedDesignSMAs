""" contents: 
--------------
class SpringEntity(object):
class SpringGui(object):
class BangBangController(object):
class ConvertDuty(object):
class AnalogController(object):
"""

from __future__ import print_function

import Tkinter as tk
import numpy as np
from math import copysign, sqrt

from guiElementariesRepo import EntriesTable, LabelsTable, SpringButtons
from mathElementariesRepo import isnumber, calcDist
from springProperties import BasicSpring


class SpringEntity(object):
    def __init__(self, parent, springID, backColor, iomangr):
        """ the antagonistic springs are controlled in a decentralized scheme; as a result each spring has its own gui, controller and state-simulator [pending]
        serial communication and gui-update are handled from here
        """
        self.ioman = iomangr
        self.serialNo = springID
        self.controlOn, self.moveToNextRefPoint = False, False
        self.curPostn, self.reference, self.refPostn, self.ZeroPoint = [[] for _ in range(4)]
        self.duty, self.prevSentDuty, self.error, self.totalResistance = 1023, 1023, 0.0, 1.8
        self.cRMS, self.irms, self.ssDuty, self.rmsList = 0.0, 0.0, 1023, [0.0 for _ in range(10)]
        # self.Qmatrx = [[-9.5, 46.0], [55.0, 86.0], [57.5, 10.5]]    # coordinates of anchor points for springs
        self.Qmatrx = [[20.70, 46.50], [85.64, 84.00], [85.65, 9.00]]    # coordinates of anchor points for springs

        self.s = BasicSpring()
        self.gui = SpringGui(parent, backColor,self.serialNo)
        self.dutyConverter = ConvertDuty(self.s.rho)
        self.controller = AnalogController(self.dutyConverter)

    def update(self, dtime):
        self.calcErrorDeformation()
        self.produceThetaH()
        if self.gui.ButtonsTab.setSpring or self.gui.ButtonsTab.resetSpring:
            """ priority to manual buttons (disable controller) """
            if self.controlOn: self.controlOn = False
            self.serveButtons()
            self.displayDutyTocurrent()
            self.calcRMS()
            self.registerControl()
            self.moveToNextRefPoint = False
        elif self.controlOn:
            if self.gui.ButtonsTab.applyDuty == True:
                """ stop bang-bang, apply the rms of the control signal (used when reference position is reached)"""
                self.duty =int(self.ssDuty)
                self.gui.ButtonsTab.applyDuty, self.controlOn = False, False
                print("{0:s}: {1:s}".format(str(self.serialNo), "dutyFixed"))
                self.moveToNextRefPoint = False
            else:
                controllerGains = [self.gui.EntriesTab.get(3,0), self.gui.EntriesTab.get(4,0), self.gui.EntriesTab.get(5,0)]
                controllerGains = [float(x) if isnumber(x) else 0.0 for x in controllerGains]
                self.duty = int(self.controller.update(self.error, controllerGains, dtime))
                self.displayDutyTocurrent()
                self.calcRMS()
                self.moveToNextRefPoint = True if abs(self.error) <= 0.1 else False
            self.registerControl()

    def serveButtons(self):
        """ duty is updated via the Class variable `duty' """
        if self.gui.ButtonsTab.setSpring:
            duty = self.gui.EntriesTab.get(0,0) if isnumber(self.gui.EntriesTab.get(0,0)) else str(1023) # type(duty) == string
            duty = str(max(0, min(1023, int(duty))))
            print("{0:s}: {1:s}".format(str(self.serialNo), duty))
            self.duty = int(float(duty))
            self.gui.ButtonsTab.setSpring = False
        elif self.gui.ButtonsTab.resetSpring:
            print("{0:s}: 1023".format(str(self.serialNo)))
            self.duty = 1023
            self.gui.ButtonsTab.resetSpring = False

    def displayDutyTocurrent(self):
        self.irms, vref = self.dutyConverter.toRMS(self.duty)
        self.gui.LabelsTab.set(0,1,round(self.irms,2))
        self.gui.LabelsTab.set(1,1,round(vref,2))  # voltage on reference resistance of voltage divider

    def calcErrorDeformation(self):        
        self.s.delta = calcDist([self.Qmatrx[int(self.serialNo)-1], self.curPostn]).tolist() - 23.0  # length of crimping equipment == 23.0
        self.error = calcDist([self.Qmatrx[int(self.serialNo)-1], self.curPostn]).tolist() - calcDist([self.Qmatrx[int(self.serialNo)-1], self.reference]).tolist()   # this way it is signed
        self.gui.LabelsTab.set(3,1,round(self.s.delta, 2));  self.gui.LabelsTab.set(4,1,round(self.error, 2))

    def produceThetaH(self):
        """ estimate final temperature, based on input current; the value of the heat convection coefficient is a parametric expression with respect to the spring-pitch & (el. current)^2 
        """
        if not(self.s.pitchManual):  # in case you want to trim the pitch value
            self.s.pitch = self.s.delta/self.s.n 
        heatConvCoef, = self.s.hFunc(self.s.pitch, self.irms**2)[0]    #returns a numpy.array 2D
        ssTemp = self.s.tinf + ((self.irms**2)*self.s.rho/heatConvCoef)
        self.s.h = heatConvCoef*1e3
        self.gui.LabelsTab.set(2,1, "{0:05.1f}::{1:4.2f}".format(ssTemp, heatConvCoef*1e3))

    def registerControl(self):
        self.gui.EntriesTab.set(0,0, str(self.duty)) 
        if self.duty != self.prevSentDuty:
            springSerial = max(1, int(self.serialNo) % 3)
            message = "#" + str(springSerial) + ": "+ str(self.duty) +"\r"
            serialID = 1 if int(self.serialNo)==3 else 0
            self.ioman.writeSerial(serialID, message)
        self.prevSentDuty = self.duty

    def calcRMS(self):
        """ takes the RMS value of the 'continuous' waveform (pulse train)"""
        samplesNumber = int(float(self.gui.EntriesTab.get(1,0))) if isnumber(self.gui.EntriesTab.get(1,0)) else 1e1
        samplesNumber = samplesNumber if samplesNumber>=1e1 else 1e1
        self.rmsList.insert(0, self.irms)
        while len(self.rmsList) >= samplesNumber:
            self.rmsList.pop()
        self.cRMS = sqrt(sum([item**2 for item in self.rmsList])/len(self.rmsList))
        self.ssDuty = int(1023*(1-(self.cRMS*self.totalResistance/3.4)**2))
        self.gui.LabelsTab.set(5,1,round(self.cRMS,2)); self.gui.EntriesTab.set(2,0,self.ssDuty)
        

class AnalogController(object):
    def __init__(self, dutyConverter):
        """ this is a pi w/ saturation on the input
        """
        self.dutyConverter = dutyConverter
        self.pGain, self.iGain  = 190.0, 0.0
        self.errorCutOff = 0.18
        self.sum_i, self.error_1, self.i_error_1 = [0.0 for _ in range(3)]
        
    def update(self, error, controllerGains, dtime):
        [self.pGain, self.iGain, self.errorCutOff] = [gain for gain in controllerGains]
        if (self.iGain==0.0) or (error<0.0):
            self.sum_i = 0.0
            self.error_1 = 0.0
        else:
            self.sum_i += error

        error = min(self.errorCutOff, max(0.0, error))    # saturator at controller input
        pSignal = self.pGain*error # error (mm) --> ampere**2
        iSignal = self.iGain*self.sum_i

        controlSignal = sum([pSignal, iSignal])
        controlSqrt = sqrt(controlSignal)
        duty = self.dutyConverter.toDuty(controlSqrt)
        duty = max(duty, 490)   # software current limiter (it should be reduntant for appropriate value of self.errorCutOff)
        self.error_1 = error
        return duty

    
class ConvertDuty(object):
    def __init__(self, spring_rho):
        """ conversions duty <--> current: 
        current through the spring and voltage across the voltage divider (used for verification)
        """
        self.Vp, self.dividerResistance = 3.4, 1.4
        self.totalResistance =  self.dividerResistance + spring_rho

    def toRMS(self, duty):
        truermsV = self.Vp*sqrt((1023.0 - duty)/1023.0)
        truermsC = truermsV/self.totalResistance if self.totalResistance != 0 else 999.9
        DC_true = self.Vp*(1023.0 - duty)/1023.0
        voltXdivider = self.dividerResistance*DC_true/self.totalResistance # common multimeters record the dc-component
        return truermsC, voltXdivider

    def toDuty(self, currentValue):
        voltageValue = currentValue*self.totalResistance
        duty = 1023.0 - 1023.0*((voltageValue/self.Vp)**2)
        return duty


class BangBangController(object):
    def __init__(self):
        pass

    def update(self, error):
        """ this is inverted pwm: 1023 --> 0 Amps: 
        if error >= 0: duty = 1023, else: duty = 640
        """
        duty = 1023 - max(0, copysign(433, -error))
        return duty


class SpringGui(object):
    def __init__(self, parent, backColor,serialNo):
        """ create an interface w/ a few buttons, indicators and entries for each spring (individual control)
        """
        self.parent = parent
        self.frameLabels = tk.Frame(self.parent, background=backColor)
        self.frameEntries = tk.Frame(self.parent, background=backColor)
        self.frameButtons = tk.Frame(self.parent, background=backColor)
        self.EntriesTab = EntriesTable(self.frameEntries,6,1)
        self.LabelsTab = LabelsTable(self.frameLabels, 6,3)
        """ electrical data: current and voltage across voltage divider"""
        self.LabelsTab.set(0,0,"rms(A)"), self.LabelsTab.set(1,0,"(V) on resDiv"),
        """ spring data: steady-state temperature, estimation of heat convection coefficient, deformation and error from reference point"""
        self.LabelsTab.set(2,0,"ssT-H"), self.LabelsTab.set(3,0,"delta"), self.LabelsTab.set(4,0,"error")
        self.LabelsTab.set(0,1,"-9"), self.LabelsTab.set(1,1,"-9"), self.LabelsTab.set(2,1,"-9"), self.LabelsTab.set(3,1,"-9"), self.LabelsTab.set(4,1,"-9")
        self.LabelsTab.set(0,2,"duty"), 
        self.LabelsTab.set(1,2,"noSamples"), self.LabelsTab.set(2,2,"ssDuty"), 
        self.LabelsTab.set(3,2,"pGain"), self.LabelsTab.set(4,2,"iGain"),
        self.LabelsTab.set(5,0,"Irms"), self.LabelsTab.set(5,2,"errorCutOff")

        self.EntriesTab.set(0,0,1023), self.EntriesTab.set(1,0,6e2), 
        self.EntriesTab.set(2,0,-9.9), self.EntriesTab.set(3,0,190), 
        self.EntriesTab.set(4,0,0.0), self.EntriesTab.set(5,0,0.18)

        self.ButtonsTab = SpringButtons(self.frameButtons,4,1, names=[
            ["set::"+ serialNo], ["rest::"+serialNo], ["setZero::"+serialNo], ["applyDuty::"+serialNo]])
        self.frameLabels.pack(side="left", fill="x")
        self.frameButtons.pack(side="right", fill="x")
        self.frameEntries.pack(side="right", fill="x")

    def set(self, row,column,value):
        self.LabelsTab.set(row,column,str(value))
    def get(self, row, column):
        return self.EntriesTab.get(row,column)
    def setEntries(self, row,column,value):
        self.EntriesTab.set(row,column,str(value))
