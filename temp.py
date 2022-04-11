import numpy as np
from scipy.fft import *
from scipy.io import wavfile
import pyaudio
import wave
from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
import scipy.fft as fft
from scipy.signal import find_peaks
from textwrap import wrap

# write to wave file
CHUNK = 1000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 12
WAVE_OUTPUT_FILENAME = "input.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

#------

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

# get length of wav file
sample_rate, data = wavfile.read("input.wav")
stop = int(len(data) / sample_rate) * 1000
steps = 1000

frequencies = []

for i in range(steps):
    if stop * ((i + 1.0) / steps) > stop:
        break
    
    frequencies.append(freq("input.wav", stop * ((i + 0.0) / steps), stop * ((i + 1.0) / steps)))

skip = 0

temp = ""

for f in frequencies:
    if f < 2500 and f > 1500:
        temp += "1"
        # print("1", end="")
    elif f < 1500 and f > 500:
        temp += "0"
        # print("0", end="")

print(temp, "\n")

binary = ""
skip = 0
current = "0"

for char in temp:
    if current != char:
        skip = 0
    
    if skip > 0:
        skip -= 1
    elif char == "0":
        binary += "0"
        current = "0"
        skip = 8
    else:
        binary += "1"
        current = "1"
        skip = 8

print(binary, "\n")

i = 0
NULL_BYTE = "11000001"
key1inv = 183
key2 = 193
m = ""

for i in range(len(binary)):
    if binary[i:i+8] == NULL_BYTE:
        binary = binary[i + 8:]
        msg_started = True
        print("Start found")
        break

for j in range(0, len(binary), 8):
    if binary[j:j+8] == NULL_BYTE:
        binary = binary[:j]
        print("End found")
        break
    else:
        m += chr((key1inv * (int(binary[j:j+8], 2) - key2)) % 256)

print("Message: " + m[0 : len(m) - 1])
