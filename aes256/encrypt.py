from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Generate a random salt
salt = b'\x8f\x88\xe7\xfdG\xd4f\xf6\x12.\x8e\x94\x96\xb4\xe0'
iv = b'\x87\xb9\xa1\xe8\x1e\xc6\xd1\xff\xf7L6\x0cV\x03\x07\xfb'

password = "YourPassword" 
kdf = PBKDF2HMAC(
    algorithm=SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)
key = kdf.derive(password.encode())

padder = padding.PKCS7(128).padder()
plaintext = b"This is the text to be encrypted. sadsad"  # Replace with your own plaintext
padded_plaintext = padder.update(plaintext) + padder.finalize()

cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
encryptor = cipher.encryptor()

ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

with open("encrypted.59", "wb") as file:
    file.write(ciphertext)
