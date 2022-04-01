from pygame import mixer
from time import sleep

mixer.init()

# mixer.music.load("D.mp3")
# mixer.music.set_volume(0.5)
# mixer.music.play()
# sleep(1)
# mixer.music.stop()

# from playsound import playsound

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

for i in range(0, len(binary), 2):
    if binary[i:i+2] == '00':
        print('A')
        mixer.music.load("A.mp3")
        mixer.music.set_volume(0.5)
        mixer.music.play()
        sleep(1)
        mixer.music.stop()
        # SoundPlayer.playTone(200, 1, True, dev)
    elif binary[i:i+2] == '01':
        print('B')
        mixer.music.load("B.mp3")
        mixer.music.set_volume(0.5)
        mixer.music.play()
        sleep(1)
        mixer.music.stop()
        # SoundPlayer.playTone(400, 1, True, dev)
    elif binary[i:i+2] == '10':
        print('C')
        mixer.music.load("C.mp3")
        mixer.music.set_volume(0.5)
        mixer.music.play()
        sleep(1)
        mixer.music.stop()
        # SoundPlayer.playTone(800, 1, True, dev)
    else:
        print('D')
        mixer.music.load("D.mp3")
        mixer.music.set_volume(0.5)
        mixer.music.play()
        sleep(1)
        mixer.music.stop()
        # SoundPlayer.playTone(1000, 1, True, dev)
    # time.sleep(1)

