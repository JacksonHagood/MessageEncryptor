from pickle import NONE
from scipy.io import wavfile
import numpy as np
# import matplotlib.pyplot as plt
import pyaudio
import scipy.fft as fft
from scipy.signal import find_peaks
from textwrap import wrap
from functools import reduce
import operator as op
import wave
import signal
import os

cont = True

def sigint_handler(signal, frame):
        print("Stopping...")
        global cont
        cont = False

signal.signal(signal.SIGINT, sigint_handler)


# write to wave file
CHUNK = 1000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 25
WAVE_OUTPUT_FILENAME = "input.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
input("Press <Enter> to start recording...")
print("* recording")

frames = []

while cont:
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

REL_FREQ = 4

FREQ0 = 1000
FREQ1 = 2000

NULL_BYTE = "11000001"

freq_sample, sig_audio = wavfile.read("./input.wav")

if sig_audio.ndim > 1:
        sig_audio = sig_audio[:, 0]

duration = int(freq_sample/(REL_FREQ*12))
#print("Duration:", duration)
# List to store binary value over window (needs to be cleaned before message can be decoded)
dirty_bin = []
x=0
for i in range(0,len(sig_audio),duration):
    yf = fft.rfft(sig_audio[i:i+duration])
    xf = fft.rfftfreq(duration, 1 / freq_sample)



    """plt.plot(xf, yf)
    plt.savefig(f"plot{x}")
    plt.margins(x=0, y=-0.25)
    plt.clf()
    x += 1"""

    #peaks, info = find_peaks(yf, height=0, threshold=600, distance=4)
    """
    for i in range(len(xf)):
        if xf[i] < 0:
            
    """
    """plt.plot(yf)
    plt.plot(peaks, yf[peaks], "x")
    plt.savefig(f"plot{x}")
    plt.clf()"""
    
    #print(xf[peaks])
    #print("Y: ", yf[peaks])

    """
    for p in peaks:
        if (xf[p] > 400 and xf[p] < 3600):
            print(xf[p], abs(yf[p]))"""
   #print("\n\n")

    """if (abs(FREQ0-abs(xf[np.argmax(yf)])) < 500):
        l.append(0)"""

    dominant_freq = xf[np.argmax(np.abs(yf))]
    #print(dominant_freq)

    if (abs(FREQ1-dominant_freq) < 50):
        dirty_bin.append(1)
    elif (abs(FREQ0-dominant_freq) < 50):
        dirty_bin.append(0)
    else:
        dirty_bin.append(-1)

#print(dirty_bin)

ciphertext = ""

for bit in range(len(dirty_bin)):
    if dirty_bin[bit] != -1:
        print("Trimming")
        dirty_bin = dirty_bin[bit+1:]
        break

for k in range(0, len(dirty_bin), REL_FREQ):
    if int(round(sum(dirty_bin[k:k+REL_FREQ])/REL_FREQ, 0)) == -1:
        break
    mid_chunk = dirty_bin[int(round(k+(REL_FREQ/4))):int(round(k+(3*REL_FREQ/4)))]
    if len(mid_chunk) == 0:
        break
    ciphertext += str(int(round(sum(mid_chunk)/(len(mid_chunk)), 0)))



ciphertext += ((32-len(ciphertext)) % 32) * '0'
ciphertext = np.fromstring(ciphertext, dtype=np.ubyte) - 48
"""ciphertext[12] = ciphertext[12] ^ 1
ciphertext[55] = ciphertext[55] ^ 1
ciphertext[70] = ciphertext[55] ^ 1"""
decoded = ""
remove = [2**i for i in range(5)]
remove.append(0)
#print(remove)
for i in range(0, len(ciphertext), 32):
    print(ciphertext[i:i+32])
    bits = [i for i, bit in enumerate(ciphertext[i:i+32]) if bit]
    if not bits:
        continue
    index = (reduce(op.xor, bits))
    
    ciphertext[i+index] = ciphertext[i+index] ^ 1
    decoded += "".join([",".join(item) for item in np.delete(ciphertext[i:i+32], remove).astype(str)])
    

ciphertext = decoded
print(ciphertext)
#print(ciphertext)


key1inv = 183
key2 = 193

# Search for NULL and trim binary
msg_started = False
m = ""

for i in range(len(ciphertext)):
    if ciphertext[i:i+8] == NULL_BYTE and not msg_started:
        ciphertext = ciphertext[i+8:]
        msg_started = True
        print("Start found")
        break

for j in range(0, len(ciphertext), 8):
    char = ciphertext[j:j+8]
    #print(char)
    """if len(char) < 8:
        char += (8 - len(char)) * "1"""
    if char == NULL_BYTE:
        print("End found")
        break
    else:
        #print("Char:", chr((key1inv * (int(char, 2) - key2)) % 256), char)
        m += chr((key1inv * (int(char, 2) - key2)) % 256)
#os.system("clear")
print("Message: " + m)
