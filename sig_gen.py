import numpy as np
from scipy.signal import sawtooth


def sin(t):
    px = np.sin(t)
    return normalize_pixels(px)

def square_wave(t):
    px = np.floor(np.sin(t))
    return normalize_pixels(px)

def noise(t):
    px = np.random.rand(len(t))
    return normalize_pixels(px)

def constant(t):
    freq = t[-1] - t[0]
    col = freq / 12700
    px = np.ones(len(t)) * col
    return px.astype(np.float32)

def normalize_pixels(pixels):
    pixels += abs(min(pixels))
    pixels /= max(pixels)
    return pixels.astype(np.float32)

def triangle(t):
    px = sawtooth(t, 0.5)
    return normalize_pixels(px)


class SignalGenerator():
    def __init__(self, waveform, numpix, freq, id=""):
        self.waveform = waveform
        self.numpix = numpix
        self.freq = freq
        self.state = 0
        self.id = id

    def get_series(self, n_scanned_px):
        t = np.linspace(self.state, self.state + self.freq, num=self.numpix)
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
        
