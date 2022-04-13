# imports (for writing to wav file)
from scipy.io import wavfile
import numpy as np

# define variables
FREQ0 = 1000
FREQ1 = 2000
samplerate = 44100
array = np.array([])
t = np.linspace(0., (1/12), int(samplerate/12))
amplitude = np.iinfo(np.int16).max
high = amplitude * np.sin(2. * np.pi * FREQ1 * t)
low = amplitude * np.sin(2. * np.pi * FREQ0 * t)
high[-100: -1] = 0
low[-100: -1] = 0
space = np.zeros(500)

# affine cipher (encryption) keys
key1 = 7
key2 = 193

# take input
m = input("Enter the message: ")
c = []
binary = ""

# encrypt each character with encryption formula
for char in m:
    c.append((key1 * ord(char) + key2) % 256)

# convert encrypted ASCII message to binary (padded with 11000001)
binary += "11000001"
for char in c:
    temp = bin(char)[2:]
    binary += '0' * (8 - len(temp)) + temp
binary += "11000001"

print(binary)

# iterate through string of binary numbers
for i in range(0, len(binary), 1):
    if binary[i] == '0':
        array = np.append(array, low) # low
    else:
        array = np.append(array, high) # high

# construct array
array = np.append(space, array)
array = np.append(array, space)

# write to wave file
wavfile.write("output.wav", samplerate, array.astype(np.int16))
