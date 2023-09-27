import numpy as np
from scipy.signal import sawtooth


def sin(t):
    px = np.sin(t)
    # is -1 to 1
    px += 1
    px /= 2
    return px


def normalize_pixels(pixels):
    pixels += abs(pixels.min())
    pixels /= pixels.max()
    return pixels


def square_wave(t):
    px = np.ceil(np.sin(t))
    # already 0 or 1
    return px

def noise(t):
    px = np.random.rand(len(t))
    # 0 to 1
    return px

def constant(t):
    freq = t[-1] - t[0]
    col = freq / 12700
    px = np.ones(len(t), dtype=np.float32) * col
    # 0 to 1
    return px

def triangle(t):
    px = sawtooth(t, 0.5)
    # 0 to 1
    return px





class SignalGenerator():
    def __init__(self, waveform, numpix, freq, id=""):
        self.waveform = waveform
        self.numpix = numpix
        self._freq = freq
        self.state = 0
        self.id = id
        self.ref_t = np.linspace(0, (self.freq * (2 * np.pi)), num=self.numpix, dtype=np.float32)

    @property
    def freq(self):
        return(self._freq)

    @freq.setter
    def freq(self, freq):
        self._freq = int(freq)
        self.ref_t = np.linspace(0, (self.freq * (2 * np.pi)), num=self.numpix, dtype=np.float32)
        # TODO: you could also precompute the Wavefunction by making one thats double as long and then just
        # indexing into the section you need

    def get_series(self, n_scanned_px):
        t = self.ref_t + self.state
        px = self.waveform(t)
        self.state = t[np.mod(int(n_scanned_px), self.numpix - 1)]
        return px

    def print_freq(self):
        print(self.id, " frequency: " , self.freq)

    def cycle_waveform(self):
        if self.waveform == sin:
            self.waveform = square_wave
        elif self.waveform == square_wave:
            self.waveform = noise
        elif self.waveform == noise:
            self.waveform = constant
        elif self.waveform == constant:
            self.waveform = triangle
        else:
            self.waveform = sin
        
