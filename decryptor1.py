from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
import scipy.fft as fft
from scipy.signal import find_peaks

freq_sample, sig_audio = wavfile.read("./example.wav")
pow_audio_signal = sig_audio / np.power(2, 15)
time_axis = 1000 * np.arange(0, len(pow_audio_signal), 1) / float(freq_sample)
plt.plot(time_axis, pow_audio_signal, color='blue')

duration = int(freq_sample/(2*12))

for i in range(0,len(sig_audio),duration):
    yf = fft.fft(sig_audio[i:i+duration])
    xf = fft.fftfreq(duration, 1 / freq_sample)
    print(yf)
