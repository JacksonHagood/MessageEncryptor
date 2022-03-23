# affine cipher keys
key1inv = 183
key2 = 193

c = input("Enter the encrypted message: ").split()
m = ""

for char in c:
    # decrypt each character with decryption formula
    m += chr((key1inv * (int(char) - key2)) % 256)

# print message
print("Message: " + m)
