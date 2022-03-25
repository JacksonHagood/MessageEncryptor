from textwrap import wrap

# affine cipher keys
key1inv = 183
key2 = 193

c = wrap(input("Enter the encrypted message: "), 8)
m = ""

i = 0

for char in c:
    if (char != "11000001"):
        # decrypt each character with decryption formula (ignore null characters)
        m += chr((key1inv * (int(char, 2) - key2)) % 256)

# print message
print("Message: " + m)
