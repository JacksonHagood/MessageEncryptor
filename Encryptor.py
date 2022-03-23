# affine cipher keys
key1 = 7
key2 = 193

m = input("Enter the message: ")
c = []

for char in m:
    # encrypt each character with encryption formula
    c.append((key1 * ord(char) + key2) % 256)

# print encrypted message
print("Encrypted message: ", end="")
for char in c:
    print(char, end=" ")
print()