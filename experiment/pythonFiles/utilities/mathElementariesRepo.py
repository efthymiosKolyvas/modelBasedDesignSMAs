""" collection of the math-related functions:
    - calcDist()
    - calcHomography()
    - fixPointPos()
    - sortLeds()
    - isnumber()
"""

import numpy as np
import cv2

def calcDist(points):
    return np.linalg.norm(np.array(points[0]) - np.array(points[1]))

def calcHomography(pointsIR):
    """ associates the physical distances between the four LEDs on the board with the identified light sources as returned by Wiimote
    order of LEDs matters on the position of the origin (see also sortLeds() )
    """
    ptsreal = np.array([[0.0, 0.0], [131.0, 0.0], [0.0, 94.0], [131.0, 94.0]], dtype = 'float32') 
    # sequence is circular:: top left--top right--botm left -- bottom right
    matrix = cv2.getPerspectiveTransform(np.array(pointsIR, dtype = 'float32'), ptsreal)
    return matrix

def fixPointPos(matrix, points):
    """ apply the homography correction """
    ptsreal = np.array([points], dtype = 'float32')
    pointsFxd = cv2.perspectiveTransform(ptsreal, matrix)
    return pointsFxd[0]

def sortLeds(ledsQueue, screenWidth=570, screenHeight=350):
    ''' scale the LEDs from the camera resolution (1024 x 768) to canvas size (570 x 350)
    sort the leds returned from Wii according to their position: first is: min(x), min(y) 
    note: depends on the physical installation of the Wiimote w/ respect to the LED board & the setup of the origin during the calculation of the Homography matrix (see calcHomography() )
    remember to use 0.0 floats during the scaling division
    '''
    leds = [[led['pos'], led['size']] for led in ledsQueue if led]  # this is: [size, [x, y]]
    if len(leds)!=4:
        sortBiSz = leds[:]
        sortBiSz.sort(key=lambda x: x[1], reverse=True)
        scaled = [[[screenWidth*i[0][0]/1024.0, screenHeight*i[0][1]/768.0], i[1]] for i in sortBiSz]
        fixedLeds = [[[-i[0][0]+screenWidth, i[0][1]], i[1]] for i in scaled]
    else:
        scaled = [[[screenWidth*i[0][0]/1024.0, screenHeight*i[0][1]/768.0], i[1]] for i in leds]
        mirrored = scaled[:]
        mirrored = [[[-i[0][0]+screenWidth, i[0][1]], i[1]] for i in mirrored]
        mirrored.sort(key=lambda x: x[0][1])
        lefties, righties = mirrored[:2], mirrored[2:]
        fixedLeds = sorted(lefties, key=lambda x: x[0][0]) + sorted(righties, key=lambda x: x[0][0])
    return fixedLeds

def isnumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
