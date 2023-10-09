from dataclasses import dataclass
import sig_gen as sg
import kaleidoscope as kal
import numpy as np
import json

PRESETFILE = "preset_lib.json"


def reset_states(p):
    p.r_state = 0
    p.g_state = 0
    p.b_state = 0
    p.update_state = True


MAPPING_turn = {
    0: ("r_freq", "inc", 80, "Red"),
    1: ("g_freq", "inc", 50, "Green"),
    2: ("b_freq", "inc", 1, "Blue"),
    3: ("px_scan_speed", "inc", 70, "Scan"),
    4: ("", "", 110, "Kal"),
    5: ("k_n_segments", 12, 110, "Segments"),
    6: ("k_flip", 17, 100, "Flip"),
    7: ("increments", "*6+1", 70, "increments"),
    8: ("k_manual_rot_curr", "k_manual_rot_curr", 120, ""),
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
    #value = int(value/2)
    if value < 37:
        return (value * 10, True)
    else:
        return ((value - 37) * 10, False)


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
    increments: int = 1

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

    need_update: bool = False
    update_state: bool = False

    current_preset_num: int = 0

    def __setattr__(self, name, value):
        if name == "need_update":
            self.__dict__["need_update"] = value
        else:
            super().__setattr__(name, value)
            self.need_update = True

    @classmethod
    def from_dict(cls, d):
        instance = cls(**d)
        return instance

    def to_dict(self):
        return self.__dict__


class Vizard():
    def __init__(self):
        self.params = Parameters()
        self._w = self.params.w
        self._h = self.params.h
        self._winh = self.params.winh
        self._winw = self.params.winw
        self._numpix = self.params.w * self.params.h

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

        self._k_ix = 0
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

    @property
    def k_ix(self):
        return(self._k_ix)

    @k_ix.setter
    def k_ix(self, k_ix):
        self._k_ix = k_ix % (len(self.kaleidoscopes))
        self.params.kaleidoscope_ix = k_ix % (len(self.kaleidoscopes))

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
        p["need_update"] = True
        p["update_state"] = True
        self.presets[str(number)] = p
        self.save_preset_lib()
        return f"Added new Preset in {number}"

    def load_params_from_preset(self, number):
        stay_at_n = self.params.current_preset_num
        self.params = Parameters.from_dict(self.presets[str(number)])
        self.params.need_update = True
        self.params.update_state = True
        self.params.current_preset_num = stay_at_n
        return f"Loaded Preset from {number}"

    def update_params(self):
        if self.params.need_update:
            # Basics
            self._w = self.params.w
            self._h = self.params.h
            self._winh = self.params.winh
            self._winw = self.params.winw
            self._numpix = self._w * self._h
            # Signal Generators
            self.rchannel.numpix = self._numpix
            self.gchannel.numpix = self._numpix
            self.bchannel.numpix = self._numpix

            self.rchannel.freq = self.params.r_freq
            self.gchannel.freq = self.params.g_freq
            self.bchannel.freq = self.params.b_freq

            self.rchannel.waveform_ix = self.params.r_waveform_ix #% len(self.waveforms)
            self.gchannel.waveform_ix = self.params.g_waveform_ix #% len(self.waveforms)
            self.bchannel.waveform_ix = self.params.b_waveform_ix #% len(self.waveforms)
            # Kaleidoscopes
            self.k_ix = self.params.kaleidoscope_ix

            self.kaleidoscopes[1].flipped = self.params.k_flip
            self.kaleidoscopes[1].full_size = self.params.w
            self.kaleidoscopes[1].n_segments = self.params.k_n_segments
            self.kaleidoscopes[1].alternate_flip = self.params.k_alternate_flip

            self.kaleidoscopes[2].flipped = self.params.k_flip
            self.kaleidoscopes[2].size = self.params.w
            self.kaleidoscopes[2].n_segments = self.params.k_n_segments
            self.kaleidoscopes[2].alternate_flip = self.params.k_alternate_flip

            self.kaleidoscopes[3].flipped = self.params.k_flip
            self.kaleidoscopes[3].size = self.params.w
            if len(self.params.k_manual_rot) != len(self.kaleidoscopes[3].rotations):
                if not len(self.params.k_manual_rot) == 0:
                    self.kaleidoscopes[3].rotations = [i[0] for i in self.params.k_manual_rot]
                    self.kaleidoscopes[3].rotations_dir = [i[1] for i in self.params.k_manual_rot]
                else:
                    self.kaleidoscopes[3].rotations = []
                    self.kaleidoscopes[3].rotations_dir = []
            if self.win_canvas.shape != (self.params.winh, self.params.winw, 3):
                self.win_canvas = np.zeros((self.params.winh, self.params.winw, 3), dtype=np.float32)


            if self.params.update_state:
                self.rchannel.state = self.params.r_state
                self.gchannel.state = self.params.g_state
                self.bchannel.state = self.params.b_state
                self.params.update_state = False

            self.params.need_update = False

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

        # print(leftover_w, leftover_h, left, top, w, h, winw, winh, (left + w))
        # win_canvas = np.zeros((winh, winw, 3), dtype=np.float32)
        self.win_canvas[top:(top + self._h), left:(left + self._w), :] = rgb

        # if False:
        #     if left > 1:
        #         #print(rgb[:, 0:left, :].shape)
        #         #print(rgb[:, 0:left:-1, :].shape)
        #         win_canvas[:, 0:left, :] = rgb[:, 0:left, :][:,::-1,:]
        #         win_canvas[:, (winw - right):winw, :] = rgb[:, (w - right):w, :][:,::-1,:]
        #     if top > 1:
        #         win_canvas[0:top, :, :] = rgb[0:top, :, :][::-1,:,:]
        #         win_canvas[(winh - bottom):winh, :, :] = rgb[(h - bottom):h, :, :][::-1,:,:]
        return self.win_canvas

