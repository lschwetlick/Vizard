from OpenGL import GLUT
from OpenGL import GL
from OpenGL import GLU

import time
import sys
import numpy as np

import mido

import sig_gen as sg
import kaleidoscope as kal

WINW, WINH = 600, 600
win_canvas = np.zeros((WINH, WINW, 3), dtype=np.float32)
W, H = 600, 600
numpix = W * H

updatespeed = 66 # in ms
px_scan_speed = 50#545.5 #px/ms

K_ix = 0
k_n_segments = 1
k_flipped = 0
k_alternate_flipped = 1
kaleidoscopes = [None,
                 kal.Multiscope(k_flipped, W, k_n_segments, k_alternate_flipped),
                 kal.Recurseoscope(k_flipped, W, k_n_segments)]

# K_inv = False
# k_level = 1

rchannel = sg.SignalGenerator(sg.sin, numpix, 1, id="red")
gchannel = sg.SignalGenerator(sg.sin, numpix, 1, id="green")
bchannel = sg.SignalGenerator(sg.sin, numpix, 1, id="blue")

increments = 1

i = 0
pix = np.ones((W * H * 3), dtype=np.float32)

t1 = time.time()


def showBlankScreen():
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT) # Remove everything from screen (i.e. displays all white)


def computePixels():
    global i, pix, t1, updatespeed, px_scan_speed, K_ix, k_n_segments, k_flipped, k_alternate_flipped, win_canvas, WINW, WINH, W, H
    w = W
    h = H
    winw = WINW
    winh = WINH

    # i am at
    n_scanned_px = updatespeed * px_scan_speed

    r = rchannel.get_series(n_scanned_px)
    g = gchannel.get_series(n_scanned_px)
    b = bchannel.get_series(n_scanned_px)

    rgb = np.array([r, g, b]).T.reshape(w, h, 3)
    if K_ix > 0:
        rgb = kaleidoscopes[K_ix].kaleide(rgb)
    # rgb = kal.kaleidoscope_levels(rgb, level=k_level, flipped=K_inv)
    assert rgb.shape == (w, h, 3)
    leftover_w = winw - w
    left = int(leftover_w / 2)
    right = leftover_w - left

    leftover_h = winh - h
    top = int(leftover_h / 2)
    bottom = leftover_h - top

    print(leftover_w, leftover_h, left, top, w, h, winw, winh, (left + w))
    win_canvas = np.zeros((winh, winw, 3), dtype=np.float32)
    win_canvas[top:(top + h), left:(left + w), :] = rgb

    if False:
        if left > 1:
            #print(rgb[:, 0:left, :].shape)
            #print(rgb[:, 0:left:-1, :].shape)
            win_canvas[:, 0:left, :] = rgb[:, 0:left, :][:,::-1,:]
            win_canvas[:, (winw - right):winw, :] = rgb[:, (w - right):w, :][:,::-1,:]
        if top > 1:
            win_canvas[0:top, :, :] = rgb[0:top, :, :][::-1,:,:]
            win_canvas[(winh - bottom):winh, :, :] = rgb[(h - bottom):h, :, :][::-1,:,:]


    
    #rgb = rgb.reshape(-1)
    
    
    GLUT.glutPostRedisplay()
    return win_canvas


def draw():
    global t1, updatespeed, WINW, WINH, W, H
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    pix = computePixels()
    assert pix.shape == (WINH, WINW, 3)
    GL.glDrawPixels(WINW, WINH, GL.GL_RGB, GL.GL_FLOAT, pix.reshape(-1).data)
    GL.glFlush()
    #print(f"flip took {(time.time() - t1)}")
    updatespeed = int(((time.time() - t1)) * 1000)
    t1 = time.time()


def on_motion(x, y):
    global delta_r, delta_b, px_scan_speed
    max_x = 600
    max_delta_r = 3000
    steps = max_delta_r / max_x
    delta_r = steps * x
    #delta_b = steps * y
    
    max_px_scan_speed = 3600
    steps = max_px_scan_speed / max_x
    px_scan_speed = steps * y
    
    # if state == 0:  # Mouse pressed
    #     self.mouseLastPos = np.array([x, y])
    # elif state == 1:
    #     self.mouseLastPos = None

def on_key(key, x, y):
    global wind, px_scan_speed, waveform_r, K_ix, K_inv, increments
    print(key)
    if key == b"q":
        rchannel.freq += increments
        rchannel.print_freq()
    if key == b"a":
        rchannel.freq -= increments
        rchannel.print_freq()
    if key == b"W":
        gchannel.freq += increments
        gchannel.print_freq()
    if key == b"s":
        gchannel.freq -= increments
        gchannel.print_freq()
    if key == b"e":
        bchannel.freq += increments
        bchannel.print_freq()
    if key == b"d":
        bchannel.freq -= increments
        bchannel.print_freq()
    if key == b"r":
        px_scan_speed += increments
        print("px_scan_speed:", px_scan_speed)
    if key == b"f":
        px_scan_speed -= increments
        print("px_scan_speed:", px_scan_speed)

    if key == b"y":
        rchannel.cycle_waveform()
        print("rchannel.waveform:", rchannel.waveform)
    if key == b"x":
        bchannel.cycle_waveform()
        print("bchannel.waveform:", bchannel.waveform)
    if key == b"c":
        gchannel.cycle_waveform()
        print("gchannel.waveform:", gchannel.waveform)
    if key == b"k":
        K_ix += 1
        if K_ix >= len(kaleidoscopes):
            K_ix = 0
        print("Kaleidoscope", K_ix)
    if key == b"l":
        if K_inv:
            K_inv = False
        else:
            K_inv = True
    
    if key == b"1":
        increments = 1
    if key == b"2":
        increments = 10
    if key == b"3":
        increments = 100
    if key == b"4":
        increments = 1000
        
    if key == b"p":
        GLUT.glutDestroyWindow(wind)
        sys.exit(0)


def print_message(message):
    print(message)


def handle_midi(message):
    global wind, rchannel, bchannel, gchannel, px_scan_speed, waveform_r, K_ix, increments, k_n_segments, k_flipped, k_alternate_flipped
    # RED Channel
    if message.control == 0:
        if message.channel == 0:
            rchannel.freq = message.value * increments
            rchannel.print_freq()
        if (message.channel == 1) and (message.value == 0):
            rchannel.cycle_waveform()
            print("rchannel.waveform:", rchannel.waveform)
    # Green Channel
    elif message.control == 1:
        if message.channel == 0:
            gchannel.freq = message.value * increments
            gchannel.print_freq()
        if (message.channel == 1) and (message.value == 0):
            gchannel.cycle_waveform()
            print("gchannel.waveform:", gchannel.waveform)
    # Blue Channel
    elif message.control == 2:
        if message.channel == 0:
            bchannel.freq = message.value * increments
            bchannel.print_freq()
        if (message.channel == 1) and (message.value == 0):
            bchannel.cycle_waveform()
            print("bchannel.waveform:", bchannel.waveform)
    # Scan Speed
    elif message.control == 3:
        if message.channel == 0:
            px_scan_speed = message.value * increments
            print("px_scan_speed:", px_scan_speed)
        elif (message.channel == 1) and (message.value == 0):
            rchannel.state = 0
            bchannel.state = 0
            gchannel.state = 0

    # Kaleidoscope Switcher
    elif message.control == 4:
        if (message.channel == 1) and (message.value == 0):
            K_ix += 1
            if K_ix >= (len(kaleidoscopes)):
                K_ix = 0
            print("Kaleidoscope", K_ix)

    # Kaleidoscope N Elements
    elif message.control == 5:
        if message.channel == 0:
            k_n_segments = int(message.value/12)
            kaleidoscopes[2].n_segments = k_n_segments
            #print(message, k_n_segments)
            kaleidoscopes[1].n_segments = k_n_segments
            print("k_n_segments", k_n_segments)

    # Kaleidoscope Flips
    elif message.control == 6:
        if message.channel == 0:
            k_flipped = int(message.value/17)
            kaleidoscopes[1].flipped = k_flipped
            kaleidoscopes[2].flipped = k_flipped
            print("k_flipped:", k_flipped)

    # Control Increments
    elif message.control == 7:
        if message.channel == 0:
            increments = (int(message.value) * 6) +1
            print("increments:", increments)

    # Kaleidoscope Flips
    elif message.control == 10:
        if message.channel == 0:
            k_alternate_flipped = int(message.value/17)
            kaleidoscopes[1].alternate_flip = k_alternate_flipped
            print("k_alternate_flipped:", k_alternate_flipped)


    else:
        print(message)



port = mido.open_input(callback=handle_midi)
outport = mido.open_output()

ll = [80, 50, 1, 70,
      110, 110, 100, 70,
      120, 120, 100, 120,
      120, 120, 120, 120]
for i in range(15):
    msg = mido.Message('control_change', channel=1, control=i, value=ll[i], time=0)
    outport.send(msg)



def reshape_me(newWidth, newHeight):
    global W, H, numpix, rchannel, bchannel, gchannel, WINW, WINH, win_canvas
    
    WINW, WINH = newWidth, newHeight
    win_canvas = np.zeros((WINW, WINH, 3), dtype=np.float32)
    W, H = newWidth, newHeight
    if W < H:
        H = W
    else:
        W = H
    print(WINW, WINH, W, H)
    numpix = W * H
    rchannel.numpix = numpix
    bchannel.numpix = numpix
    gchannel.numpix = numpix
    GLUT.glutPostRedisplay()
    return None



port.callback = handle_midi

GLUT.glutInit()  # Initialize a glut instance which will allow us to customize our window
GLUT.glutInitDisplayMode(GLUT.GLUT_RGB)  # Set the display mode to be colored
GLUT.glutInitWindowSize(W, H)   # Set the width and height of your window
GLUT.glutInitWindowPosition(0, 0)   # Set the position at which this windows should appear
wind = GLUT.glutCreateWindow("It's the Vizard")  # Give your window a title
GLUT.glutReshapeFunc(reshape_me)
#GLUT.glutMouseFunc(mouseFunc)
#GLUT.glutPassiveMotionFunc(on_motion)
GLUT.glutKeyboardFunc(on_key)
GLUT.glutDisplayFunc(draw)  # Tell OpenGL to call the showScreen method continuously
#GLUT.glutIdleFunc(showScreen)     # Draw any graphics or shapes in the showScreen function at all times
GLUT.glutMainLoop()  # Keeps the window created above displaying/running in a loop