from OpenGL import GLUT
from OpenGL import GL
from OpenGL import GLU

from dataclasses import dataclass
import time
import sys
import numpy as np

import mido

import sig_gen as sg
import kaleidoscope as kal
from viz_manager import Parameters, Vizard

VIZ = Vizard()

t1 = time.time()
updatespeed = 66 # in ms

def computePixels():
    global updatespeed, VIZ
    # we copy the correct parameters to the generation classes BETWEEN calculations
    VIZ.update_params()
    # we need to know how long the flips are taking
    n_scanned_px = updatespeed * VIZ.params.px_scan_speed
    # get the signal
    rgb = VIZ.get_RGB(n_scanned_px)
    rgb = VIZ.apply_kaleidoscope(rgb)

    rgb = VIZ.embed_rgb_in_window(rgb)
    GLUT.glutPostRedisplay()
    return rgb


def draw():
    global t1, updatespeed, VIZ
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    pix = computePixels()
    #assert pix.shape == (WINH, WINW, 3)
    GL.glDrawPixels(VIZ._winw, VIZ._winh, GL.GL_RGB, GL.GL_FLOAT, pix.reshape(-1).data)
    GL.glFlush()

    #print(f"flip took {(time.time() - t1)}")
    updatespeed = int(((time.time() - t1)) * 1000)
    t1 = time.time()

def print_message(message):
    print(message)


def handle_midi(message):
    #global wind, rchannel, bchannel, gchannel, px_scan_speed, waveform_r, K_ix, increments, k_n_segments, k_flipped, k_alternate_flipped
    global VIZ
    # RED Channel
    if message.control == 0:
        if message.channel == 0:
            VIZ.params.r_freq = message.value * VIZ.params.increments
            print("rchannel.r_freq:", message.value * VIZ.params.increments)
        if (message.channel == 1) and (message.value == 0):
            VIZ.params.r_waveform_ix += 1
            print("rchannel.waveform:", VIZ.params.r_waveform_ix)

    # Green Channel
    elif message.control == 1:
        if message.channel == 0:
            VIZ.params.g_freq = message.value * VIZ.params.increments
            print("gchannel.gfreq:", message.value * VIZ.params.increments)
        if (message.channel == 1) and (message.value == 0):
            VIZ.params.g_waveform_ix += 1
            print("gchannel.waveform:", VIZ.params.g_waveform_ix)

    # Blue Channel
    elif message.control == 2:
        if message.channel == 0:
            VIZ.params.b_freq = message.value * VIZ.params.increments
            print("bchannel.bfreq:", message.value * VIZ.params.increments)
        if (message.channel == 1) and (message.value == 0):
            VIZ.params.b_waveform_ix += 1
            print("bchannel.waveform:", VIZ.params.b_waveform_ix)
    
    # Scan Speed
    elif message.control == 3:
        if message.channel == 0:
            VIZ.params.px_scan_speed = message.value * VIZ.params.increments
            print("px_scan_speed:", VIZ.params.px_scan_speed)
        elif (message.channel == 1) and (message.value == 0):
            VIZ.params.rstate = 0
            VIZ.params.gstate = 0
            VIZ.params.bstate = 0
            VIZ.params.update_state = True
            print("RESET STATE")

    # Control Increments
    elif message.control == 7:
        if message.channel == 0:
            VIZ.params.increments = (int(message.value) * 6) + 1
            print("increments:", VIZ.params.increments)
            # VIZ.need_update = True


    # Kaleidoscope Switcher
    elif message.control == 4:
        if (message.channel == 1) and (message.value == 0):
            VIZ.params.kaleidoscope_ix = VIZ.params.kaleidoscope_ix + 1
            print("Kaleidoscope", VIZ.params.kaleidoscope_ix)

    # Kaleidoscope N Elements
    elif message.control == 5:
        if message.channel == 0:
            k_n_segments = int(message.value / 12)
            VIZ.params.k_n_segments = k_n_segments
            print("k_n_segments", k_n_segments)

    # Kaleidoscope Flips
    elif message.control == 6:
        if message.channel == 0:
            k_flip = int(message.value / 17)
            VIZ.params.k_flip = k_flip
            print("k_flipped:", k_flip)

    # Kaleidoscope Flips
    elif message.control == 10:
        if message.channel == 0:
            k_alternate_flip = int(message.value / 17)
            VIZ.params.k_alternate_flip = k_alternate_flip
            print("k_alternate_flip:", k_alternate_flip)

    else:
        print(message)


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
    global VIZ

    VIZ.params.winw, VIZ.params.winh = newWidth, newHeight
    VIZ.params.w, VIZ.params.h = newWidth, newHeight
    if VIZ.params.w < VIZ.params.h:
        VIZ.params.h = VIZ.params.w
    else:
        VIZ.params.w = VIZ.params.h
    GLUT.glutPostRedisplay()
    return None






port.callback = handle_midi

GLUT.glutInit()  # Initialize a glut instance which will allow us to customize our window
GLUT.glutInitDisplayMode(GLUT.GLUT_RGB)  # Set the display mode to be colored
GLUT.glutInitWindowSize(VIZ.params.winw, VIZ.params.winh)   # Set the width and height of your window
GLUT.glutInitWindowPosition(0, 0)   # Set the position at which this windows should appear
wind = GLUT.glutCreateWindow("It's the Vizard")  # Give your window a title
GLUT.glutReshapeFunc(reshape_me)
#GLUT.glutMouseFunc(mouseFunc)
#GLUT.glutPassiveMotionFunc(on_motion)
#GLUT.glutKeyboardFunc(on_key)
GLUT.glutDisplayFunc(draw)  # Tell OpenGL to call the showScreen method continuously
#GLUT.glutIdleFunc(showScreen)     # Draw any graphics or shapes in the showScreen function at all times
GLUT.glutMainLoop()  # Keeps the window created above displaying/running in a loop