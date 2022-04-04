from scipy.io import wavfile
import numpy as np


samplerate = 44100
FREQ0 = 5000
FREQ1 = 10000
array = np.array([])
t = np.linspace(0., (1/12), int(samplerate/12))
amplitude = np.iinfo(np.int16).max
high = amplitude * np.sin(2. * np.pi * FREQ1 * t)
low = amplitude * np.sin(2. * np.pi * FREQ0 * t)
high[-100:-1] = 0
low[-100:-1] = 0
space = np.zeros(500)

# affine cipher keys
key1 = 7
key2 = 193

m = input("Enter the message: ")
c = []
binary = ""

for char in m:
    # encrypt each character with encryption formula
    c.append((key1 * ord(char) + key2) % 256)

# print encrypted message as 8 bit binary numbers (starting and ending with a null character)

binary += "11000001"
for char in c:
    temp = bin(char)[2:]
    binary += '0' * (8 - len(temp)) + temp
binary += "11000001"

print("Encrypted message: " + binary)



for i in range(0, len(binary), 1):
    if binary[i] == '0':
        #print('0')
        array = np.append(array, low)
    else:
        #print('1')
        temp = np.full((1, FREQ0), amplitude)
        array = np.append(array, high)
        


wavfile.write("example.wav", samplerate, array.astype(np.int16))


