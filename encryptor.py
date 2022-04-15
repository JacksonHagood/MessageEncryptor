from scipy.io import wavfile
import numpy as np
import os

def get_hamming(data, d_bits, p_bits):
    print(len(data))
    if len(data) != d_bits:
        data = np.append(data, np.zeros(d_bits-len(data)))
    encoded = np.zeros(2 ** p_bits, dtype=np.ubyte)
    parity_bits = np.zeros(p_bits+1)
    data_index = 0
    p_place = 4
    for i in range(3, 2 ** p_bits):
        if i == p_place:
            p_place *= 2
        else:
            data_bit = data[data_index]
            #print(data_bit)
            encoded[i] = data_bit
            data_index += 1
            parity_bits[0] += data_bit


            # Update to allow for variable number of parity bits

            if int(i % 2) == 1:
                parity_bits[1] += data_bit
                #print(i, 1)
            if int((i % 4) / 2) == 1:
                parity_bits[2] += data_bit
                #print(i, 2)
            if int((i % 8) / 4) == 1:
                parity_bits[3] += data_bit
                #print(i, 3)
            if int((i % 16) / 8) == 1:
                parity_bits[4] += data_bit
                #print(i, 4)
            if int((i % 32) / 16) == 1:
                parity_bits[5] += data_bit
                #print(i, 5)

    for i in range(1, p_bits+1):
        if parity_bits[i] % 2 == 1:
            encoded[(2**(i-1))] = 1
            parity_bits[0] += data_bit
    if parity_bits[0] % 2 == 1:
            encoded[0] = 1
    return encoded

P_BITS = 5          # Number of parity bits per packet (exluding 0)
D_BITS = 26         # Number of data bits per packet
PACKET_SIZE = 32    # Number of total bits per packet (P_BITS + D_BITS + 1; 2^P_BITS >= PACKET_SIZE)

samplerate = 44100
FREQ0 = 1000
FREQ1 = 2000
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
    #print(bin(ord(char)))
    # encrypt each character with encryption formula
    c.append((key1 * ord(char) + key2) % 256)

# print encrypted message as 8 bit binary numbers (starting and ending with a null character)

binary += "11000001"
for char in c:
    temp = bin(char)[2:]
    binary += '0' * (8 - len(temp)) + temp
binary += "11000001"

bit_arr = np.fromstring(binary, dtype=np.ubyte) - 48

print("Encrypted message: ", (binary))


binary_arr = get_hamming(bit_arr[:D_BITS], D_BITS, P_BITS)
for i in range(26, len(bit_arr), D_BITS):
    binary_arr = np.append(binary_arr, get_hamming(bit_arr[i:i+D_BITS], D_BITS, P_BITS))
    print("Encrypted message: ", binary_arr)
for i in range(0, len(binary_arr), 1):
    if binary_arr[i] == 0:
        #print('0')
        array = np.append(array, low)
    else:
        #print('1')
        temp = np.full((1, FREQ0), amplitude)
        array = np.append(array, high)
        
array = np.append(space, array)
array = np.append(array, space)

wavfile.write("encrypted.wav", samplerate, array.astype(np.int16))

input("Press <Enter> to play message")

wav_file = "./encrypted.wav"
os.system(f'aplay {wav_file}')


