from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def encrypt(plaintext, key):
    # Generate a random initialization vector (IV)
    iv = get_random_bytes(AES.block_size)

    # Create an AES cipher object with the provided key and AES.MODE_CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Pad the plaintext to match the block size of AES
    padded_plaintext = pad(plaintext.encode(), AES.block_size)

    # Encrypt the padded plaintext
    ciphertext = cipher.encrypt(padded_plaintext)

    # Return the IV and ciphertext
    return iv + ciphertext

def decrypt(ciphertext, key):
    # Extract the IV from the ciphertext
    iv = ciphertext[:AES.block_size]

    # Create an AES cipher object with the provided key, AES.MODE_CBC mode, and the extracted IV
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the ciphertext
    decrypted_data = cipher.decrypt(ciphertext[AES.block_size:])

    # Unpad the decrypted data
    plaintext = unpad(decrypted_data, AES.block_size)

    # Return the plaintext
    return plaintext.decode()

encrypted_text = encrypt('MTExOTE4NzA4NDMzMTIwMDUyMw.GDgFnv.EBjwX1O8B6eU4WPfAN4mdD6Y4sCBHbGI_MM3Gw', b'\xfc\x93\x17\xdfm\xdc\x81\xe5\xc9\x11\x93\x81\xd0\xe8\x0c\xc1\xcb\x14\x8eU\x1b\xd5\x96\x80%\xb0G\xf7(Z8\xda')
print(encrypted_text)

print(decrypt(b'w\xca\xd5\x90E\xda\xa0\x80\x1f\x99\x1f\xcf0{\xaa\xc762\x12t|\xa1\xaf\x9b\xe8`\nO\x89\x85\xcf#\x07n\xb5\xec\xad\x1a\x9e\x9e\x98\x93\x8d\xf3\xef\xd5\xfd\xc0\x8b\xefA\xf6\x12\x9a\xa3;\x14T\xdc\x17Y"3M\xec\xc1\x8bf\xd8\xd3z\xa4F\xd9\xca\xadQ\x99\xa4\x08\xd9\x93z\x94\xf5MS \x87!\xe7\x0b`\xf2)\xe4', b'\xfc\x93\x17\xdfm\xdc\x81\xe5\xc9\x11\x93\x81\xd0\xe8\x0c\xc1\xcb\x14\x8eU\x1b\xd5\x96\x80%\xb0G\xf7(Z8\xda'))
