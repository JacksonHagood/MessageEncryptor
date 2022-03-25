from soundplayer import SoundPlayer
import time

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

dev = 2 # set using aplay -l

for char in binary:
    if char == '0':
        SoundPlayer.playTone(500, 0.9, True, dev)
        print("low")
    else:
        SoundPlayer.playTone(1000, 0.9, True, dev)
        print("high")
    time.sleep(0.1)
