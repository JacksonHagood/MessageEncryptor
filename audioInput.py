from scipy import fft, arange
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import os


def frequency_spectrum(x, sf):
    """
    Derive frequency spectrum of a signal from time domain
    :param x: signal in the time domain
    :param sf: sampling frequency
    :returns frequencies and their content distribution
    """
    x = x - np.average(x)  # zero-centering

    n = len(x)
    k = np.arange(n)
    tarr = n / float(sf)
    frqarr = k / float(tarr)  # two sides frequency range

    frqarr = frqarr[range(n // 2)]  # one side frequency range

    x = fft(x) / n  # fft computing and normalization
    x = x[range(n // 2)]

    return frqarr, abs(x)


# Sine sample with a frequency of 1hz and add some noise
sr = 32  # sampling rate
y = np.linspace(0, 2*np.pi, sr)
y = np.tile(np.sin(y), 5)
y += np.random.normal(0, 1, y.shape)
t = np.arange(len(y)) / float(sr)

plt.subplot(2, 1, 1)
plt.plot(t, y)
plt.xlabel('t')
plt.ylabel('y')

# frq, X = frequency_spectrum(y, sr)

# plt.subplot(2, 1, 2)
# plt.plot(frq, X, 'b')
# plt.xlabel('Freq (Hz)')
# plt.ylabel('|X(freq)|')
# plt.tight_layout()


# wav sample from https://freewavesamples.com/files/Alesis-Sanctuary-QCard-Crickets.wav
here_path = os.path.dirname(os.path.realpath(__file__))
wav_file_name = 'Alesis-Sanctuary-QCard-Crickets.wav'
#wave_file_path = os.path.join(here_path, wav_file_name)
sr, signal = wavfile.read("output.wav")

y = signal[:, 0]  # use the first channel (or take their average, alternatively)
t = np.arange(len(y)) / float(sr)

plt.figure()
plt.subplot(2, 1, 1)
plt.plot(t, y)
plt.xlabel('t')
plt.ylabel('y')

# frq, X = frequency_spectrum(y, sr)

# plt.subplot(2, 1, 2)
# plt.plot(frq, X, 'b')
# plt.xlabel('Freq (Hz)')
# plt.ylabel('|X(freq)|')
# plt.tight_layout()

plt.show()