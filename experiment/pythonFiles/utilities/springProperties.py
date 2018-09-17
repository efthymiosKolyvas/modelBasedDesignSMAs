""" summary of spring properties, SMA spring model & simulation [pending]
"""
from __future__ import print_function
import numpy as np
from scipy import interpolate

class BasicSpring(object):
    """ lexicon of the spring properties
    """
    def __init__(self, **kwargs):
        self.d = kwargs.get("d", .51)                 # wire diameter, units: (mm)
        self.D = kwargs.get("D", 3.45)              # spring diameter, units: (mm)
        self.n = kwargs.get("n", 8.0)                 # number of active-coils
        self.delta = kwargs.get("delta", 0)        # deformation, units:  (mm)
        self.pitch = kwargs.get("pitch", 0.0)   # coil-to-coil distance, units: (mm)
        self.force = kwargs.get("force", 0)        # units: (gr)

        self.hFunc = self.buildHsurf()
        self.h, = self.hFunc(self.pitch, 0.0)[0]       # hFunc(pitchValue, irms**2)
        self.rho = kwargs.get("rho", 0.35)         # units: (Ohm)
        self.cv = kwargs.get("cv", 0.1155)          # heat capacity in (J/K)

        self.tinf = kwargs.get("tinf", 18.0)         # environmental temperature
        self.th = kwargs.get("th", 0.0)             # material temperature (assumes the normalization th = thRecorded-tinf)
        self.thp = kwargs.get("thp", self.th)      # this is previous temperature

        self.Lo = kwargs.get("Lo", self.n*self.pitch + self.d)  # free length (no load) in (m)
        if not(self.Lo == self.n*self.pitch + self.d):
            self.pitch = (self.Lo - self.d)/self.n
            print("{0:s}: {1:s}".format("setting Lo sets spring.pitch to", str(self.pitch)))
        self.pitchManual = kwargs.get("pitchManual", False)    # enables to set the pitch manually from the mainFunction

        self.alpha = np.arctan(self.pitch/(np.pi*self.D))  # pitch/coil angle
        self.Lw = np.pi*self.D*(self.n/np.cos(self.alpha))  # wire length
        self.solid = (self.n+1)*self.d  # solid length (fully compressed)
        self.C = self.D/self.d # spring index

    def buildHsurf(self):
        """ build the interpolation function for the parametrization of the heat convection coefficient
        """
        p00 = 2.261; p10 = 3.879; p01 = 0.5832; p20 = -2.035; p11 = 0.6178; p02 = 0.1431
        yDataMm = np.array([0, 3.0]); xDataMm = np.array([0.1, 1.1])   # pitch, irms**2
        noPoints = 7e1
        xgrd = np.linspace(xDataMm[0], xDataMm[1], noPoints )
        ygrd = np.linspace(yDataMm[0], yDataMm[1], noPoints )
        [x, y] = np.meshgrid (xgrd, ygrd)        
        h = p00 + p10*x + p01*y + p20*x**2 + p11*x*y + p02*y**2
        hFunc = interpolate.RectBivariateSpline(ygrd, xgrd, h*1e-3)  # swapping of the x, y arguments is intentional: 
        return hFunc  # call it by hFunc(pitchValue, irms**2)

    def temperatureEstimation(self, args, ts=0.01, initialCondition=0):
        """args::(time, current (A)), ts:: sampling time, initialCondition (temperature, w/o tinf)
        args = [[tinit, tfin], input]
        """
        [ydd, tdd] =  self.__iterateDiscrete(args=args, ts=ts, initialCondition=initialCondition)
        return ydd, tdd
    
    def __iterateDiscrete(self, args, ts=0.01, initialCondition=0):
        ydd = []
        ti, qi = args    # time, input (raw - don't square)
        tdd = np.linspace(ti[0], ti[-1], (ti[-1]-ti[0])/ts +1)     # format time according to discretization step
        """update non-constant material parameters"""
        if not(self.pitchManual):
            self.pitch = self.delta/self.n
        self.h, = self.hFunc(qi[-1]**2, self.pitch)[0]
        q, p = self.rho/self.cv,  self.h/self.cv
        """discretize (ZOH)"""
        bz = q/p*(1- np.exp(-p*ts));            
        az = -np.exp(-p*ts);
        """simulate"""
        ydd.insert(0, initialCondition)
        for index, t in enumerate(tdd):
            newValue = bz*(qi**2) - az*ydd[index]
            ydd.insert(index+1, newValue)
        ydd.pop()
        self.thp = self.th
        self.th = ydd[-1]
        return ydd, tdd           #  add enironmental temperature before display


    
if __name__ == "__main__":
    
    b = BasicSpring(E = 1e1)
    if 1:
        # print("{}".format([a for a in dir(b) if not a.startswith('__')]))
        for key, value in b.__dict__.items():
            if not key.startswith('__'):
                print("{}\t {}".format(key, value))
