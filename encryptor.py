# imports
from scipy.io import wavfile
import numpy as np
import os

# hamming functionality
def get_hamming(data, d_bits, p_bits):
    # print(len(data))

    # ensure data is the correct size
    if len(data) != d_bits:
        data = np.append(data, np.zeros(d_bits - len(data)))
    
    # add space for parity bits
    encoded = np.zeros(2 ** p_bits, dtype = np.ubyte)
    parity_bits = np.zeros(p_bits + 1)
    data_index = 0
    p_place = 4

    # iterate through parity bits
    for i in range(3, 2 ** p_bits):
        # double 4
        if i == p_place:
            p_place *= 2
        
        else:
            # set data bit and increment index
            data_bit = data[data_index]
            encoded[i] = data_bit
            data_index += 1
            parity_bits[0] += data_bit
            
            # allow for variable number of parity bits
            if int(i % 2) == 1:
                parity_bits[1] += data_bit
            if int((i % 4) / 2) == 1:
                parity_bits[2] += data_bit
            if int((i % 8) / 4) == 1:
                parity_bits[3] += data_bit
            if int((i % 16) / 8) == 1:
                parity_bits[4] += data_bit
            if int((i % 32) / 16) == 1:
                parity_bits[5] += data_bit

    # iterate through parity bits
    for i in range(1, p_bits + 1):
        if parity_bits[i] % 2 == 1:
            encoded[(2 ** (i - 1))] = 1
            parity_bits[0] += data_bit
    
    # first index
    if parity_bits[0] % 2 == 1:
            encoded[0] = 1

    # return encoding
    return encoded

# hamming variables
P_BITS = 5 # number of parity bits per packet (exluding 0)
D_BITS = 26 # number of data bits per packet
PACKET_SIZE = 32 # number of total bits per packet (P_BITS + D_BITS + 1; 2^P_BITS >= PACKET_SIZE)

# wav file variables
samplerate = 44100
FREQ0 = 1000 # tone 0
FREQ1 = 2000 # tone 1
array = np.array([])
t = np.linspace(0., (1 / 12), int(samplerate / 12))
amplitude = np.iinfo(np.int16).max
high = amplitude * np.sin(2. * np.pi * FREQ1 * t)
low = amplitude * np.sin(2. * np.pi * FREQ0 * t)
high[-100 : -1] = 0
low[-100 : -1] = 0
space = np.zeros(500)

# affine cipher keys
key1 = 7
key2 = 193

# accept message from user input
m = input("Enter the message: ")
c = []
binary = ""

# encrypt ASCII characters
for char in m:
    c.append((key1 * ord(char) + key2) % 256)

binary += "11000001" # start with null

# convert message to binary
for char in c:
    temp = bin(char)[2:]
    binary += '0' * (8 - len(temp)) + temp

binary += "11000001" # end with null

# get bit array
bit_arr = np.fromstring(binary, dtype = np.ubyte) - 48

# get hamming foundation
binary_arr = get_hamming(bit_arr[:D_BITS], D_BITS, P_BITS)

# get new array with hamming
for i in range(26, len(bit_arr), D_BITS):
    binary_arr = np.append(binary_arr, get_hamming(bit_arr[i:i+D_BITS], D_BITS, P_BITS))

# iterate through array with hamming and add signals
for i in range(0, len(binary_arr), 1):
    if binary_arr[i] == 0:
        array = np.append(array, low) # low
    else:
        array = np.append(array, high) # high

# format array
array = np.append(space, array)
array = np.append(array, space)

# write to wav file
wavfile.write("output.wav", samplerate, array.astype(np.int16))

# wait for keystroke
input("Press <Enter> to play message")

# play wav file
wav_file = "./output.wav"
os.system(f'aplay {wav_file}')

# os.remove(wav_file)
