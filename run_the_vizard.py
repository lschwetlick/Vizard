from OpenGL import GLUT
from OpenGL import GL

import time
import os

import mido

from viz_manager import Vizard
import prettytable

import keyboard
import midi_controls
from GUI import print_table

VIZ = Vizard()
T1 = time.time()
UPDATESPEED = 66  # in ms


def computePixels():
    global UPDATESPEED, VIZ
    # we copy the correct parameters to the generation classes BETWEEN
    # calculations
    VIZ.update_params()
    # we need to know how long the flips are taking
    n_scanned_px = UPDATESPEED * VIZ.px_scan_speed
    # get the signal
    rgb = VIZ.get_RGB(n_scanned_px)
    rgb = VIZ.apply_kaleidoscope(rgb)
    #rgb = VIZ.embed_rgb_in_window(rgb)
    GLUT.glutPostRedisplay()
    return rgb


def draw():
    global T1, UPDATESPEED, VIZ
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    pix = computePixels()
    # assert pix.shape == (WINH, WINW, 3)
    #pix_uint8 = (pix * 256).astype('uint8')
    GL.glDrawPixels(VIZ.winw, VIZ.winh, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, pix.data)
    GL.glFlush()

    # print(f"flip took {(time.time() - T1)}")
    UPDATESPEED = int(((time.time() - T1)) * 1000)
    T1 = time.time()


def handle_midi(message):
    global VIZ, OUTPORT
    VIZ.midi_msg_str = "time: " + str(time.time())[:10] + " " + str(message)
    try:
        dial = message.control
        value = message.value
        # TURN EVENTS
        if message.channel == 0:
            # blocks any accidental turn events during a click
            if not midi_controls.MIDIKNOBS[dial].isclicked:
                # update internal representation of knobs
                keyboard.PSEUDOKNOBS[dial].value = value
                midi_controls.MIDIKNOBS[dial].value = value
                # execute turn function
                try:
                    VIZ = midi_controls.MIDIKNOBS[dial].turn(VIZ)
                except Exception as X:
                    print(X)

        current_turn_value = midi_controls.MIDIKNOBS[dial].value
        # CLICK IN EVENTS
        if (message.channel == 1) and (message.value == 127):
            # register click in time for longclick detection
            midi_controls.MIDIKNOBS[dial].click_in()
            midi_controls.MIDIKNOBS[dial].isclicked = True
        # RELEASE EVENTS
        if (message.channel == 1) and (message.value == 0):
            midi_controls.MIDIKNOBS[dial].isclicked = False
            if midi_controls.MIDIKNOBS[dial].is_longclick():
                midi_controls.MIDIKNOBS[dial].longclick_out(VIZ)
            else:
                midi_controls.MIDIKNOBS[dial].click_out(VIZ)
            print_table(midi_controls.MIDIKNOBS, VIZ.params.to_dict(), "CLICK")

        # logic for register changes
        if midi_controls.MIDIKNOBS[dial].value != current_turn_value:
            msg = mido.Message('control_change', channel=0, control=dial,
                               value=midi_controls.MIDIKNOBS[dial].value,
                               time=0)
            OUTPORT.send(msg)
    except Exception as X:
        VIZ.error_msg = X


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


def send_dataclass_to_midi(outport, params, PSEUDOKNOBS):
    print("sending midi")
    for chan in midi_controls.MIDIKNOBS.keys():
        name = midi_controls.MIDIKNOBS[chan].turn_var
        if name != "":
            if name == "k_manual_rot_curr":
                val = 0
            else:
                val = int(params.__dict__[name])

            if outport != "kb_only":
                # send value
                msg = mido.Message('control_change', channel=0, control=chan,
                                   value=val, time=0)
                outport.send(msg)
            PSEUDOKNOBS[chan].value = val
        if outport != "kb_only":
            # send col
            col = midi_controls.MIDIKNOBS[chan].color
            msg = mido.Message('control_change', channel=1, control=chan,
                               value=col, time=0)
            outport.send(msg)


def on_key(key, x, y):
    global VIZ, OUTPORT
    if key in keyboard.KEYSMAP.keys():
        keyboard.KEYSMAP[key][1]()
        msg = keyboard.KEYSMAP[key][0]()
        handle_midi(msg)
        send_dataclass_to_midi(OUTPORT, VIZ.params, keyboard.PSEUDOKNOBS)


try:
    INPORT = mido.open_input('Midi Fighter Twister', callback=handle_midi)
    OUTPORT = mido.open_output('Midi Fighter Twister')

    print(VIZ.params)
    INPORT.callback = handle_midi
except OSError:
    print("MIDI not available. Use Keyboard!")
    OUTPORT = "kb_only"

send_dataclass_to_midi(OUTPORT, VIZ.params, keyboard.PSEUDOKNOBS)


# Initialize a glut instance which will allow us to customize our window
GLUT.glutInit()
# Set the display mode to be colored
GLUT.glutInitDisplayMode(GLUT.GLUT_RGB)
# Set the width and height of your window
GLUT.glutInitWindowSize(VIZ.params.winw, VIZ.params.winh)
# Set the position at which this windows should appear
GLUT.glutInitWindowPosition(0, 0)
# Give your window a title
wind = GLUT.glutCreateWindow("It's the Vizard")
GLUT.glutReshapeFunc(reshape_me)
# GLUT.glutMouseFunc(mouseFunc)
# GLUT.glutPassiveMotionFunc(on_motion)
GLUT.glutKeyboardFunc(on_key)
# Tell OpenGL to call the showScreen method continuously
GLUT.glutDisplayFunc(draw)
# Keeps the window created above displaying/running in a loop
GLUT.glutMainLoop()
