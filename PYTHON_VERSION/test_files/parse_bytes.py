byte_array = b'l\x00o\x00h\x00\\\x00X\x00X\x00W\x00V\x00o\x00o\x00p\x00j\x00]\x00Y\x00W\x00Y\x00l\x00n\x00n\x00o\x00i\x00\\\x00[\x00Z\x00\\\x00a\x00k\x00o\x00l\x00f\x00Z\x00Z\x00\\\x00Z\x00]\x00e\x00m\x00k\x00^\x00Z\x00f\x00Z\x00[\x00[\x00`\x00j\x00g\x00a\x00c\x00[\x00Z\x00\\\x00Z\x00_\x00h\x00_\x00Z\x00W\x00Z\x00Y\x00X\x00[\x00]\x00\\\x00'

temps = []

# Iterate over the byte array by stepping through every two bytes

print(len(byte_array))
print()

for i in range(0, len(byte_array), 2):
    # Convert the two bytes into a little-endian short integer
    pixel_value = byte_array[i] | (byte_array[i+1] << 8)
    temps.append(pixel_value)

print()
print(len(temps))