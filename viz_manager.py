from dataclasses import dataclass
import sig_gen as sg
import kaleidoscope as kal
import numpy as np

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

    winw: int = 600
    winh: int = 600
    w: int = 600
    h: int = 600

    need_update: bool = False
    update_state: bool = False


    def __setattr__(self, name, value):
        if name == "need_update":
            self.__dict__["need_update"] = value
        else:
            super().__setattr__(name, value)
            self.need_update = True


class Vizard():
    def __init__(self):
        self.params = Parameters()
        self._w = self.params.w
        self._h = self.params.h
        self._winh = self.params.winh
        self._winw = self.params.winw
        self._numpix = self.params.w * self.params.h

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
        self.kaleidoscopes = [None, self.kal1, self.kal2]

        self.win_canvas = np.empty((self.params.winh, self.params.winw, 3),
                                   dtype=np.float32)


    @property
    def k_ix(self):
        return(self._k_ix)

    @k_ix.setter
    def k_ix(self, k_ix):
        self._k_ix = k_ix % (len(self.kaleidoscopes))
        self.params.kaleidoscope_ix = k_ix % (len(self.kaleidoscopes))

    def update_params(self):
        if self.params.need_update:
            self._w = self.params.w
            self._h = self.params.h
            self._winh = self.params.winh
            self._winw = self.params.winw
            self._numpix = self._w * self._h

            self.rchannel.numpix = self._numpix
            self.gchannel.numpix = self._numpix
            self.bchannel.numpix = self._numpix

            self.rchannel.freq = self.params.r_freq
            self.gchannel.freq = self.params.g_freq
            self.bchannel.freq = self.params.b_freq

            self.rchannel.waveform_ix = self.params.r_waveform_ix % len(self.waveforms)
            self.gchannel.waveform_ix = self.params.g_waveform_ix % len(self.waveforms)
            self.bchannel.waveform_ix = self.params.b_waveform_ix % len(self.waveforms)

            self.k_ix = self.params.kaleidoscope_ix
            for i in range(1, len(self.kaleidoscopes)):
                self.kaleidoscopes[i].flipped = self.params.k_flip
                self.kaleidoscopes[i].size = self.params.w
                self.kaleidoscopes[i].n_segments = self.params.k_n_segments
                self.kaleidoscopes[i].alternate_flip = self.params.k_alternate_flip

            if self.win_canvas.shape != (self.params.winh, self.params.winw, 3):
                self.win_canvas = np.zeros((self.params.winh, self.params.winw, 3), dtype=np.float32)

            if self.params.update_state:
                self.rchannel.state = self.params.rstate
                self.gchannel.state = self.params.gstate
                self.bchannel.state = self.params.bstate
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

