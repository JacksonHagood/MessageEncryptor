# affine cipher keys
key1 = 7
key2 = 193

m = input("Enter the message: ")
c = []

for char in m:
    # encrypt each character with encryption formula
    c.append((key1 * ord(char) + key2) % 256)

# print encrypted message as 8 bit binary numbers (starting and ending with a null character)
print("Encrypted message: 11000001", end="")
for char in c:
    temp = bin(char)[2:]
    print('0' * (8 - len(temp)) + temp, end="")
print("11000001")
