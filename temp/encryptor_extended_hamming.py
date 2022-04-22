# imports
from telnetlib import ENCRYPT
from scipy.io import wavfile
import numpy as np
import os
from encryptor_constants import *

# hamming functionality
def get_hamming(data, p_bits):
    print(p_bits)
    packet_size = 2 ** p_bits
    d_bits = packet_size - (p_bits + 1)
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
    for i in range(3, packet_size):
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
            for j in range(p_bits):
                if int((i % 2 ** (j+1)) / (2 ** j)) == 1:
                    parity_bits[j+1] += data_bit
            """
            if int((i % 2 ** 1) / (2 ** 0)) == 1:
                parity_bits[1] += data_bit
            if int((i % (2 ** 2)) / 2) == 1:
                parity_bits[2] += data_bit
            if int((i % (2 ** 3)) / 4) == 1:
                parity_bits[3] += data_bit
            if int((i % (2 ** 4)) / 8) == 1:
                parity_bits[4] += data_bit
            if int((i % (2 ** 5)) / 16) == 1:
                parity_bits[5] += data_bit"""

    # iterate through parity bits
    for i in range(1, p_bits + 1):
        if parity_bits[i] % 2 == 1:
            encoded[(2 ** (i - 1))] = 1
            parity_bits[0] += data_bit
    
    # first index
    if parity_bits[0] % 2 == 1:
            encoded[0] = 1

    # return encoding
    print(encoded, "\n\n")
    return encoded


# hamming variables
P_BITS = 5 # number of parity bits per packet (exluding 0)
PACKET_SIZE = 2 ** P_BITS # number of total bits per packet (P_BITS + D_BITS + 1; 2^P_BITS >= PACKET_SIZE)
D_BITS = PACKET_SIZE - (P_BITS + 1) # number of data bits per packet


# wav file variables
array = np.array([])
space = np.zeros(500)

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
key2 = KEYS[index1]

# accept message from user input
m = input("Enter the message: ")
P_BITS = int(input("Enter number of parity bits for error correction: "))
PACKET_SIZE = 2 ** P_BITS # number of total bits per packet (P_BITS + D_BITS + 1; 2^P_BITS >= PACKET_SIZE)
D_BITS = PACKET_SIZE - (P_BITS + 1) # number of data bits per packet
binary = ""

# encrypt ASCII characters
ENCRYPTED_NULL = encrypt_char(0, key1, key2)

c = ENCRYPTED_NULL + encrypt_msg(m, key1, key2) + ENCRYPTED_NULL
binary = to_bin(c)

# get bit array
bit_arr = np.fromstring(binary, dtype = np.ubyte) - 48

# get hamming foundation
binary_arr = get_hamming(bit_arr[: D_BITS], P_BITS)

# get new array with hamming
for i in range(D_BITS, len(bit_arr), D_BITS):
    binary_arr = np.append(binary_arr, get_hamming(bit_arr[i:i+D_BITS], P_BITS))

# iterate through array with hamming and add signals
for i in range(0, len(binary_arr), 1):
    if binary_arr[i] == 0:
        array = np.append(array, LOW_SIGNAL) # low
    else:
        array = np.append(array, HIGH_SIGNAL) # high

# format array
array = np.append(space, array)
array = np.append(array, space)

# REMOVE FOLLOWING BLOCK
# output binary for debugging
string = ""
for i in range(len(binary_arr)):
    string += str(binary_arr[i])
print(string)

# write to wav file
wavfile.write("output.wav", SAMPLE_RATE, array.astype(np.int16))

# wait for keystroke
input("Press <Enter> to play message")

# play wav file
wav_file = "./output.wav"
os.system(f'aplay {wav_file}')

# os.remove(wav_file)