from OpenGL import GLUT
from OpenGL import GL

import time
import os

import mido

from viz_manager import Vizard, MAPPING_turn, MAPPING_click, k_rot_map
import prettytable

import keyboard


VIZ = Vizard()

t1 = time.time()
updatespeed = 66  # in ms
last8click = 0


def computePixels():
    global updatespeed, VIZ
    # we copy the correct parameters to the generation classes BETWEEN
    # calculations
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
    # assert pix.shape == (WINH, WINW, 3)
    GL.glDrawPixels(VIZ._winw, VIZ._winh, GL.GL_RGB, GL.GL_FLOAT,
                    pix.reshape(-1).data)
    GL.glFlush()

    # print(f"flip took {(time.time() - t1)}")
    updatespeed = int(((time.time() - t1)) * 1000)
    t1 = time.time()


def handle_midi(message):
    global VIZ, a1, OUTPORT, last8click

    dial = message.control
    value = message.value
    keyboard.PSEUDOKNOBS[dial].value = value
    extra_message = "Extra"
    if message.channel == 0:
        name = MAPPING_turn[dial][0]
        if MAPPING_turn[dial][1] == "inc":
            value = int(value * VIZ.params.increments)
        elif type(MAPPING_turn[dial][1]) == int:
            value = int(value / MAPPING_turn[dial][1])
        elif MAPPING_turn[dial][1] == "*6+1":
            value = int((value * 6) + 1)
        elif MAPPING_turn[dial][1] == "preset":
            value = int(value)
        elif MAPPING_turn[dial][1] == "k_manual_rot_curr":
            value = k_rot_map(int(value))
            name = "k_manual_rot_curr"

        VIZ.params.__setattr__(name, value)
        

    elif (message.channel == 1) and (message.value == 127):
        if MAPPING_click[dial][1] == "k_manual_rot":
            last8click = time.time()

    elif (message.channel == 1) and (message.value == 0):
        extra_message = f"regclick,, {VIZ.params.current_preset_num}"
        name = MAPPING_click[dial][0]
        if type(MAPPING_click[dial][1]) == int:
            value = (VIZ.params.__dict__[name]
                     + MAPPING_click[dial][1]) % len(VIZ.waveforms)
            VIZ.params.__setattr__(name, value)
        elif MAPPING_click[dial][1] == "load":
            extra_message = \
                VIZ.load_params_from_preset(VIZ.params.current_preset_num)
            send_dataclass_to_midi(OUTPORT, VIZ.params)
        elif MAPPING_click[dial][1] == "save":
            extra_message = \
                VIZ.add_params_as_preset(VIZ.params.current_preset_num)
        elif MAPPING_click[dial][1] == "k_manual_rot":
            now = time.time()
            extra_message = f"hello {now - last8click}"
            if ((now - last8click) > 2) & ((now - last8click) < 10):
                VIZ.params.k_manual_rot = ()
            else:
                VIZ.params.k_manual_rot = \
                    VIZ.params.k_manual_rot + (VIZ.params.k_manual_rot_curr,)
        else:
            MAPPING_click[dial][1](VIZ.params)

    if VIZ.interface_mode:
        print_table(VIZ)
    print(message)
    print(f"K Man Rot {VIZ.params.k_manual_rot}")
    print(extra_message)


def VIZfind(name):
    global VIZ
    if name == "":
        return ""
    elif name == "kaleidoscope_ix":
        return VIZ.kal_names[VIZ.params.__dict__[name]]
    elif name[2:6] == "wave":
        return VIZ.waveforms_names[VIZ.params.__dict__[name]]
    elif name == "Preset_save":
        return "Save"
    elif name == "Preset_load":
        return "Load"
    elif name == "k_manual_rot":
        return VIZ.params.k_manual_rot_curr
    else:
        return VIZ.params.__dict__[name]


def print_table(VIZ):
    # Color
    R = "\033[0;31;40m"  # RED
    # G = "\033[0;32;40m"  # GREEN
    # Y = "\033[0;33;40m"  # Yellow
    # B = "\033[0;34;40m"  # Blue
    N = "\033[0m"  # Reset
    tab = prettytable.PrettyTable()
    tab.hrules = 1
    tab.header = False

    for i in range(4):
        r = []
        for j in range(4):
            r.append(R + MAPPING_turn[(i * 4) + j][3] + N)
        tab.add_row(r)
        r = []
        for j in range(4):
            r.append(VIZfind(MAPPING_turn[(i * 4) + j][0]))
        tab.add_row(r)
        r = []
        for j in range(4):
            r.append(VIZfind(MAPPING_click[(i * 4) + j][0]))
        tab.add_row(r)
    if VIZ.interface_mode:
        os.system('clear')
        print(tab)


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
                val = int(params.__dict__[name] / params.increments)
            elif type(MAPPING_turn[chan][1]) == int:
                val = params.__dict__[name] * MAPPING_turn[chan][1]
            elif MAPPING_turn[chan][1] == "*6+1":
                val = int((params.__dict__[name] / 6) - 1)
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


# print(VIZ.presets["0"])
# print(Parameters().to_dict())
# aa = Parameters.from_dict(Parameters().to_dict())
# print(aa)


def on_key(key, x, y):
    if key in keyboard.KEYSMAP.keys():
        keyboard.KEYSMAP[key][1]()
        msg = keyboard.KEYSMAP[key][0]()
        handle_midi(msg)
        send_dataclass_to_midi(OUTPORT, VIZ.params, keyboard.PSEUDOKNOBS)


try:
    port = mido.open_input('Midi Fighter Twister', callback=handle_midi)
    OUTPORT = mido.open_output('Midi Fighter Twister')

    print(VIZ.params)
    port.callback = handle_midi
except OSError:
    print("MIDI not available. Use Keyboard!")
    OUTPORT = "kb_only"

send_dataclass_to_midi(OUTPORT, VIZ.params, keyboard.PSEUDOKNOBS)

print_table(VIZ)


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
