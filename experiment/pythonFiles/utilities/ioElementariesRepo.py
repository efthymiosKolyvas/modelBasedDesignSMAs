"""
classes & functions for the ioManager:

classes: 
-- Thread for wii
-- Serial for arduino

Functions:
-- getWii --> open wii connection 
-- echo_client --> push message to client
-- echo_server --> make the server (make a thread and give it the queue w/ the data)
-- createServer --> open connection to client
-- emptyQueue
"""

import threading, cwiid, time, Queue, serial
from subprocess import call
from multiprocessing.connection import Listener

############### Thread to get wii Data (IR values)
class ThreadedActivites(threading.Thread):
    def __init__(self, queue, wm):
        """ create a thread for polling & place the data in a queue (the queue is handled by MainWindow.drawLEDs())
        """
        self.queue = queue
        self.wm = wm
        self.wm.rpt_mode = cwiid.RPT_IR
        self._stopevent = threading.Event()
        self._sleepperiod = 0.01
        threading.Thread.__init__(self)

    def run(self):
        """ uncomment the lines to time the polling of wii
        """
        self.myNumber = 0
        # self.showValue, self.storeValue = 0, 0
        while not self._stopevent.isSet():
            self.queue.put(self.wm.state['ir_src']) # ir-List
            #self.showValue = time.time()
            #print("thread loop closes in  %s (ms)" % str(1e3*(self.showValue - self.storeValue)))
            #self.storeValue = self.showValue
            self._stopevent.wait(self._sleepperiod)
    
    def join(self, timeout = None):
        self._stopevent.set()
        threading.Thread.join(self)


###########
class SerialComm(object):
    def __init__(self, addressPath = '/dev/ttyACM0'):
        """ establish the serial connection to the arduino(s)
        """
        self.ser = None
        try:
            # self.ser = serial.Serial('/dev/ttyACM0', 19200, timeout=0)
            #self.ser = serial.Serial('/dev/ttyUSB0', 19200, timeout=0)  # this is redboard sparkfun
            self.ser = serial.Serial(addressPath, 19200, timeout=0)
            time.sleep(3)
            self.ser.flushOutput()
            self.ser.flushInput()    # if it doesn't work... use Arduino serial monitor to flush the read/write buffers
            time.sleep(1)
            print "serial link established"
            self.ser.write(unicode("#1: 1023\r"))
            time.sleep(1)
            reply = self.ser.read(100)
            if reply:
                print reply
        except serial.SerialException, e:
            print "problem with Serial"

    def writeSerial(self, message):
        if self.ser:
            if self.ser.isOpen(): 
                reply = None
                self.ser.write(unicode(message))
                time.sleep(.01)
                reply = self.ser.read(100)
                if reply:
                    print reply
                else:
                    print "set...got nothing instead...."
        else:
            print  message

    def closeSerial(self):
        if self.ser: self.ser.close()



###FUNCTIONS:

def emptyQueue(queue):
    while queue.qsize()>0:
        queue.get()
    queue.task_done()

###
def getWii():
    """ open bluetooth in linux and connect to wii
    """
    try:
        call(["rfkill" , "unblock" , "bluetooth"])
        print  "press 1+2 buttons now..."
        time.sleep(1)
        try:
            wm = cwiid.Wiimote()
            return wm
        except:
            raise SystemExit("...cannot find  wiimote")
    except:
        raise SystemExit("...no-bluetooth")


"""functions to create a server & push spring data to the clients (connected via localhost) (based on a reply from stackoverflow)
 [used in IoManager.__init__()].
"""
def echo_client(conn, q):
    """ push the data from the queue: q through connection: conn & empty the queue from excessive data
    """
    try:
        while True:
            msg = conn.recv()
            rply = q.get()
            while q.qsize()>2:
               q.get()
            conn.send(rply)
    except EOFError:
        print('Connection closed')
    
def echo_server(address, authkey, queue):
    """ create a new thread for each client and a new queue for the client's data
    """
    clientsQueues = queue
    print 'before Listener'
    serv = Listener(address, authkey=authkey)
    while True:
        try:
            print 'before client accept'
            client = serv.accept()
            q = Queue.LifoQueue()
            tt = threading.Thread(target=echo_client, args = (client, q))      # new thread for each client (non-blocking for more clients)
            tt.daemon = True
            clientsQueues.put(q)    # new client's queue is placed here
            tt.start()
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)

def createServer(clientsQueues):
    echo_server(("", 25000), authkey="peekaboo", queue=clientsQueues)
