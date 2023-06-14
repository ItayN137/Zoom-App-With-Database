import rsa
from Crypto.Random import get_random_bytes
import hashlib
from Crypto.Cipher import AES
from  Crypto.Util.Padding import pad, unpad

def generate_rsa_keys(client_socket):
    public_key, private_key = rsa.newkeys(1024)

    with open("public.pem", "wb") as f:
        f.write(public_key.save_pkcs1("PEM"))

    with open("private.pem", "wb") as f:
        f.write(private_key.save_pkcs1("PEM"))

    #client_socket.send(public_key)
    return public_key, private_key


def encrypt_rsa(data, public_key):
    return rsa.encrypt(data.encode(), public_key)


def decrypt_rsa(data, private_key):
    dectypted_data = rsa.decrypt(data, private_key)
    return dectypted_data.decode()


def create_AES_key_iv():
    key = get_random_bytes(16)
    iv = get_random_bytes(16)

    return key, iv


def generate_cipher(key, iv):
    return AES.new(key, AES.MODE_CBC, iv)


def encrypt_AES(plaintext, cipher):
    return cipher.encrypt(pad(plaintext, AES.block_size))


def decrypt_AES(ciphertext, key, iv):
    cipher = generate_cipher(key, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext


def encrypt_MD5(data):
    return hashlib.md5(data).hexdigest()


message = b"hi my name is itay"
print(message)
print(len(message))


aes_key, aes_iv = create_AES_key_iv()
aes_cipher = generate_cipher(aes_key, aes_iv)
aes_e = encrypt_AES(message, aes_cipher)
print(aes_e)
aes_d = decrypt_AES(aes_e, aes_key, aes_iv)
print(aes_d.decode())




