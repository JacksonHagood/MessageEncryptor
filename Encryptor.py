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

p = SoundPlayer("z.wav", 0)
p.play(0.5)
time.sleep(1)

# for i in range(0, len(binary), 2):
#     if binary[i:i+2] == '00':
#         print('A')
#         SoundPlayer.playTone(200, 1, True, dev)
#     elif binary[i:i+2] == '01':
#         print('B')
#         SoundPlayer.playTone(400, 1, True, dev)
#     elif binary[i:i+2] == '10':
#         print('C')
#         SoundPlayer.playTone(800, 1, True, dev)
#     else:
#         print('D')
#         SoundPlayer.playTone(1000, 1, True, dev)
#     # time.sleep(1)

# for char in binary:
#     if char == '0':
#         SoundPlayer.playTone(500, 0.5, False, dev)
#         print("low")
#     else:
#         SoundPlayer.playTone(1000, 0.5, False, dev)
#         print("high")
#     time.sleep(0.6)
