from OpenGL import GLUT
from OpenGL import GL

import time
import os

import mido

from viz_manager import Vizard, MAPPING_turn, MAPPING_click, k_rot_map
import prettytable

import keyboard


VIZ = Vizard()
T1 = time.time()
UPDATESPEED = 66  # in ms
LAST8CLICK = 0


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

    rgb = VIZ.embed_rgb_in_window(rgb)
    GLUT.glutPostRedisplay()
    return rgb


def draw():
    global T1, UPDATESPEED, VIZ
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    pix = computePixels()
    # assert pix.shape == (WINH, WINW, 3)
    GL.glDrawPixels(VIZ._winw, VIZ._winh, GL.GL_RGB, GL.GL_FLOAT,
                    pix.reshape(-1).data)
    GL.glFlush()

    # print(f"flip took {(time.time() - T1)}")
    UPDATESPEED = int(((time.time() - T1)) * 1000)
    T1 = time.time()


def handle_midi(message):
    global VIZ, a1, OUTPORT, LAST8CLICK

    dial = message.control
    value = message.value
    keyboard.PSEUDOKNOBS[dial].value = value
    extra_message = "Extra"
    # turn events
    if message.channel == 0:
        print("turn")
        name = MAPPING_turn[dial][0]
        if MAPPING_turn[dial][1] == "k_manual_rot_curr":
            value = k_rot_map(int(value))
            name = "k_manual_rot_curr"
        print("set", name, value)
        VIZ.params.__setattr__(name, value)
    
    #press in events
    if (message.channel == 1) and (message.value == 127):
        print("press")
        if MAPPING_click[dial][1] == "k_manual_rot":
            LAST8CLICK = time.time()

    # release events
    if (message.channel == 1) and (message.value == 0):
        extra_message = f"regclick,, {VIZ.params.current_preset_num}"
        print("release", extra_message)
        name = MAPPING_click[dial][0]
        print(f"release {name}")
        if name == "Preset_load":
            thispreset = VIZ.params.current_preset_num
            print(f" loading {thispreset}")
            try:
                extra_message = \
                    VIZ.load_params_from_preset(thispreset)
            except Exception as e:
                print(f"Could not load Preset {thispreset}")
                print(e)
                raise
            send_dataclass_to_midi(OUTPORT, VIZ.params)
        elif name == "Preset_save":
            try:
                extra_message = \
                    VIZ.add_params_as_preset(VIZ.params.current_preset_num)
            except:
                print(f"Could not save Preset {thispreset}")
                raise
        elif name == "k_manual_rot":
            now = time.time()
            extra_message = f"Deleting Rotations {now - LAST8CLICK}"
            if ((now - LAST8CLICK) > 2) & ((now - LAST8CLICK) < 10):
                VIZ.params.k_manual_rot = ()
            else:
                VIZ.params.k_manual_rot = \
                    VIZ.params.k_manual_rot + (VIZ.params.k_manual_rot_curr,)
        elif name == "update_state":
            MAPPING_click[dial][1](VIZ.params)
        else:
            val = VIZ.params.__getattribute__(name) + 1
            VIZ.params.__setattr__(name, val)


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
    for chan in MAPPING_turn.keys():
        name = MAPPING_turn[chan][0]
        if name != "":
            if MAPPING_turn[chan][1] == "inc":
                pass
                #val = int(params.__dict__[name] / params.increments)
                val = 0
            elif type(MAPPING_turn[chan][1]) == int:
                val = params.__dict__[name] * MAPPING_turn[chan][1]
            elif MAPPING_turn[chan][1] == "*6+1":
                val = VIZ.increments#int((params.__dict__[name] / 6) - 1)
            elif MAPPING_turn[chan][1] == "preset":
                val = int(params.__dict__[name])
            if outport != "kb_only":
                # send value
                msg = mido.Message('control_change', channel=0, control=chan,
                                   value=val, time=0)
                outport.send(msg)
            PSEUDOKNOBS[chan].value = val
        if outport != "kb_only":
            # send col
            col = MAPPING_turn[chan][2]
            msg = mido.Message('control_change', channel=1, control=chan,
                               value=col, time=0)
            outport.send(msg)


def on_key(key, x, y):
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
