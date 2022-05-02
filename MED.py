# message encryptor and decryptor
# Jackson Hagood, Andrew Imwalle, and Max Smith

# imports
import adafruit_character_lcd.character_lcd as characterlcd
import adafruit_mcp3xxx.mcp3008 as MCP
import board
import busio
import digitalio
import numpy as np
import operator as op
import os
import pyaudio
import RPi.GPIO as GPIO
import scipy.fftpack as fft
import signal
import wave
from adafruit_mcp3xxx.analog_in import AnalogIn
from functools import reduce
from scipy.interpolate import interp1d
from scipy.io import wavfile
from scipy.signal import find_peaks
from time import sleep

# suppress warnings
warnings.filterwarnings("ignore")

# setup for DIP input through mcp3008
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D22)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)

# measurements from mcp3008 for each possible DIP input
chan_vals = [64512, 63288.32, 62241.92, 61121.92, 60181.76, 59050.24, 58018.56, 56895.36, 56050.56, 54929.92, 53889.28, 52775.04, 51841.28, 50720.0, 49713.92, 48598.4, 47981.44, 46864.64, 45843.84, 44739.84, 43781.12, 42673.28, 41668.48, 40576.64, 39689.6, 38590.08, 37569.28, 36505.6, 35536.64, 34457.6, 33456.0, 32377.6, 31500.8, 30418.56, 29394.56, 28333.44, 27346.56, 26280.96, 25267.84, 24200.32, 23240.96, 22187.52, 21178.88, 20136.32, 19142.4, 18104.96, 17082.88, 16058.88, 15290.88, 14229.76, 13208.96, 12176.0, 11182.08, 10144.0, 9144.32, 8120.32, 7116.16, 6090.24, 5079.68, 4078.08, 3070.72, 2046.72, 1037.44, 0]
nums = [i for i in range(64)]

# performs linear interpolation over chan_vals and maps mcp3008 input to an integer value
def get_dip_input():
    lcd.clear()
    lcd.message = "Set keys on DIP"
    #wait 5 seconds for user input, then get and return value
    sleep(5)
    num_interp = interp1d(chan_vals, nums)
    sum = 0
    for i in range(100):
        sum = sum + chan0.value
        sleep(0.001)
    avg = sum / 100
    num = int(np.around(num_interp(avg)))
    print("num: ", num)
    return num
  
# encrypts a single character based on the provided keys
def encrypt_char(char, key1, key2):
    ciphertext = (key1 * ord(char) + key2) % 256
    char = ""
    temp = bin(ciphertext)[2:]
    char += '0' * (8 - len(temp)) + temp
    print(char)
    return char

# button setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(20, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(21, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

# setup LCD
lcd_columns = 16
lcd_rows = 2
lcd_rs = digitalio.DigitalInOut(board.D19)
lcd_en = digitalio.DigitalInOut(board.D26)
lcd_d4 = digitalio.DigitalInOut(board.D18)
lcd_d5 = digitalio.DigitalInOut(board.D23)
lcd_d6 = digitalio.DigitalInOut(board.D24)
lcd_d7 = digitalio.DigitalInOut(board.D25)
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)
lcd.clear()

cont = True # boolean for signal handling

# signal handler for stopping recording
def button_handler(channel):
        print("Stopping...")
        global cont
        cont = False

# setup event handler for button interrupt
GPIO.add_event_detect(21, GPIO.RISING, callback = button_handler)

def encryptor():
    global lcd

    # encode data with Hamming(32, 26) 
    # (this is really (31, 26); the sixth parity bit was included without adding
    # functionality for 2-bit error detection just to round out packet size to an even 4 bytes)
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
                # Determine parity bits
                data_bit = data[data_index]
                encoded[i] = data_bit
                data_index += 1
                parity_bits[0] += data_bit
                
                
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

        # set parity bits in encoded binary
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


    # get dip switch value
    dip = get_dip_input()

    # strip key indices from dip input
    index1 = dip % 2 # first 5 bits
    index2 = int(dip / 2) # last (6th) bit

    # get affine cipher keys
    key1 = 193 if index2 == 1 else 97
    key2 = [177, 10, 186, 162, 46, 197, 21, 133, 109, 137, 115, 90, 65, 145, 216, 154, 196, 53, 19, 152, 220, 28, 108, 198, 234, 16, 50, 143, 117, 12, 48, 239][index1]
    """
    lcd.message = f'{dip} {index2}'
    sleep(3)
    lcd.message = f'Key1={key1} Key2={key2}'
    sleep(5)
    lcd.clear()
    """
    # accept message from user input
    lcd.clear()
    lcd.message = "Enter message"
    m = input("Enter the message: ")
    c = []
    binary = ""

    # encrypt ASCII characters
    for char in m:
        c.append((key1 * ord(char) + key2) % 256)

    binary += encrypt_char('\0', key1, key2) # start with null
    
    # convert message to binary
    for char in c:
        temp = bin(char)[2:]
        binary += '0' * (8 - len(temp)) + temp

    binary += encrypt_char('\0', key1, key2) # end with null

    # get bit array
    bit_arr = np.fromstring(binary, dtype = np.ubyte) - 48

    # get hamming foundation
    binary_arr = get_hamming(bit_arr[: D_BITS], D_BITS, P_BITS)

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

    # wait for button press
    lcd.clear()
    lcd.message = "Press B1\nTo Play"
    
    while True:
        if GPIO.input(16) == GPIO.HIGH:
            break
 
    # play wav file
    lcd.clear()
    lcd.message = "Playing message"
    wav_file = "./output.wav"
    os.system(f'aplay {wav_file}')

    lcd.clear()
    # os.remove(wav_file)

def decryptor():
    global lcd

    # wav file variables
    chunk = 1000
    rate = 44100
    channels = 1
    wav_file = "input.wav"
    form = pyaudio.paInt16
    frames = []

    #get dip switch values
    dip = get_dip_input()

    # wait for keystroke
    lcd.clear()
    lcd.message = "Press B1\nTo Record"
    
    # wait for button press
    while True:
        if GPIO.input(16) == GPIO.HIGH:
            break
    
    # suppress ALSA warnings
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)

    # setup audio listener
    lcd.clear()
    lcd.message = "Loading\nMicrophone..."
    print("Loading Microphone...")
    
    # setup recorder
    p = pyaudio.PyAudio()
    stream = p.open(format = form, channels = channels, rate = rate, input = True, frames_per_buffer = chunk)
    
    # wait for button press
    os.dup2(old_stderr, 2)
    os.close(old_stderr)
    lcd.clear()
    lcd.message = "Recording\n(B3 to stop)"
    print("* recording")

    # read sound signal
    global cont
    cont = True
    while cont:
        data = stream.read(chunk)
        frames.append(data)

    # stop recording (will stop on button interrupt)
    lcd.clear()
    lcd.message = "Done"
    print("* done recording")

    # close reader
    stream.stop_stream()
    stream.close()
    p.terminate()

    # write to wav file
    wf = wave.open(wav_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(form))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    # reading wav file variables
    REL_FREQ = 4
    FREQ0 = 1000 # tone 0
    FREQ1 = 2000 # tone 1
    

    # open wav file
    freq_sample, sig_audio = wavfile.read("./input.wav")

    if sig_audio.ndim > 1:
            sig_audio = sig_audio[:, 0]

    # get duration
    duration = int(freq_sample / (REL_FREQ * 12))

    # list to store binary value over window
    dirty_bin = []

    # iterate through signal to get frequency information
    for i in range(0, len(sig_audio), duration):
        # get y and x
        yf = fft.rfft(sig_audio[i : i + duration])
        xf = fft.rfftfreq(duration, 1 / freq_sample)

        # determine the dominant frequency
        dominant_freq = xf[np.argmax(np.abs(yf))]

        # determine if the frequency is 0 or 1 (or noise)
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

    ciphertext = "" # raw ciphertext bit string

    # Noise removal by averaging determined value over window
    for k in range(0, len(dirty_bin), REL_FREQ):
        if int(round(sum(dirty_bin[k : k + REL_FREQ]) / REL_FREQ, 0)) == -1:
            break
        
        mid_chunk = dirty_bin[int(round(k + (REL_FREQ / 4))):int(round(k + (3 * REL_FREQ / 4)))]

        if len(mid_chunk) == 0:
            break
        
        ciphertext += str(int(round(sum(mid_chunk) / (len(mid_chunk)), 0))) # append to ciphertext

    # convert ciphertext
    ciphertext += ((32 - len(ciphertext)) % 32) * '0'
    ciphertext = np.fromstring(ciphertext, dtype=np.ubyte) - 48

    # initialize variables for hamming decoding
    decoded = ""
    remove = [2 ** i for i in range(5)]
    remove.append(0)

    # iterate through ciphertext to decode hamming
    # this will correct any 1-bit errors that occur within a packet)
    for i in range(0, len(ciphertext), 32):
        bits = [i for i, bit in enumerate(ciphertext[i : i + 32]) if bit]
        if not bits:
            continue
        index = (reduce(op.xor, bits))
        
        ciphertext[i + index] = ciphertext[i + index] ^ 1
        decoded += "".join([",".join(item) for item in np.delete(ciphertext[i : i + 32], remove).astype(str)])
        
    # set ciphertext to the decoded/error-corrected bit string
    ciphertext = decoded

    # strip key indices from dip input
    index1 = dip % 2 # first 5 bits
    index2 = int(dip / 2) # last (6th) bit
    
    # get affine cipher keys
    key1 = 193 if index2 == 1 else 97
    key1inv = 65 if index2 == 1 else 161
    key2 = [177, 10, 186, 162, 46, 197, 21, 133, 109, 137, 115, 90, 65, 145, 216, 154, 196, 53, 19, 152, 220, 28, 108, 198, 234, 16, 50, 143, 117, 12, 48, 239][index1]
    
    # null byte constant is encrypted null character binary string
    NULL_BYTE = encrypt_char('\0', key1, key2)

    # initialize message variable
    m = ""
    print(ciphertext)
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
    lcd.clear()
    
    # setup
    i = 0
    m += " "

    while True:
        # display message, moving to the right
        if GPIO.input(16) == GPIO.HIGH:
            break
        
        lcd.message = m[i:i + 16] + "\n(B1 to exit)"
        
        if len(m) < 18:
            continue
        
        i = (i + 1) % len(m)
        sleep(0.25)

# starting state which allows user selection of mode
while True:
    sleep (0.1)
    lcd.message = "Select Mode\nEnc: B1, Dec: B2"
    
    if GPIO.input(16) == GPIO.HIGH:
        encryptor()
    elif GPIO.input(20) == GPIO.HIGH:
        decryptor()
