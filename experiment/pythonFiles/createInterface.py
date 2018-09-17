"""
setup connections by ioManager and create the main interface

- set the variables `UseWii, UseSerial, UseFile' to 0,1 depending on the hardware connections on the system
- set the variable `nosprings'
"""

from utilities.mainEntities import MainWindow, IoManager
import Tkinter as tk

class GuiServer(object):
    def __init__(self,iom,noSprings):
        """ set outer tkinter window and assign keyboard shortcuts
        """
        self.iom = iom
        self.root = tk.Tk()
        self.gui = MainWindow(parent=self.root, iomanager=iom, noSprings = noSprings)
        shortKeys = [["q", "a"], ["w", "s"], ["e", "d"]]
        if noSprings >= 1:
            self.root.bind(shortKeys[0][0], lambda event, parameter = [3, 0, 0]:
                           self.gui.springsArray[0].gui.ButtonsTab.buttonClick(event, parameter))
            self.root.bind(shortKeys[0][1], lambda event, parameter = [3, 1, 0]: 
                           self.gui.springsArray[0].gui.ButtonsTab.buttonClick(event, parameter))
        if noSprings >= 2:
            self.root.bind(shortKeys[1][0], lambda event, parameter = [3, 0, 0]:
                           self.gui.springsArray[1].gui.ButtonsTab.buttonClick(event, parameter))
            self.root.bind(shortKeys[1][1], lambda event, parameter = [3, 1, 0]: 
                           self.gui.springsArray[1].gui.ButtonsTab.buttonClick(event, parameter))
        if noSprings >= 3:
            self.root.bind(shortKeys[2][0], lambda event, parameter = [3, 0, 0]:
                           self.gui.springsArray[2].gui.ButtonsTab.buttonClick(event, parameter))
            self.root.bind(shortKeys[2][1], lambda event, parameter = [3, 1, 0]: 
                           self.gui.springsArray[2].gui.ButtonsTab.buttonClick(event, parameter))

    def update(self):
        self.gui.update()
        self.root.after(7, self.update)

    def run(self):
        self.root.after(1, self.update)
        self.root.mainloop()
        self.iom.closingCleanup(self.gui.homographyMtrx)

        

if __name__ == "__main__":

    UseWii, UseSerial, UseFile = 0, 0, 0
    PublishData = True
    nosprings = 3

    ioman = IoManager(UseWii=UseWii, UseSerial=UseSerial, UseFile=UseFile, PublishData=PublishData, noSprings=nosprings)
    springApp = GuiServer(ioman,nosprings).run()

    if 0: call(["rfkill" , "block" , "bluetooth"])   # (optional) close bluetooth on exit
    print "exittted"
