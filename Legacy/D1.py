# imports (for recording to wav file and analyzing wav file)
import pyaudio
import wave
from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
import scipy.fft as fft
from scipy.signal import find_peaks
from textwrap import wrap

# write to wave file
# CHUNK = 1000
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 44100
# RECORD_SECONDS = 12
# WAVE_OUTPUT_FILENAME = "input.wav"

# p = pyaudio.PyAudio()

# stream = p.open(format=FORMAT,
#                 channels=CHANNELS,
#                 rate=RATE,
#                 input=True,
#                 frames_per_buffer=CHUNK)

# print("* recording")

# frames = []

# for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#     data = stream.read(CHUNK)
#     frames.append(data)

# print("* done recording")

# stream.stop_stream()
# stream.close()
# p.terminate()

# wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
# wf.setnchannels(CHANNELS)
# wf.setsampwidth(p.get_sample_size(FORMAT))
# wf.setframerate(RATE)
# wf.writeframes(b''.join(frames))
# wf.close()

REL_FREQ = 4
FREQ0 = 1000
FREQ1 = 2000
NULL_BYTE = "11000001"

freq_sample, sig_audio = wavfile.read("./input.wav")
sig_audio = sig_audio.flatten()
#print(freq_sample, sig_audio)
#pow_audio_signal = sig_audio / np.power(2, 15)
#time_axis = 1000 * np.arange(0, len(pow_audio_signal), 1) / float(freq_sample)
#plt.plot(time_axis, pow_audio_signal, color='blue')
#print(type(sig_audio), type(sig_audio[0]))
duration = int(freq_sample/(REL_FREQ*12))


# List to store binary value over window (needs to be cleaned before message can be decoded)
dirty_bin = []
#x=0
for i in range(0,len(sig_audio),duration):
    yf = fft.fft(sig_audio[i:i+duration])
    xf = fft.fftfreq(duration, 1 / freq_sample)

    peaks, info = find_peaks(yf, height=0, threshold=100)
    # print(xf[peaks])

    if (abs(FREQ1-abs(xf[np.argmax(yf)])) < 500):
        dirty_bin.append(1)
    else:
        dirty_bin.append(0)

#print(dirty_bin)

ciphertext = ""

for i in range(0, len(dirty_bin), REL_FREQ):
    ciphertext += str(int(round(sum(dirty_bin[i:i+REL_FREQ])/REL_FREQ, 0)))

# affine cipher (decryption) keys
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
    if ciphertext[j:j+8] == NULL_BYTE:
        ciphertext = ciphertext[:j]
        print("End found")
        break
    else:
        m += chr((key1inv * (int(ciphertext[j:j+8], 2) - key2)) % 256)

# print message
print("Message: " + m)
