from dataclasses import dataclass, field
import sig_gen as sg
import kaleidoscope as kal
import numpy as np
import json
import prettytable
import os

PRESETFILE = "preset_lib.json"


def reset_states(p):
    p.r_state = 0
    p.g_state = 0
    p.b_state = 0
    p.update_state = True


MAPPING_turn = {
    0: ("r_freq", "inc", 80, "Red [q]"),
    1: ("g_freq", "inc", 50, "Green [w]"),
    2: ("b_freq", "inc", 1, "Blue [e]"),
    3: ("px_scan_speed", "inc", 70, "Scan [r]"),
    4: ("", "", 110, "Kal"),
    5: ("k_n_segments", 12, 110, "Segments"),
    6: ("k_flip", 17, 100, "Flip"),
    7: ("increments", "*6+1", 70, "increments"),
    8: ("k_manual_rot_curr", "k_manual_rot_curr", 120, "Kal Rotation"),
    9: ("", "", 120, ""),
    10: ("k_alternate_flip", 17, 100, "Flip 2"),
    11: ("", "", 120, ""),
    12: ("", "", 1, ""),
    13: ("", "", 1, ""),
    14: ("", "", 60, ""),
    15: ("current_preset_num", "preset", 60, "Preset")
}

MAPPING_click = {
    0: ("r_waveform_ix", 1, 80),
    1: ("g_waveform_ix", 1, 50),
    2: ("b_waveform_ix", 1, 1),
    3: ("update_state", reset_states, 70),
    4: ("kaleidoscope_ix", 1, 120),
    5: ("", "", 120),
    6: ("", "", 120),
    7: ("", "", 120),
    8: ("k_manual_rot", "k_manual_rot", 120),
    9: ("", "", 120),
    10: ("", "", 120),
    11: ("", "", 120),
    12: ("", "", 120),
    13: ("", "", 120),
    14: ("Preset_save", "save", 60),
    15: ("Preset_load", "load", 60)
}


def k_rot_map(value):
    # value = int(value/2)
    if value < 74:
        return (value * 5, True)
    else:
        return ((value - 74) * 5, False)


@dataclass(unsafe_hash=True)
class Parameters:
    '''Class for keeping track of an item in inventory.'''
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
    k_manual_rot_curr: tuple = ()
    k_manual_rot: tuple = ((120, True), (240, True), (360, True))

    winw: int = 600
    winh: int = 600
    w: int = 600
    h: int = 600

    need_update: tuple = ()

    update_state: bool = False

    current_preset_num: int = 0

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
        self.interface_mode = False
        self.increments = 1
        self.params = Parameters()
        self._w = self.params.w
        self._h = self.params.h
        self._winh = self.params.winh
        self._winw = self.params.winw
        self._numpix = self.params.w * self.params.h
        self.px_scan_speed = int(self.params.px_scan_speed)

        self.waveforms_names = ["sin", "square", "noise",
                                "constant", "triangle"]
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
        self.kal_names = ["None", "Multiscope", "Recurseoscope", "NEW"]

        self.win_canvas = np.empty((self.params.winh, self.params.winw, 3),
                                   dtype=np.float32)
        self.presets = {}
        self.load_preset_lib()
        
        self.extra_message = ""

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
        for name in self.params.need_update:
            match name:
                case "w":
                    self._w = self.params.w
                    self._numpix = self._w * self._h
                    # Signal Generators
                    self.rchannel.numpix = self._numpix
                    self.gchannel.numpix = self._numpix
                    self.bchannel.numpix = self._numpix
                    self.kaleidoscopes[1].full_size = self.params.w
                    self.kaleidoscopes[2].size = self.params.w
                    self.kaleidoscopes[3].size = self.params.w
                case "h":
                    self._h = self.params.h
                    self._numpix = self._w * self._h
                    # Signal Generators
                    self.rchannel.numpix = self._numpix
                    self.gchannel.numpix = self._numpix
                    self.bchannel.numpix = self._numpix
                case "_winh":
                    self._winh = self.params.winh
                case "_winw":
                    self._winw = self.params.winw
                case "increments":
                    self.increments = int((self.params.increments * 6) + 1)
                case "px_scan_speed":
                    self.px_scan_speed = int(self.params.px_scan_speed * self.increments)
                case "r_freq":
                    self.rchannel.freq = int(self.params.r_freq * self.increments)
                case "g_freq":
                    self.gchannel.freq = int(self.params.g_freq * self.increments)
                case "b_freq":
                    self.bchannel.freq = int(self.params.b_freq * self.increments)
                case "r_waveform_ix":
                    self.rchannel.waveform_ix = (self.params.r_waveform_ix) % len(self.waveforms)  #  click
                case "g_waveform_ix":
                    self.gchannel.waveform_ix = (self.params.g_waveform_ix) % len(self.waveforms)  #  click
                case "b_waveform_ix":
                    self.bchannel.waveform_ix = (self.params.b_waveform_ix) % len(self.waveforms)  #  click
                case "kaleidoscope_ix":
                    self.k_ix = (self.params.kaleidoscope_ix) % len(self.kaleidoscopes)  #  click
                case "k_flip":
                    self.kaleidoscopes[1].flipped = int(self.params.k_flip / 17)
                    self.kaleidoscopes[2].flipped = int(self.params.k_flip / 17)
                    self.kaleidoscopes[3].flipped = int(self.params.k_flip / 17)
                case "k_alternate_flip":
                    self.kaleidoscopes[1].alternate_flip = int(self.params.k_alternate_flip / 17)
                    self.kaleidoscopes[2].alternate_flip = int(self.params.k_alternate_flip / 17)
                case "k_n_segments":
                    self.kaleidoscopes[1].n_segments = int(self.params.k_n_segments / 12)
                    self.kaleidoscopes[2].n_segments = int(self.params.k_n_segments / 12)
                case "k_manual_rot":
                    if not len(self.params.k_manual_rot) == 0:
                        self.kaleidoscopes[3].rotations = \
                            [i[0] for i in self.params.k_manual_rot]
                        self.kaleidoscopes[3].rotations_dir = \
                            [i[1] for i in self.params.k_manual_rot]
                    else:
                        self.kaleidoscopes[3].rotations = []
                        self.kaleidoscopes[3].rotations_dir = []

        #    if len(self.params.k_manual_rot) \
        #           != len(self.kaleidoscopes[3].rotations):
        #self.params.r_waveform_ix = self.rchannel.waveform_ix
        #self.params.g_waveform_ix = self.gchannel.waveform_ix
        #self.params.v_waveform_ix = self.bchannel.waveform_ix
        #self.params.kaleidoscope_ix = self.k_ix
        if self.win_canvas.shape != (self.params.winh,
                                    self.params.winw, 3):
            self.win_canvas = \
                np.zeros((self.params.winh, self.params.winw, 3),
                        dtype=np.float32)


        if self.params.update_state:
            self.rchannel.state = self.params.r_state
            self.gchannel.state = self.params.g_state
            self.bchannel.state = self.params.b_state
            self.params.update_state = False

        if len(self.params.need_update) != 0:
            self.print_table()
            print(self.extra_message)
            self.params.need_update = ()

    def print_table(self):
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
                r.append(self.VIZfind(MAPPING_turn[(i * 4) + j][0]))
            tab.add_row(r)
            r = []
            for j in range(4):
                r.append(self.VIZfind(MAPPING_click[(i * 4) + j][0]))
            tab.add_row(r)
        if self.interface_mode:
            os.system('clear')
            print(tab)
            print(f"K Man Rot {self.params.k_manual_rot}")

    def VIZfind(self, name):
        if name == "":
            return ""
        elif name == "kaleidoscope_ix":
            return self.kal_names[self.k_ix]
        elif name == "r_waveform_ix":
            return self.waveforms_names[self.rchannel.waveform_ix]
        elif name == "g_waveform_ix":
            return self.waveforms_names[self.gchannel.waveform_ix]
        elif name == "b_waveform_ix":
            return self.waveforms_names[self.bchannel.waveform_ix]
        elif name == "r_freq":
            return self.rchannel.freq
        elif name == "g_freq":
            return self.gchannel.freq
        elif name == "b_freq":
            return self.bchannel.freq
        elif name == "px_scan_speed":
            return self.px_scan_speed
        elif name == "k_n_segments":
            return self.kaleidoscopes[1].n_segments
        elif name == "k_flip":
            return self.kaleidoscopes[1].flipped
        elif name == "k_alternate_flip":
            return self.kaleidoscopes[1].alternate_flip
        elif name == "increments":
            return self.increments
        elif name == "Preset_save":
            return "Save"
        elif name == "Preset_load":
            return "Load"
        elif name == "k_manual_rot":
            return self.params.k_manual_rot_curr
        else:
            return self.params.__dict__[name]


    def get_RGB(self, n_scanned_px):
        r = self.rchannel.get_series(n_scanned_px)
        g = self.gchannel.get_series(n_scanned_px)
        b = self.bchannel.get_series(n_scanned_px)
        rgb = np.array([r, g, b]).T.reshape(self._w, self._h, 3)
        return rgb

    def apply_kaleidoscope(self, rgb):
        if self.k_ix > 0:
            rgb = self.kaleidoscopes[self.k_ix].kaleide(rgb)
        return rgb

    def embed_rgb_in_window(self, rgb):
        leftover_w = self._winw - self._w
        left = int(leftover_w / 2)
        right = leftover_w - left

        leftover_h = self._winh - self._h
        top = int(leftover_h / 2)
        bottom = leftover_h - top

        reflect = False
        if not reflect:
            self.win_canvas[top:(top + self._h),
                            left:(left + self._w), :] = rgb
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