import numpy as np

# wavfile constants
SAMPLE_RATE = 44100
REL_FREQ = 4 # number of reads per bit recorded
FREQ0 = 1000 # tone 0
FREQ1 = 2000 # tone 1

AMPLITUDE = np.iinfo(np.int16).max
T = np.linspace(0., (1 / 12), int(SAMPLE_RATE / 12))
HIGH_SIGNAL = AMPLITUDE = np.iinfo(np.int16).max * np.sin(2. * np.pi * FREQ1 * T)
LOW_SIGNAL = AMPLITUDE = np.iinfo(np.int16).max * np.sin(2. * np.pi * FREQ0 * T)
HIGH_SIGNAL[-100 : -1] = 0
LOW_SIGNAL[-100 : -1] = 0
READ_SIZE = 1000 #


# encryption/decryption constants
KEYS = [177, 10, 186, 162, 46, 197, 21, 133, 109, 137, 115, 90, 65, 145, 216, 154, 196, 53, 19, 152, 220, 28, 108, 198, 234, 16, 50, 143, 117, 12, 48, 239]

def encrypt_char(char, key1, key2):
    return (key1 * ord(char) + key2) % 256

def encrypt_msg(msg, key1, key2):
    encrypted_msg = ""
    for c in msg:
        encrypted_msg += encrypt_char(c, key1, key2)

def to_bin(msg):
    ciphertext = ""
    for char in msg:
        temp = bin(char)[2:]
        ciphertext += '0' * (8 - len(temp)) + temp
    return ciphertext