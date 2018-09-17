""" collection of the Classes for the construction of the gui:
    - MakeCanva
    - EntriesTable
    - LabelsTable
    - Buttons General table (the layout)
        -individual buttons: buttons in the main gui
        -individual buttons: buttons for each spring
"""
import Tkinter as tk
import tkFont


class MakeCanva(object):
    """canvas is used to plot the position of the LEDs as returned by wii & (set/plot) the reference point: 4x LEDs (for calculation of homography) + reference
    """
    def __init__(self, parent):
        self.parent = parent
        self.canvas = tk.Canvas(self.parent, width = 570, height = 350,
                                bg = "#eee", scrollregion=(0,0,100,200), name="thisiscanvas")
        self.canvas.pack()
        colours = ["black", "red", "green", "blue", "#ff0"]
        self._elements = []
        for colour in colours:
            self._elements.append(self.canvas.create_oval(0, 0, 4, 4, fill = colour, outline = "white"))
        self.referencePoint = []

    def update(self, points):
        points = points
        """ this is padding of the list `points', for the cases where wii returns < 4 values"""
        if len(points) < 4:
            a = 4 - len(points)
            for i in range(a):
                points.append([0, 0])
        for indx, _  in enumerate(self._elements[0:4]):
            self.canvas.coords(self._elements[indx], points[indx][0], points[indx][1], 
                               points[indx][0]+5, points[indx][1]+5)

    def callback(self,event):
        """capture the `click on canvas' event & get coordinates for the new reference point
        """
        if str(event.widget) == ".frameleft.canvasframe.thisiscanvas":
            self.referencePoint = [event.x-6, event.y-8]
            self.canvas.coords(self._elements[-1], event.x-6, event.y-8, 
                                          event.x+5-6, event.y+5-8)


class EntriesTable(object):
    """ make a table of entries; indexing is by [row][column]
    """
    def __init__(self, parent, rows=1, columns=1):
        self.parent = parent
        self._entries, self._entryVars = [], []
        for row in range(rows):
            current_row_entry, current_row_vars = [], []
            for column in range(columns):
                setfocus =1
                variable = tk.StringVar()
                entry = tk.Entry(self.parent, textvariable=variable, 
                                 borderwidth=0, width=8, font=tkFont.Font(size=9, weight=tkFont.BOLD), justify="right", takefocus=setfocus, background="gray39", foreground="white")
                entry.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row_entry.append(entry)
                current_row_vars.append(variable)
            self._entries.append(current_row_entry)
            self._entryVars.append(current_row_vars)
        for column in range(columns):
            self.parent.grid_columnconfigure(column, weight=1)

    def set(self, row, column, value):
        self._entryVars[row][column].set(value)

    def get(self, row, column):
        return self._entryVars[row][column].get()


class LabelsTable(object):
    """ make a table of labels (based on: http://stackoverflow.com/questions/11047803/creating-a-table-look-a-like-tkinter)
    """
    def __init__(self, parent, rows=3, columns=2):
        self.parent = parent
        self._widgets = []
        boldFont = tkFont.Font(weight=tkFont.BOLD, size=9)
        normalFont = tkFont.Font(weight=tkFont.NORMAL, size=10)
        for row in range(rows):
            current_row = []
            for column in range(columns):
                selection = boldFont
                label = tk.Label(self.parent, text="%s/%s" % (row, column), 
                                 borderwidth=0, width=10, font = selection)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)
        for column in range(columns):
            self.parent.grid_columnconfigure(column, weight=1)

    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

    def get(self, row, column):
        widget = self._widgets[row][column]
        return widget["text"]


class MakeAbuttonsTable(object):
    def __init__(self, parent, rows=1, columns=1,**kwargs):
        """ basic structure for buttons' table, inhereted for generic and spring tables
        """
        self.parent = parent
        self.buttonnames = kwargs.get('names', [["unnamedButton" for _ in range(columns)]])
        self.functionsLibrary = kwargs.get('functions', [[self.empty_fun for _ in range(columns)]])
        self._buttons = []
        for indxR, row in enumerate(range(rows)):
            current_row=[]
            for indxC,column in enumerate(range(columns)):
                butt = tk.Button(self.parent, text=self.buttonnames[indxR][indxC], relief = "raised", 
                                 borderwidth=0, width=6, height=1, font=tkFont.Font(size=9, weight=tkFont.BOLD), takefocus=1, background="#eee")
                butt.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                butt.bind("<Return>", lambda event, parameter = [0, row, column]: 
                          self.buttonClick(event, parameter))
                butt.bind("<space>", lambda event, parameter = [1, row, column]: 
                          self.buttonClick(event, parameter))
                butt.bind("<ButtonPress-1>", lambda event, parameter = [2, row, column]: 
                          self.buttonClick(event, parameter))
                current_row.append(butt)
            self._buttons.append(current_row)
        for column in range(columns):
            self.parent.grid_columnconfigure(column, weight=1)

    def buttonClick(self,event, parameter):
        try:
            self.functionsLibrary[parameter[1]][parameter[2]](parameter)
            if parameter[0] == 3:
                self._buttons[parameter[1]][parameter[2]].configure(relief='sunken')
                self._buttons[parameter[1]][parameter[2]].flash()
                self._buttons[parameter[1]][parameter[2]].configure(relief='solid')
        except IndexError:
            print "function non-existent"

    def empty_fun(self, parameter):
        print "..there is nothing here.."



class GenericButtons(MakeAbuttonsTable):
    def __init__(self, parent, rows=1, columns=1,**kwargs):
        """ make buttons for the main gui: the callback functions set flags to be handled by the MainWindow & SpringEntity classes
        """
        self.buttonnames = [[" ", "REC_latch", "reCalbr"], ["controller:on", " REC_demand", "changeReference"]]
        self.functionsLibrary = [[self.empty_fun, self.recordLatch_fun, self.recalibrate_fun], 
                        [self.controllerOn_fun, self.recordDemand_fun, self.changeReference_fun]]
        self.ToggleLatch, self.recordDemand, self.controllerOn, self.changeReference = [False for _ in range(4)]
        self.firstRun = kwargs.get('firstRun', True)
        MakeAbuttonsTable.__init__(self, parent, rows, columns, names=self.buttonnames, functions=self.functionsLibrary)

    def empty_fun(self, parameter):
        print "..there is nothing here.."

    def recalibrate_fun(self, parameter):
        self.firstRun = True
        print "this is recalibrate"

    def recordDemand_fun(self, parameter):
        self.recordDemand = True

    def recordLatch_fun(self, parameter):
        self.ToggleLatch = not(self.ToggleLatch)
        if self.ToggleLatch:
            self._buttons[0][1].configure(bg="#eaa")
            print "Record Latch is __ON__"
        else:
            self._buttons[0][1].configure(bg="#eee")
            print "Record Latch is __OFF__"

    def controllerOn_fun(self, parameter):
        self.controllerOn = True
        print "controller(s):: ON"

    def changeReference_fun(self, parameter):
        self.changeReference = True
        print "referencePointUpdated"



class SpringButtons(MakeAbuttonsTable):
    def __init__(self, parent, rows=2, columns=1, **kwargs):
        """make the buttons for the individual spring's interface
        """
        self.buttonsNames = kwargs.get("names", [["set"], ["reset"]])
        self.functionsLibrary = kwargs.get("functions", [[self.setSpring], [self.resetSpring], [self.setZeroPoint_fun], [self.applyDuty_fun]])
        MakeAbuttonsTable.__init__(self, parent, rows, columns, names=self.buttonsNames, functions=self.functionsLibrary)
        self.setZeroPoint, self.setSpring, self.resetSpring, self.applyDuty = [False for _ in range(4)]

    def setZeroPoint_fun(self, parameter):
        self.setZeroPoint = True
        print "IC:: Set"

    def setSpring(self,parameter):
        self.resetSpring = False
        self.setSpring = True

    def resetSpring(self,parameter):
        self.setSpring = False
        self.resetSpring = True

    def applyDuty_fun(self,parameter):
        self.applyDuty = True

    def emptyFun(self,parameter):
        print "empty function"
        pass
