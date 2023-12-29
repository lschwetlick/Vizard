from dataclasses import dataclass, field
from GUI import print_table
import sig_gen as sg
import kaleidoscope as kal
import numpy as np
import json

import os
from midi_controls import MIDIKNOBS

PRESETFILE = "preset_lib.json"
REFLECTIONFILE = "kal_rotations_lib.json"

@dataclass(unsafe_hash=True)
class Parameters:
    '''Class for storing parameters before the Manager adopts them'''
    r_freq: int = 1
    r_state: int = 0
    r_waveform_ix: int = 0
    g_freq: int = 1
    g_state: int = 0
    g_waveform_ix: int = 0
    b_freq: int = 1
    b_state: int = 0
    b_waveform_ix: int = 0

    px_scan_speed: int = 50
    increments: int = 0

    kaleidoscope_ix: int = 0
    k_n_segments: int = 0
    k_flip: int = 1
    k_alternate_flip: int = 1
    k_manual_rot_curr: tuple = (None, None)
    k_manual_rot: tuple = ((120, True), (240, True), (360, True))

    winw: int = 600
    winh: int = 600
    w: int = 600
    h: int = 600

    need_update: tuple = ()

    update_state: bool = False

    current_preset_num: int = 0
    current_refl_num: int = 0

    def __setattr__(self, name, value):
        if name == "need_update":
            self.__dict__["need_update"] = value
        else:
            #print("set", name, value)
            super().__setattr__(name, value)
            self.need_update = self.need_update + (name,)

    @classmethod
    def from_dict(cls, d):
        instance = cls(**d)
        return instance

    def to_dict(self):
        return self.__dict__


class Vizard():
    def __init__(self):
        self.interface_mode = True
        self.debugmode = True
        self.increments = 1
        self.params = Parameters()
        self.w = self.params.w
        self.h = self.params.h
        self.winh = self.params.winh
        self.winw = self.params.winw
        self._numpix = self.params.w * self.params.h
        self.px_scan_speed = int(self.params.px_scan_speed)
        self.waveforms = [sg.sin, sg.square_wave,
                          sg.noise, sg.constant, sg.triangle]

        self.rchannel = sg.SignalGenerator(self.waveforms, self._numpix,
                                           self.params.r_freq, id="red")
        self.gchannel = sg.SignalGenerator(self.waveforms, self._numpix,
                                           self.params.r_freq, id="green")
        self.bchannel = sg.SignalGenerator(self.waveforms, self._numpix,
                                           self.params.r_freq, id="blue")

        self.k_ix = 0
        self.kal1 = kal.Multiscope(self.params.k_flip, self.params.w,
                                   self.params.k_n_segments,
                                   self.params.k_alternate_flip)
        self.kal2 = kal.Recurseoscope(self.params.k_flip, self.params.w,
                                      self.params.k_n_segments)
        self.kal3 = kal.KaleidoscopeMultiMirror(self.params.k_flip,
                                                self.params.w)
        self.kaleidoscopes = [None, self.kal1, self.kal2, self.kal3]
        self.win_canvas = np.empty((self.params.winh, self.params.winw, 3),
                                   dtype=np.float32)
        self.presets = {}
        #self.refl_presets = {}
        self.load_preset_lib()
        self.load_reflection_lib()
        self.extra_message = ""
        self.debug_message = ""
        self.midi_msg_str = ""
        self.error_message = ""

    def load_reflection_lib(self):
        print("Load Reflection Lib")
        with open(REFLECTIONFILE, 'r') as f:
            self.refl_presets = json.load(f)

    def load_reflection_from_preset(self, number):
        self.load_reflection_lib()
        p = self.refl_presets[str(number)]
        p = tuplify(p)
        self.params.k_manual_rot = p
        return f"Loaded Reflections from {number}"

    def load_preset_lib(self):
        print("Load Preset Lib")
        with open(PRESETFILE, 'r') as f:
            self.presets = json.load(f)

    def save_preset_lib(self):
        print("Save Preset Lib")
        with open(PRESETFILE, 'w') as f:
            json.dump(self.presets, f)

    def add_params_as_preset(self, number):
        p = self.params.to_dict().copy()
        p["need_update"] = ()
        print(p)
        self.presets[str(number)] = p
        self.save_preset_lib()
        return f"Added new Preset in {number}"

    def load_params_from_preset(self, number):
        stay_at_n = self.params.current_preset_num
        p = self.presets[str(number)]
        p = tuplify(p)
        print(p)
        self.params = Parameters.from_dict(p)
        update_names = (tuplify(list(self.presets[str(number)].keys())))
        self.params.need_update = update_names
        self.params.update_state = True
        self.params.current_preset_num = stay_at_n
        return f"Loaded Preset from {number}"


    def update_params(self):
        """ Deploys the parameter values to the correct places """
        for name in self.params.need_update:
            match name:
                case "w":
                    self.w = self.params.w
                    self._numpix = self.w * self.h
                    # Signal Generators
                    self.rchannel.numpix = self._numpix
                    self.gchannel.numpix = self._numpix
                    self.bchannel.numpix = self._numpix
                    self.kaleidoscopes[1].full_size = self.params.w
                    self.kaleidoscopes[2].size = self.params.w
                    self.kaleidoscopes[3].size = self.params.w
                case "h":
                    self.h = self.params.h
                    self._numpix = self.w * self.h
                    # Signal Generators
                    self.rchannel.numpix = self._numpix
                    self.gchannel.numpix = self._numpix
                    self.bchannel.numpix = self._numpix
                case "winh":
                    self.winh = self.params.winh
                    print("set", self.winh)
                case "winw":
                    self.winw = self.params.winw
                    print("set", self.winw)
                case "r_freq":
                    self.rchannel.freq = self.params.r_freq
                case "g_freq":
                    self.gchannel.freq = self.params.g_freq
                case "b_freq":
                    self.bchannel.freq =self.params.b_freq
                case "r_waveform_ix":
                    self.rchannel.waveform_ix = self.params.r_waveform_ix
                case "g_waveform_ix":
                    self.gchannel.waveform_ix = self.params.g_waveform_ix
                case "b_waveform_ix":
                    self.bchannel.waveform_ix = self.params.b_waveform_ix
                case "kaleidoscope_ix":
                    self.k_ix = (self.params.kaleidoscope_ix)
                case "k_flip":
                    # the first one is always None
                    for k in self.kaleidoscopes[1:4]:
                        k.flipped = self.params.k_flip
                case "k_alternate_flip":
                    for k in self.kaleidoscopes[1:3]:
                        k.alternate_flip = self.params.k_alternate_flip
                case "k_n_segments":
                    for k in self.kaleidoscopes[1:3]:
                        k.n_segments = self.params.k_n_segments
                case "k_manual_rot":
                    if not len(self.params.k_manual_rot) == 0:
                        self.kaleidoscopes[3].rotations = \
                            [i[0] for i in self.params.k_manual_rot]
                        self.kaleidoscopes[3].rotations_dir = \
                            [i[1] for i in self.params.k_manual_rot]
                    else:
                        self.kaleidoscopes[3].rotations = []
                        self.kaleidoscopes[3].rotations_dir = []
                case _:
                    # in the default case, take the value for name from params
                    # and write it into the manager
                    value = self.params.__getattribute__(name) 
                    self.__setattr__(name, value)


        if self.win_canvas.shape != (self.winh, self.winw, 3):
            self.win_canvas = np.zeros((self.winh, self.winw, 3),
                                       dtype=np.float32)


        if self.params.update_state:
            self.rchannel.state = self.params.r_state
            self.gchannel.state = self.params.g_state
            self.bchannel.state = self.params.b_state
            self.params.update_state = False

        if len(self.params.need_update) != 0:
            if self.interface_mode:
                print_table(MIDIKNOBS, self.params.to_dict(), self.extra_message)
                print("Width, Height: " + str([self.w, self.h,]) +
                      "; Window Size: " + str([self.winw, self.winh]))
                print("Rotations List: " + str(self.params.k_manual_rot))
                print(str(self.error_message))
            if self.debugmode:
                print(self.midi_msg_str)
                print(self.debug_message)
            self.params.need_update = ()

    def get_RGB(self, n_scanned_px):
        r = self.rchannel.get_series(n_scanned_px)
        g = self.gchannel.get_series(n_scanned_px)
        b = self.bchannel.get_series(n_scanned_px)
        rgb = np.array([r, g, b]).T.reshape(self.w, self.h, 3)
        return rgb

    def apply_kaleidoscope(self, rgb):
        if self.k_ix > 0:
            rgb = self.kaleidoscopes[self.k_ix].kaleide(rgb)
        return rgb

    def embed_rgb_in_window(self, rgb):
        leftover_w = self.winw - self.w
        left = int(leftover_w / 2)
        right = leftover_w - left

        leftover_h = self.winh - self.h
        top = int(leftover_h / 2)
        bottom = leftover_h - top

        reflect = False
        if not reflect:
            self.win_canvas[top:(top + self.h),
                            left:(left + self.w), :] = rgb
        else:
            if left > 1:
                # print(rgb[:, 0:left, :].shape)
                # print(rgb[:, 0:left:-1, :].shape)
                self.win_canvas[:, 0:left, :] = rgb[:, 0:left, :][:, ::-1, :]
                self.win_canvas[:, (self.winw - right):self.winw, :] = \
                    rgb[:, (self.w - right):self.w, :][:, ::-1, :]
            if top > 1:
                self.win_canvas[0:top, :, :] = rgb[0:top, :, :][::-1, :, :]
                self.win_canvas[(self.winh - bottom):self.winh, :, :] = \
                    rgb[(self.h - bottom):self.h, :, :][::-1, :, :]
        return self.win_canvas


def tuplify(listything):
    if isinstance(listything, list): return tuple(map(tuplify, listything))
    if isinstance(listything, dict): return {k:tuplify(v) for k,v in listything.items()}
    return listything