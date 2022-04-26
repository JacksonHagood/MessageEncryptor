# imports
from pickle import NONE
from scipy.io import wavfile
import numpy as np
import pyaudio
import scipy.fft as fft
from scipy.signal import find_peaks
from textwrap import wrap
from functools import reduce
import operator as op
import wave
import signal
import os
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
from time import sleep
from Project.encryptor_constants import *


def scroll_on_lcd(output):
    while True:
        # display message, moving to the right
        lcd.message = output[i:i + 16]
        if len(output) < 18:
            break
        i = (i + 1) % len(m)
        sleep(0.25)


cont = True # boolean for signal handling

# signal handler for stopping recording
def sigint_handler(signal, frame):
        print("Stopping...")
        global cont
        cont = False

signal.signal(signal.SIGINT, sigint_handler) # signal setup

# wav file variables
channels = 1
wav_file = "input.wav"
form = pyaudio.paInt16
frames = []

# setup audio listener
p = pyaudio.PyAudio()
stream = p.open(format = form, channels = channels, rate = SAMPLE_RATE, input = True, frames_per_buffer = READ_SIZE)

# wait for keystroke
p_bits = int(input("Enter number of parity bits for error correction: "))
packet_size = 2 ** p_bits # number of total bits per packet (P_BITS + D_BITS + 1; 2^P_BITS >= PACKET_SIZE)
d_bits = packet_size - (p_bits + 1) # number of data bits per packet
input("Press <Enter> to start recording...")
print("* recording")

# read sound signal
while cont:
    data = stream.read(READ_SIZE)
    frames.append(data)

# stop recording
print("* done recording")

# close reader
stream.stop_stream()
stream.close()
p.terminate()

# write to wav file
wf = wave.open(wav_file, 'wb')
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(form))
wf.setframerate(SAMPLE_RATE)
wf.writeframes(b''.join(frames))
wf.close()

# open wav file
freq_sample, sig_audio = wavfile.read("./input.wav")

if sig_audio.ndim > 1:
        sig_audio = sig_audio[:, 0]

# get duration
duration = int(freq_sample / (REL_FREQ * 12))

# list to store binary value over window
dirty_bin = []
x = 0

# iterate through signal
for i in range(0, len(sig_audio), duration):
    # get y and x
    yf = fft.rfft(sig_audio[i : i + duration])
    xf = fft.rfftfreq(duration, 1 / freq_sample)

    # determine the dominant frequency
    dominant_freq = xf[np.argmax(np.abs(yf))]

    # determine if the frequency is 0 or 1
    if (abs(FREQ1 - dominant_freq) < 50):
        dirty_bin.append(1)
    elif (abs(FREQ0 - dominant_freq) < 50):
        dirty_bin.append(0)
    else:
        dirty_bin.append(-1)

# trim array at the front
for bit in range(len(dirty_bin)):
    if dirty_bin[bit] != -1:
        dirty_bin = dirty_bin[bit + 1 :]
        break

ciphertext = "" # raw ciphertext

# add to ciphertext
for k in range(0, len(dirty_bin), REL_FREQ):
    if int(round(sum(dirty_bin[k : k + REL_FREQ]) / REL_FREQ, 0)) == -1:
        break
    
    mid_chunk = dirty_bin[int(round(k + (REL_FREQ / 4))):int(round(k + (3 * REL_FREQ / 4)))]

    if len(mid_chunk) == 0:
        break
    
    ciphertext += str(int(round(sum(mid_chunk) / (len(mid_chunk)), 0))) # append to ciphertext

# convert ciphertext
ciphertext += ((packet_size - len(ciphertext)) % packet_size) * '0'
ciphertext = np.fromstring(ciphertext, dtype=np.ubyte) - 48

# account for hamming
decoded = ""
remove = [2 ** i for i in range(p_bits)]
remove.append(0)

# iterate through ciphertext
for i in range(0, len(ciphertext), packet_size):
    bits = [i for i, bit in enumerate(ciphertext[i : i + packet_size]) if bit]
    if not bits:
        continue
    index = (reduce(op.xor, bits))
    
    ciphertext[i + index] = ciphertext[i + index] ^ 1
    decoded += "".join([",".join(item) for item in np.delete(ciphertext[i : i + packet_size], remove).astype(str)])
    
# get actual ciphertext
ciphertext = decoded

# TODO: dipswitch
d = "1111111111"

# dipswitch values
index1 = 0
index2 = 0

# get dipswitch values
for i in range(5):
    if (d[i] == "1"):
        index1 += 2 ** i
    if (d[i + 5] == "1"):
        index2 += 2 ** i

# get affine cipher keys
key1 = 193 if index2 % 2 == 0 else 97
key1inv = 65 if index2 % 2 == 0 else 161
key2 = KEYS[index1]

NULL_BYTE = to_bin(encrypt_char(0, key1, key2))
# initialize message variable
m = ""

# search for start of message (null)
for i in range(len(ciphertext)):
    if ciphertext[i : i + 8] == NULL_BYTE:
        ciphertext = ciphertext[i + 8 :]
        break

# iterate through message until the null is reached
for j in range(0, len(ciphertext), 8):
    char = ciphertext[j : j + 8]
    if char == NULL_BYTE:
        break
    else:
        # decode ciphertext with affine cipher
        m += chr((key1inv * (int(char, 2) - key2)) % 256)

# print message
print("Message: " + m)

# setup LCD
lcd_columns = 16
lcd_rows = 2
lcd_rs = digitalio.DigitalInOut(board.D22)
lcd_en = digitalio.DigitalInOut(board.D17)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d6 = digitalio.DigitalInOut(board.D23)
lcd_d7 = digitalio.DigitalInOut(board.D18)
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)
lcd.clear()

# setup
i = 0
m += " "

scroll_on_lcd(m)

# os.remove("./input.wav")