from audioop import avg
from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
import scipy.fft as fft
from scipy.signal import find_peaks
from textwrap import wrap

REL_FREQ = 4

FREQ0 = 5000
FREQ1 = 10000

l = []

freq_sample, sig_audio = wavfile.read("./example.wav")
pow_audio_signal = sig_audio / np.power(2, 15)
time_axis = 1000 * np.arange(0, len(pow_audio_signal), 1) / float(freq_sample)
plt.plot(time_axis, pow_audio_signal, color='blue')

duration = int(freq_sample/(REL_FREQ*12))
x=0
for i in range(0,len(sig_audio),duration):
    yf = fft.fft(sig_audio[i:i+duration])
    xf = fft.fftfreq(duration, 1 / freq_sample)
    print(xf[np.argmax(yf)])

    if (abs(FREQ0-abs(xf[np.argmax(yf)])) < 500):
        l.append(0)
    elif (abs(FREQ1-abs(xf[np.argmax(yf)])) < 500):
        l.append(1)
    else:
        l.append(-1)

print(l)

ciphertext = ""

for i in range(0, len(l), 4):
    ciphertext += str(int(round(sum(l[i:i+4])/4, 0)))

key1inv = 183
key2 = 193

c = wrap(ciphertext, 8)
m = ""


for char in c:
    if (char != "11000001"):
        # decrypt each character with decryption formula (ignore null characters)
        m += chr((key1inv * (int(char, 2) - key2)) % 256)

# print message
print("Message: " + m)


#plt.plot(l)
#plt.savefig("out1")
#plt.clf()