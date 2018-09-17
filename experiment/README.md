# Antagonistic Shape Memory Alloy Actuators

## General information

This is an interface for the control of antagonistic Shape Memory Alloy (SMA) springs.

### Physical layout

 A number of SMA springs is placed radially and one end from each spring is fixed at a point on the circumferance of a circle. The free-end for all springs is connected at a common node (free to move) near the center of the circle. Actuation of an SMA, via Joule heating, reduces the length of the corresponding spring, as the SMA recovers its original 'memorized' shape. This deformation causes the common node to move from its original position. The goal is to investigate the force magnitudes developed under this antagonistic actuation, for the same trajectories in the plane and the energy consumption for each actuation profile. The position of the common node is given by tracing an infrared LED through a Wiimote. Internal actuator characteristics are given by the SMA model.  
 The Python code is used to establish the connections with external resources (serial interface & bluetooth) and provide the utilities for the position control of the common node in the plane.

The setup uses:

- an infrared LED placed at the common point
- a Wiimote to produce the location of the LED
- arduino UNO boards to produce PWM signals
- shape memory alloy springs

### GUI functionality

The GUI is separated into left and right panes. The left pane uses a Canvas object, below three entries for numeric values and general purpose buttons. The right pane is used to place containers for individual control and information for each SMA spring. These containers are created by the number of springs defined in the initialization file (see below).

- The Canvas:  
it is used to show the position of the LEDs and of the reference point. The plane at which the springs are placed, in the physical world, is defined by four LEDs. These four LEDs are used to calculate the homography matrix (correction between the springs' plane and the camera plane). Since Wiimote traces the position of up to four LEDs, a physical button is used to turn these LEDs on and off. During the initialization, the LEDs are turned on and the homography matrix is calculated by pressing the button `reCalibr` in the GUI. The common point is visible by the black LED displayed in the Canvas. The reference position is also visible in the Canvas by the yellow dot. Its position can be manipulated either by left-clicking in the Canvas, or by setting the coordinates in the entries bellow the Canvas.  
- The Entries:  
time is displayed in (ms) and the loop time is displayed to check the delays from the i/o. The coordinates of the common node are given in the brackets.  
- The Buttons:  
    - `REC_latch`: latches and unlatches the recording of data
	- `REC_demand`: records a single set of data
	- `controller:on`: sets the controller on (for all actuators). The control is decentralized, i.e. each spring has its own controller. The controllers can be disengaged by the individual actuator's control panel in the right pane (button: `rest`). The controller is disengaged when all individual controller have been turned-off  
	- `changeReference`: this begins a cycle for predefined reference points. When the common node reaches each point, the reference point is moved to the next one in the list (hard coded in the class MainWindow(), function initializeVariables()).



## Contents

### Signal flow

1. the `update()` function of the main tkinter window (`class MainWindow()`) coordinates the io-activities
2. the wiimote is connected (asynchronously - via a thread) via bluetooth
3. the control signal, for each SMA, is sent as a separate serial command to the arduino interface
    - the arduino receives the serial command by interrupt and updates the PWM (replies with acknowledgment)

### Other functionalities

- the spring's data are sent to client services connected to the localhost (for the purpose of simulating the individual SMA actuators [pending activity])
- the spring's data are recorded to a file for post-processing
- the spring's physical properties can be changed by interaction with the shell


### Dependencies

developed under Ubuntu - Linux, requires:    

- [cwiid] library (for the connection to Wiimote) and
- openCV (tested under openCV 3.0.0-rc1)

[cwiid]: http://www.abstrakraft.org/cwiid/



## Modules & Classes

- `module createInterface.py`:
    - `class GuiServer`: creates the interface and establishes connections (user initializes available hardware connections)

- `module mainEntities.py`:
    - `class IoManager`: handles the interface to external resources (wii, arduino, file, clients, bash). Uses a thread to interact with Wii & publish data to clients
    - `class MainWindow`: sets up the tkinter window and coordinates the io-activities

- `module springRepo.py`:
    - `class SpringGui`: creates a gui for user-control of each actuator
    - `class SpringEntity`: controls the actuator (uses the classes BasicSpring, Controller & SpringGui):
        - monitors button events (from the user)
        - issues the control signal
        - updates parameter values
    - `class Controller`: produces the controller output

- `module springProperties.py`:
    - `class BasicSpring`: defines the values of the actuator's  properties and the model `[model is pending]`


- `module guiElementariesRepo`: collection of classes for the construction of the gui (entries, labels, buttons, canvas)
- `module ioElementariesRepo`: collection of classes and functions for io
- `module mathElementariesRepo`: collection of functions for math calculations. The coordinates of the LEDs in the physical world are hard coded in function: `calcHomography()`
