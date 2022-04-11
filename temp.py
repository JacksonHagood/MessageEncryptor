import numpy as np
from scipy.fft import *
from scipy.io import wavfile
import matplotlib.pyplot as plt

def freq(file, start_time, end_time):
    # Open the file and convert to mono
    sr, data = wavfile.read(file)
    if data.ndim > 1:
        data = data[:, 0]
    else:
        pass

    # Return a slice of the data from start_time to end_time
    dataToRead = data[int(start_time * sr / 1000) : int(end_time * sr / 1000) + 1]

    # Fourier Transform
    N = len(dataToRead)
    yf = rfft(dataToRead)
    xf = rfftfreq(N, 1 / sr)

    # Get the most dominant frequency and return it
    idx = np.argmax(np.abs(yf))
    freq = xf[idx]
    return freq

stop, data = wavfile.read(file)
# stop = 8000
steps = 500

frequencies = []

for i in range(steps):
    # print(stop * ((i + 0.0) / 100.0), stop * ((i + 1.0) / 100.0))
    frequencies.append(freq("input.wav", stop * ((i + 0.0) / steps), stop * ((i + 1.0) / steps)))
    
    # print(freq("input.wav", stop * ((i + 0.0) / steps), stop * ((i + 1.0) / steps)))

skip = 0

for f in frequencies:
    if skip > 0:
        continue
    if f < 2500 and f > 1500:
        print("1", end="")
    elif f < 1500 and f > 500:
        print("0", end="")